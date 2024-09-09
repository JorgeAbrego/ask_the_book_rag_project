# Ask The Book "Understanding Deep Learning"

![Ask the book](images/ask_the_book.png)

## Table of Contents
- [Project Overview](#project-overview)
- [Dataset](#dataset)
- [Technologies](#technologies)
- [Preparation](#preparation)
- [Running the Application](#running-the-application)
- [Using the Application](#using-the-application)

## Project Overview

In the fast-evolving world of AI and deep learning, staying up to date with reliable and well-organized information is essential. This project builds a **Retrieval-Augmented Generation (RAG)** model using the book *"Understanding Deep Learning"* as its knowledge base. 

The goal of the project is to allow users to ask questions about deep learning concepts and get concise, relevant answers pulled directly from a trusted source. This can be especially useful for students, researchers, or practitioners who want quick access to accurate information without sifting through large amounts of material.

## Dataset

The knowledge base for this project is the book *"Understanding Deep Learning"*. This book provides a comprehensive overview of deep learning concepts, techniques, and applications. You can explore the book [here](https://udlbook.github.io/udlbook/).

## Technologies

This project integrates multiple powerful tools and frameworks to create a robust RAG model:

- **Python**: The core programming language used for model development and integration.
- **Docker**: Containerizes the application to ensure consistent development and deployment environments.
- **LangChain**: Powers the interaction between the language model and external data sources.
- **Postgres**: Stores the text embeddings in an efficient, searchable format.
- **pgvector**: An extension for Postgres that enables vector similarity search, critical for retrieving relevant data.
- **Groq**: Provides high-speed inference acceleration for the language model.
- **Streamlit**: Serves as the user interface for interacting with the RAG model.
- **Grafana**: Monitors and visualizes performance metrics, ensuring the model operates efficiently.

## Preparation

1. Clone the repository to your local machine:
   ```bash
   git clone <repository_url>
   cd <repository_folder>
   ```

2. Set up the Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Obtain a Groq API Key by signing up at [Groq](https://groq.com). 

4. Obtain a Hugging Face API Token by signing up at [Hugging Face](https://huggingface.co/).

5.  Create a .env file in the project directory. Use the example.env file as a guide to understand which environment variables need to be set. Update the values according to your environment and API keys from previous steps.

    ```bash
    cp example.env .env
    # Then edit the .env file with your specific configurations
    ```

## Running the Application

> **_NOTE:_** Keep images names and tags as is defined, so you won't need to update anything else in the project.

1. Build the Docker images for the application:
   ```bash
   docker build -t docloader_task:latest -f services/docloader/Dockerfile services/docloader
   ```

2. Run the application using Docker Compose:
   ```bash
   docker-compose up -d --build
   ```

## Using the Application

Once the application is up and running, you can access it by opening your web browser and navigating to:

```
http://localhost:8501
```

This will bring up the Streamlit-based user interface, where you can enter questions about deep learning. The RAG model will retrieve relevant information from the *"Understanding Deep Learning"* book and generate helpful responses.

![Streamlit App](images/app_page.png)

You can also check the status of the book's load to vector database in Airflow by navigating to:

```
http://localhost:8080
```

Using the credentials configured in the .env file, you will enter the airflow interface and be able to see the status of the ingest dag:

![Book Ingest](<images/book ingest.png>)

If you want to review the databases and how the information is being stored, you can access both services (Postgres and PGVector) through PgAdmin by navigating to

```
http://localhost:8888
```

Using the credentials from the .env file, you will log into PgAdmin and after configuring access to the services, you will be able to see their status:

![PgAdmin](images/pgadmin_client.png)

For more information on how to create a connection, you can enter [here](https://www.pgadmin.org/docs/pgadmin4/development/connecting.html).