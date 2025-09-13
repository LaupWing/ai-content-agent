# build_manual_index.py
import json, math, re
from typing import List, Dict
from google.cloud import storage
from vertexai.preview import language_models  # text-embedding-004
import vertexai

PROJECT_ID = "dronestart-production"
LOCATION   = "europe-west4"
BUCKET     = "dronestart-production.appspot.com"
BLOB_PATH  = "handboeken/NG56Njq7iTWBUAqsxkIipa3J8R32/S2ySsDZHfcMP32IceFBh/6_2.txt"  # put your real path here

vertexai.init(project=PROJECT_ID, location=LOCATION)

def load_manual_from_gcs(bucket: str, path: str) -> str:
    from google.cloud import storage
    client = storage.Client()
    blob = client.bucket(bucket).blob(path)
    return blob.download_as_text()

def chunk_text(t: str, chunk_chars=1500, overlap=150):
    t = re.sub(r"\s+", " ", t).strip()
    chunks = []
    i = 0
    while i < len(t):
        chunks.append(t[i:i+chunk_chars])
        i += (chunk_chars - overlap)
    return chunks

def embed_texts(texts: List[str]) -> List[List[float]]:
    model = language_models.TextEmbeddingModel.from_pretrained("text-embedding-004")
    # Batch to stay under limits
    vecs = []
    B = 100
    for i in range(0, len(texts), B):
        batch = texts[i:i+B]
        res = model.get_embeddings(batch)
        vecs.extend([e.values for e in res])
    return vecs

def main():
    manual = load_manual_from_gcs(BUCKET, BLOB_PATH)
    chunks = chunk_text(manual, 1500, 150)
    vectors = embed_texts(chunks)
    index = [{"text": c, "vec": v} for c, v in zip(chunks, vectors)]
    with open("manual_index.json", "w", encoding="utf-8") as f:
        json.dump(index, f)
    print(f"Saved {len(index)} chunks to manual_index.json")

if __name__ == "__main__":
    main()
