import argparse
import os
from loader import load_txt, add_chunk_ids
from embed import embed_documents
from chunker import *
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

    minimum_chunk_size = 500
    maximum_chunk_size = 1000
    chunk_overlap = 150
    outlier_chunk_size = 100

    files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith('.txt')]
    filenames = [filepath.split('/')[-1] for filepath in files]
    texts = [load_txt(filepath) for filepath in files]
    print(f"{len(texts)} Files Loaded Successfully.")

    print("Files: ", filenames)
    documents = prepare_documents(texts, filenames, minimum_chunk_size, maximum_chunk_size, chunk_overlap, outlier_chunk_size)
    documents = add_chunk_ids(documents)
    print(f"{len(documents)} Chunks Chunked Successfully.")
    embed_documents(documents)
    print("Documents Embedded Successfully.")

if __name__ == "__main__":
    main()