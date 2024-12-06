import os
import re
import time
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from langchain.schema.document import Document
import chromadb
from chromadb import EmbeddingFunction
from langchain.vectorstores.chroma import Chroma
from typing import List, Tuple
import logging
import openai
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

    
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Output folder for saved plots
OUTPUT_FOLDER = '../data/output_plots'
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Preprocessing function
def preprocess_data(data):
    data = re.sub(r'\s+', ' ', data)
    data = re.sub(r'\n+', '\n', data)
    data = re.sub(r'(===){4,}', '', data)
    data = re.sub(r'(---){4,}', '', data)
    data = data.replace('|', '')
    return data

# Function to save processed data
def save_processed_data(processed_data, original_path, root_path):
    new_path = original_path.replace(root_path, root_path + '-processed')
    os.makedirs(os.path.dirname(new_path), exist_ok=True)
    # Save the processed data with UTF-8 encoding
    try:
        with open(new_path, 'w', encoding='utf-8') as f:
            f.write(processed_data)
        #print(f"Successfully processed and saved: {new_path}")
    except (IOError, UnicodeEncodeError) as e:
        print(f"Error saving processed data for file {new_path}: {e}")

# Read file with fallback encoding
def read_file_with_fallback(file_name, encodings=['utf-8', 'ISO-8859-1']):
    for encoding in encodings:
        try:
            with open(file_name, 'r', encoding=encoding) as f:
                return f.read().replace('\x00', '')
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError(f"Could not decode file: {file_name}")

# Count words in a string
def count_words(text: str) -> int:
    return len(text.split())

# Preprocess files in the directory
path = Path('../data/crawled')
file_paths = list(path.rglob('*'))
total_files = len([fp for fp in file_paths if fp.is_file()])  # Count total files
processed_files = 0  # Initialize counter

for file_path in file_paths:
    if file_path.is_file():
        try:
            data = read_file_with_fallback(str(file_path))
            if data:
                processed_data = preprocess_data(data)
                save_processed_data(processed_data, str(file_path), str(path))
                processed_files += 1
                
                # Display progress after every 100 files or when finished
                if processed_files % 100 == 0 or processed_files == total_files:
                    remaining_files = total_files - processed_files
                    print(f"Progress: {processed_files}/{total_files} files processed, {remaining_files} remaining.")
        except (IOError, UnicodeDecodeError) as e:
            print(f"Error processing file {file_path}: {e}")

# Analyze processed documents
documents = []
word_counts = []
character_counts = []
path = Path('../data/crawled-processed')

for file_path in path.rglob('*'):
    if file_path.is_file():
        try:
            data = file_path.read_text().replace('\x00', '')
            if not data:
                continue

            metadata = {"file": str(file_path.relative_to(path).with_suffix(''))}
            doc = Document(page_content=data, metadata=metadata)
            documents.append(doc)
            word_counts.append(count_words(data))
            character_counts.append(len(data))

        except IOError as e:
            print(f"Error reading file {file_path}: {e}")

# Plotting word count distribution
def plot_word_distribution(word_counts):
    bins = [0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1200, 1400, 1600, 1800, 2000, 2500]
    bin_labels = ['0-100', '101-200', '201-300', '301-400', '401-500', '501-600', '601-700', '701-800', '801-900', '901-1000', '1001-1200', '1201-1400', '1401-1600', '1601-1800', '1801-2000', '2001-2500']
    counts, _ = np.histogram(word_counts, bins)

    plt.figure(figsize=(10, 6))
    plt.bar(bin_labels, counts, color='blue')
    plt.xlabel('Word Count Ranges')
    plt.ylabel('Number of Files')
    plt.title('Word Count Distribution')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_FOLDER}/word_count_distribution.png")
    plt.close()

plot_word_distribution(word_counts)

# Plotting character count distribution
def plot_character_distribution(character_counts):
    bins = [0, 2000, 4000, 5000, 6000, 7000, 8000, 10000, 12000, 200000]
    bin_labels = ['0-2k', '2k-4k', '4k-5k', '5k-6k', '6k-7k', '7k-8k', '8k-10k', '10k-12k', '12k-200k']
    counts, _ = np.histogram(character_counts, bins)

    plt.figure(figsize=(10, 6))
    plt.bar(bin_labels, counts, color='blue')
    plt.xlabel('Character Count Ranges')
    plt.ylabel('Number of Files')
    plt.title('Character Count Distribution')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_FOLDER}/character_count_distribution.png")
    plt.close()

plot_character_distribution(character_counts)

class CharacterTextSplitter:
    def _init_(self, chunk_size, chunk_overlap):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text):
        chunks = []
        i = 0
        while i < len(text):
            if i + self.chunk_size + self.chunk_overlap < len(text):
                chunks.append(text[i:i + self.chunk_size + self.chunk_overlap])
                i += self.chunk_size
            else:
                chunks.append(text[i:])
                break
        return chunks

# Initialize splitter
text_splitter = CharacterTextSplitter(
    chunk_size=5599,chunk_overlap=400
)

