from langchain_text_splitters import RecursiveCharacterTextSplitter

def get_splitter(language_ext: str):
    # tune chunk size based on file type
    return RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\nclass ", "\ndef ", "\n\n", "\n", " ", ""]
    )

def chunk_file(file: dict) -> list[dict]:
    path = file["path"]
    content = file["content"]
    ext = "." + path.split(".")[-1] if "." in path else ""

    splitter = get_splitter(ext)
    raw_chunks = splitter.split_text(content)

    chunks = []
    for i, chunk_text in enumerate(raw_chunks):
        chunks.append({
            "chunk_id": f"{path}::chunk_{i}",
            "file_path": path,
            "language": ext.lstrip("."),
            "index": i,
            "text": chunk_text
        })

    return chunks

def chunk_all_files(files: list[dict]) -> list[dict]:
    all_chunks = []
    for file in files:
        file_chunks = chunk_file(file)
        all_chunks.extend(file_chunks)
        print(f"  chunked: {file['path']} → {len(file_chunks)} chunks")
    return all_chunks