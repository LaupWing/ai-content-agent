from google.cloud import storage

def get_txt_file(path: str, bucket_name: str) -> str:
    """
    Reads a .txt file from Firebase Storage (Google Cloud Storage).

    Args:
        path: The path inside the bucket (without .txt at the end)
        bucket_name: Your Firebase project's default bucket (e.g. "my-project.appspot.com")

    Returns:
        The text content of the file as a string.
    """
    client = storage.Client()  # uses Application Default Credentials (ADC)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(f"{path}.txt")

    if not blob.exists():
        raise FileNotFoundError(f"File {path}.txt not found in bucket {bucket_name}")

    return blob.download_as_text()

bucket = "dronestart-production.appspot.com"
path = "handboeken/1fdG53b4RyP25wVOGkYCYUZjTam2/5BGNS1dqjXrTxoviRtya/1_1"

text = get_txt_file(path, bucket)
print(text)