# Plotting word count distribution after document splitting
def plot_word_distribution_after_split(word_counts):
    bins = [0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1200, 1400, 1600, 1800, 2000, 2500]
    bin_labels = ['0-100', '101-200', '201-300', '301-400', '401-500', '501-600', '601-700', '701-800', '801-900', '901-1000', '1001-1200', '1201-1400', '1401-1600', '1601-1800', '1801-2000', '2001-2500']

    counts, _ = np.histogram(word_counts, bins)

    plt.figure(figsize=(10, 6))
    plt.bar(bin_labels, counts, color='blue')

    for i, v in enumerate(counts):
        plt.text(i, v + 0.1, str(v), ha='center', va='bottom', fontsize=12)

    plt.xlabel('Word Count Ranges')
    plt.ylabel('Number of Document Chunks')
    plt.title('Word Count Distribution in Document Chunks (After Splitting)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_FOLDER}/word_count_distribution_after_split.png")
    plt.close()

# Plotting character count distribution after document splitting
def plot_character_distribution_after_split(character_counts):
    bins = [0, 2000, 4000, 5000, 6000, 7000, 8000, 10000, 12000, 20000]
    bin_labels = ['0-2k', '2k-4k', '4k-5k', '5k-6k', '6k-7k', '7k-8k', '8k-10k', '10k-12k', '12k-20k']

    counts, _ = np.histogram(character_counts, bins)

    plt.figure(figsize=(10, 6))
    plt.bar(bin_labels, counts, color='blue')

    for i, v in enumerate(counts):
        plt.text(i, v + 0.1, str(v), ha='center', va='bottom', fontsize=12)

    plt.xlabel('Character Count Ranges')
    plt.ylabel('Number of Document Chunks')
    plt.title('Character Count Distribution in Document Chunks (After Splitting)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_FOLDER}/character_count_distribution_after_split.png")
    plt.close()




start_time = time.time()

path = '../data/crawled-processed'
documents = []
document_token_counts: List[Tuple[str, int]] = []
word_counts_processed = []
character_counts_processed = []

for r, _, files in os.walk(path):
    for file in files:
        file_name = os.path.join(r, file)

        try:
            with open(file_name, "r") as f:
                data = f.read().replace('\x00', '')

            if not data:
                continue

            # Using text splitter
            chunks = text_splitter.split_text(data)
            for i, chunk in enumerate(chunks):
                doc = Document(page_content=chunk, metadata={"link": file_name[20:-3]})
                documents.append(doc)

                # Get word count and character count for the chunk
                word_count = count_words(chunk)
                character_count = sum(1 for char in chunk)

                # Append the counts to the respective lists
                word_counts_processed.append(word_count)
                character_counts_processed.append(character_count)

        except IOError as e:
            print(f"Error reading file {file_name}: {e}")


print(f"Total documents: {len(documents)}")

end_time = time.time()
elapsed_time = end_time - start_time

print(f"Time taken: {elapsed_time:.2f} seconds")

# Example usage after processing the documents
plot_word_distribution_after_split(word_counts_processed)
plot_character_distribution_after_split(character_counts_processed)


# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(_name_)

# Initialize database connection
try:
    DB_PATH = os.environ.get("DB_PATH", os.path.abspath(os.path.join(os.getcwd(), "../data/database/chromadb")))
    COLLECTION_NAME = os.environ.get("COLLECTION_NAME", "Hsrw_database")
    persistent_client = chromadb.PersistentClient(path=DB_PATH)
    collection = persistent_client.get_or_create_collection(COLLECTION_NAME)
    logger.info(f"Connected to database at {DB_PATH}")
except Exception as e:
    logger.error(f"Database connection error: {e}")

# Embedding function
openai.api_key = OPENAI_API_KEY

class MyEmbeddingFunction(EmbeddingFunction):
    def _init_(self):
        self.model = "text-embedding-3-small"


    def embed_documents(self, texts):
        embeddings = []
        for text in texts:
            for attempt in range(10):  # Retry up to 3 times
                try:
                    response = openai.Embedding.create(model=self.model, input=text, timeout=1200)
                    embeddings.append(response['data'][0]['embedding'])
                    break
                except openai.error.Timeout as e:
                    logger.error(f"Timeout error on attempt {attempt + 1}: {e}")
                    time.sleep(5)  # Wait before retrying
        return embeddings
    
    
embedding_dimension = 1536



db = Chroma(
    client=persistent_client,
    collection_name=COLLECTION_NAME,
    embedding_function=MyEmbeddingFunction(),
    collection_metadata={"hnsw:space": "cosine", "dimension": embedding_dimension}
)





# Initialize counters
total_documents = len(documents)
saved_documents = 0

# Save documents to Chroma database with progress tracking
for i, doc in enumerate(documents, start=1):
    db.add_documents([Document(page_content=doc.page_content, metadata=doc.metadata)])
    saved_documents += 1

    # Display progress after every 100 documents
    if saved_documents % 100 == 0 or saved_documents == total_documents:
        remaining_documents = total_documents - saved_documents
        print(f"Progress: {saved_documents}/{total_documents} saved, {remaining_documents} remaining.")

logger.info("Document storage complete.")