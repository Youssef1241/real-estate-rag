import argparse
import os
from pydoc import text
from loader import load_txt
from embed import embed_documents
from chunker import chunk_documents
from dotenv import load_dotenv

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="Embed documents from a given directory.")
    parser.add_argument(
        "--input-dir", 
        type=str, 
        required=True, 
        help="Path to the input directory containing .txt files to embed."
    )
    args = parser.parse_args()
    input_dir = args.input_dir

    files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith('.txt')]
    filenames = [filepath.split('/')[-1] for filepath in files]
    texts = [load_txt(filepath) for filepath in files] 
    print("Files Loaded Successfully.")
    documents = chunk_documents(texts, filenames, chunk_size=750, chunk_overlap=50)
    print("Documents Chunked Successfully.")
    embed_documents(documents)
    print("Documents Embedded Successfully.")

if __name__ == "__main__":
    main()