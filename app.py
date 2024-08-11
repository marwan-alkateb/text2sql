import streamlit as st
from pathlib import Path
from httpcore import RemoteProtocolError
from langchain.chains.sql_database.query import create_sql_query_chain
from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine, text
import sqlite3
from langchain_groq import ChatGroq
import pandas as pd
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough

# Streamlit Page Configuration
st.set_page_config(page_title="LangChain: Chat with SQL DB", page_icon="🦜")

# Database Options
LOCALDB = "USE_LOCALDB"
MYSQL = "USE_MYSQL"

radio_opt = ["Use SQLLite 3 Database- Student.db", "Connect to your MySQL Database"]
selected_opt = st.sidebar.radio(label="Choose the DB which you want to chat", options=radio_opt)

mysql_host = mysql_user = mysql_password = mysql_db = None

if radio_opt.index(selected_opt) == 1:
    db_uri = MYSQL
    mysql_host = st.sidebar.text_input("MySQL Host")
    mysql_user = st.sidebar.text_input("MySQL User")
    mysql_password = st.sidebar.text_input("MySQL Password", type="password")
    mysql_db = st.sidebar.text_input("MySQL Database")
else:
    db_uri = LOCALDB

# Input for API Key
api_key = st.sidebar.text_input(label="GRoq API Key", type="password")
if not api_key:
    st.info("Please add the GRoq API key. If you do not have one, then go get one! I'm waiting!")
    st.stop()

# LLM Setup
llm = ChatGroq(temperature=0, groq_api_key=api_key, model_name="llama-3.1-70b-versatile", streaming=True)
llm2 = ChatGroq(temperature=0, groq_api_key=api_key, model_name="llama3-70b-8192", streaming=True)


# SQL Database Setup
def configure_db(db_uri, mysql_host=None, mysql_user=None, mysql_password=None, mysql_db=None):
    if db_uri == LOCALDB:
        dbfilepath = (Path.cwd() / "student.db").absolute()
        # Remove read-only flag
        creator = lambda: sqlite3.connect(f"file:{dbfilepath}?mode=rw&check_same_thread=False", uri=True)
        return SQLDatabase(create_engine("sqlite:///", creator=creator))
    elif db_uri == MYSQL:
        if not (mysql_host and mysql_user and mysql_password and mysql_db):
            st.error("Please provide all MySQL connection details.")
            st.stop()
        return SQLDatabase(
            create_engine(f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}")
        )


db = configure_db(db_uri, mysql_host, mysql_user, mysql_password, mysql_db)


# Execute query and return rows and columns
def execute_query(db, query):
    try:
        with db._engine.connect() as connection:
            result = connection.execute(text(query))
            if result.returns_rows:
                rows = result.fetchall()
                columns = result.keys()
                return rows, columns, "Query executed successfully."
            connection.commit()
            return None, None, "Statement executed successfully, but no data returned."
    except Exception as e:
        return None, None, f"An error occurred: {e}"


# SQL input field in the sidebar
sql_input = st.sidebar.text_input(label="SQL Input", type="default")
if sql_input:
    rows, columns, message = execute_query(db, sql_input)
    st.sidebar.write(message)  # Provide feedback to the user
    if rows and columns:
        st.sidebar.write(f"Query Result:")
        st.sidebar.write(pd.DataFrame(rows, columns=columns))


def get_table_info(db_engine):
    with db_engine.connect() as connection:
        result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
        tables = [row[0] for row in result]

        context = ""
        for table in tables:
            schema_result = connection.execute(text(f"SELECT sql FROM sqlite_master WHERE name='{table}';"))
            schema = schema_result.fetchone()[0]
            sample_result = connection.execute(text(f'SELECT * FROM "{table}" LIMIT 1;'))
            rows = sample_result.fetchall()
            columns = sample_result.keys()

            context += f"{schema}\n\n/*\n3 rows from {table} table:\n"
            context += "\t".join(columns) + "\n"
            for row in rows:
                context += "\t".join(map(str, row)) + "\n"
            context += "*/\n\n\n"

        return context


def extract_sql_query(response):
    sql_query_start = response.find("SQLQuery:") + len("SQLQuery:")
    sql_query_end = response.find("SQLResult:")
    if sql_query_end == -1:
        sql_query_end = len(response)
    if sql_query_start != -1 and sql_query_start < sql_query_end:
        return response[sql_query_start:sql_query_end].strip().replace('`', '"').replace('""', '"')
    return ""


