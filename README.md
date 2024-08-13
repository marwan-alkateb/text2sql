---

## LangChain: Chat with SQL Database

### Project Overview

This project provides an interactive web application built with Streamlit that allows users to interact with SQL databases using natural language queries. Leveraging the LangChain framework, the application translates user queries into SQL commands, executes them, and displays the results. The application supports both SQLite and MySQL databases, enabling flexible database management and query execution.

### Key Features

- **Natural Language to SQL Conversion:** Users can input natural language questions, which the system translates into SQL queries using LangChain’s language models.
- **Database Support:** Choose between a local SQLite database (`student.db`) or connect to a remote MySQL database by providing connection details.
- **Interactive SQL Querying:** Users can approve or abort the execution of the generated SQL queries, ensuring control over database interactions.
- **Dynamic Table Exploration:** The app dynamically fetches and displays the schema and sample data from available tables, helping users understand the database structure.
- **User-Friendly Interface:** A sidebar allows for easy input of database connection details, SQL commands, and API keys, making the setup process straightforward.

### How It Works

1. **Database Selection:** Users choose between using a local SQLite database or connecting to a MySQL database. Connection details for MySQL are input through the sidebar.
2. **API Key Input:** Users must provide a GRoq API key for the language model to function, ensuring secure and authenticated usage.
3. **Query Handling:** Users type their natural language queries into the chat interface. The system generates the corresponding SQL queries using predefined templates and LangChain models.
4. **Query Execution:** After the query is generated, users can review and approve it before execution. The results are formatted and displayed in a user-friendly format.
5. **Table Information Display:** The sidebar provides insights into the available tables in the connected database, displaying schema details and sample data.

### Technologies Used

- **Streamlit:** For building the interactive web interface.
- **LangChain:** To manage the natural language processing and query generation.
- **SQLite/MySQL:** As the supported database systems.
- **SQLAlchemy:** To handle database connections and query executions.
- **Pandas:** For displaying query results in tabular form.

### Getting Started

To run the application:

1. Install the required dependencies by running `pip install -r requirements.txt`.
2. Start the Streamlit app with `streamlit run app.py`.
3. Provide the necessary API key and database connection details in the sidebar.
4. Begin interacting with your SQL database using natural language queries.

This project is ideal for users looking to simplify their database management by enabling conversational interactions with SQL databases.

### Streamlit App

Access the Streamlit app here: [https://text2sql-application.streamlit.app/](https://text2sql-application.streamlit.app/)

--- 
