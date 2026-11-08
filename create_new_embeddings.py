import json
import argparse
import os
from pydoc import text
from loader import load_txt
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
    documents = []

    files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith('.txt')]
    filenames = [filepath.split('/')[-1] for filepath in files]
    texts = [load_txt(filepath) for filepath in files]
    print(f"{len(texts)} Files Loaded Successfully.")

    print(files)
    print(filenames)
    with open("patterns.json", 'r') as file:
        patterns = json.load(file)
    for i, name in enumerate(filenames):
        chunked_articles = chunk_by_article(texts[i], patterns[name][0], minimum_chunk_size, maximum_chunk_size, chunk_overlap)
        merged_chunks = chunk_merged_articles(chunked_articles, minimum_chunk_size, maximum_chunk_size, chunk_overlap)
        chunks_with_headings = prepend_headings(merged_chunks, patterns[name][1])
        chunk_documents = [Document(page_content=doc, metadata={"source": name}) for doc in chunks_with_headings] 
        documents += chunk_documents

    print(f"{len(documents)} Chunks Chunked Successfully.")
    embed_documents(documents)
    print("Documents Embedded Successfully.")

if __name__ == "__main__":
    main()