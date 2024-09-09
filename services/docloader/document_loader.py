import os
import requests
import shutil
from time import sleep
import logging
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_postgres import PGVector
from langchain_postgres.vectorstores import PGVector
import warnings
warnings.filterwarnings("ignore")

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG to capture all logs, INFO for general information
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("download.log"),  # Logs to a file
        logging.StreamHandler()  # Logs to the console
    ]
)


def clean_text(text):
    return text.replace('\x00', '')


def download_pdf(url, folder_path):
    try:
        # Ensure the folder exists
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            logging.info(f"Created folder: {folder_path}")

        # Extract the file name from the URL
        file_name = url.split('/')[-1]
        file_path = os.path.join(folder_path, file_name)

        # Send HTTP GET request to download the file
        response = requests.get(url, stream=True)

        # Check if the request was successful
        if response.status_code == 200:
            # Open a local file in binary write mode
            with open(file_path, 'wb') as file:
                # Write the content to the file in chunks
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            logging.info(f"File downloaded successfully: {file_path}")
        else:
            logging.error(f"Failed to download the file. Status code: {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
    except IOError as e:
        logging.error(f"File operation failed: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    


def load_pdf(file_path):
    logging.info(f"Loading file: {file_path}")
    loader = PyMuPDFLoader(file_path)
    docs = loader.load()
    logging.info(f"{len(docs)} documents loaded from file")
    logging.info(f"Splitting loaded documents")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1000,
        chunk_overlap = 150
        )
    splits = text_splitter.split_documents(docs)
    logging.info(f"{len(splits)} splits from documents")
    model_embedding = HuggingFaceEmbeddings(model_name='multi-qa-mpnet-base-dot-v1')
    connection = f"postgresql+psycopg://vector_user:{os.environ['PG_VECTOR_PWD']}@pgvector:5432/vector_db"
    collection_name = "udlbook"

    vector_store = PGVector(
        embeddings=model_embedding,
        collection_name=collection_name,
        connection=connection,
        use_jsonb=True,
    )
    
    batch_size = 50
    # Iterate through splits in batches of 50
    for i in range(0, len(splits), batch_size):
        batch = splits[i:i + batch_size]
        logging.info(f"Processing batch {i}")
        for doc in batch:
            doc.page_content = clean_text(doc.page_content)
            # If there are any other text fields, clean them as well
            if "metadata" in doc:
                for key in doc.metadata:
                    if isinstance(doc.metadata[key], str):
                        doc.metadata[key] = clean_text(doc.metadata[key])
        vector_store.add_documents(batch)
    logging.info(f"Document loading finished.")
    

def clear_folder(folder_path):
    try:
        # Check if the folder exists
        if os.path.exists(folder_path):
            # Iterate through all the items in the folder
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                # Check if it's a file or symlink and delete it
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.unlink(item_path)
                    logging.info(f"Deleted file: {item_path}")
                # Check if it's a directory and delete it recursively
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                    logging.info(f"Deleted directory: {item_path}")
            logging.info(f"All contents of the folder '{folder_path}' have been cleared.")
        else:
            logging.warning(f"The folder '{folder_path}' does not exist.")
    
    except OSError as e:
        logging.error(f"Error while clearing folder: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    download_pdf('https://github.com/udlbook/udlbook/releases/download/v.4.0.4/UnderstandingDeepLearning_08_28_24_C.pdf', './downloads')
    load_pdf("./downloads/UnderstandingDeepLearning_08_28_24_C.pdf")
    clear_folder('./downloads')