def handle_user_query(question):
    table_info = get_table_info(db._engine)
    prompt = PromptTemplate.from_template(
        """
        Given an input question, follow these steps:
        If Question is a syntactically correct sql statement then assign it to be the SQLQuery.
        Else the Question is a request to write 1 syntactically correct {dialect} query.

        Format:
        Question: "Question here"
        SQLQuery: "SQL Query to run"
        SQLResult: "Result of the SQLQuery"
        Answer: "your answer here"
        Question: {input}
        Available tables and columns with examples: {table_info}

        Instructions:
        Correct any table or column name errors.
        Include all columns if query does inserting to avoid errors.
        Assign a unique ID to new rows by setting it to the highest existing ID + 1.
        End each SQL statement with a semicolon (;)
        Table and column names can vary in case and may contain special characters.
        Avoid backslashes in queries.
        Example: Use INSERT INTO "table_name" ... instead of INSERT INTO \"table_name\" ...
        Define a primary key if creating a table.
        Select the top {top_k} rows if the query is selective.
        Check for object existence to avoid errors if the query is destructive.
        Surround table names with double quotes.
        
        Examples:
        Question: Calculate the median of horses ages.
        SQLQuery: SELECT AVG(age) AS median_age FROM (
            SELECT age
            FROM horses
            ORDER BY age
            LIMIT 2 - (SELECT COUNT(*) FROM horses) % 2
            OFFSET (SELECT (COUNT(*) - 1) / 2 FROM horses)
        );
        """

    )

    query_chain = create_sql_query_chain(llm, db, prompt=prompt)
    try:
        with st.spinner("Generating SQL query, please wait..."):
            response = query_chain.invoke({
                "question": question,
                "table_info": table_info,
                "dialect": "sqlite",
                "input": question,
                "top_k": 5
            })
    except RemoteProtocolError:
        st.error("There was a problem processing your request. The connection was lost unexpectedly. Please try again.")
        return None, "An error occurred, please try again."

    sql_query = extract_sql_query(response)
    st.code(sql_query, language="sql")

    st.session_state['sql_query'] = sql_query
    st.session_state['current_question'] = question


def run_query_and_format_response(sql_query, question):
    try:
        result = db.run(sql_query)
        if not result:
            status = f"Query: `{sql_query}` executed successfully, but no results were returned."
        else:
            status = "ok"
    except Exception as e:
        return sql_query, f"Error during query execution: {e}. Check the link for valuable info why this happened!"

    if status == "ok":
        answer_prompt = PromptTemplate.from_template(
            """Format the Answer elegantly & concisely corresponding to the question for better readability using lists, tables, etc.
            Do not answer based on your knowledge but based on what is written here as result!
            Question: {question}
            SQL Query: {query}
            SQL Result: {result}
            Answer: """
        )

        answer_chain = (RunnablePassthrough()
                        .assign(query=lambda inputs: inputs["query"])
                        .assign(result=lambda inputs: inputs["result"]) | answer_prompt | llm2 | StrOutputParser())

        final_input = {"question": question,
                       "query": sql_query,
                       "result": result}

        formatted_response = answer_chain.invoke(final_input)

        return sql_query, formatted_response

    return sql_query, status


# Streamlit Interface for User Query
st.title("LangChain: Chat with SQL DB")
st.write("Ask questions about your SQL database.")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Always define the placeholder before usage
placeholder = st.empty()

for message in st.session_state["messages"]:
    if message["role"] == "user":
        st.chat_message("user").write(message["content"])
    else:
        st.chat_message("assistant").write(message["content"], unsafe_allow_html=True)

user_query = st.chat_input("Ask anything from the database")
if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)

    handle_user_query(user_query)

    # Re-define the placeholder to ensure it's in the correct place
    placeholder = st.empty()

if 'sql_query' in st.session_state and st.session_state.get('user_approved') is None:
    with placeholder.container():
        st.write("Do you approve this SQL query to be executed?")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Yes", key="yes_button"):
                st.session_state['user_approved'] = True

        with col2:
            if st.button("No", key="no_button"):
                st.session_state['user_approved'] = False

if st.session_state.get('user_approved') is not None:
    placeholder.empty()  # Clear the buttons once a decision is made

    if st.session_state['user_approved']:
        st.write("Executing query...")
        sql_query, formatted_response = run_query_and_format_response(st.session_state['sql_query'],
                                                                      st.session_state['current_question'])
        st.session_state.messages.append({"role": "assistant", "content": formatted_response})
        st.chat_message("assistant").write(formatted_response, unsafe_allow_html=True)
    else:
        st.write("Execution aborted based on user's request.")
        st.session_state.messages.append({"role": "assistant", "content": "Execution aborted based on user's request."})

    # Clear the session state
    del st.session_state['sql_query']
    del st.session_state['user_approved']
    del st.session_state['current_question']


def display_tables_in_sidebar(db):
    with st.sidebar, st.spinner("Fetching table names..."):
        result = db._engine.connect().execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
        tables_names = [row[0] for row in result]
        st.subheader("Available Tables")
        for table in tables_names:
            query = f'SELECT * FROM "{table}"'
            rows, columns, _ = execute_query(db, query)
            st.write(f"**Table: {table}**")
            st.write(pd.DataFrame(rows, columns=columns))


display_tables_in_sidebar(db)
