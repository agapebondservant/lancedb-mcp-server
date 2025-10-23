import os
import lancedb

def unique_documents(documents):
    """
    Given a list of documents, returns a filtered list of unique documents
    based on their page content.

    :param documents:
    :return: unique_docs
    """
    unique_docs = []
    seen_page_contents = set()
    for doc in documents:
        if doc.page_content not in seen_page_contents:
            unique_docs.append(doc)
            seen_page_contents.add(doc.page_content)
    return unique_docs

def format_as_text_and_link(document):
    text = document.page_content
    source = ""
    if 'source' in document.metadata:
        source = f"\n\nSource: {document.metadata['source']}"
    return f"{text}{source}"

def get_lancedb_connection():
    """
    Using the environment variable LANCEDB_URI,
    sets up a connection to the LanceDB database.
    Supports S3-compatible storage and local storage endpoints.
    :return: LanceDB connection
    """
    lancedb_uri = os.environ.get("LANCEDB_URI", "~/lancedb")

    # S3-compatible endpoint
    if "s3" in lancedb_uri:
        storage_options = {
            "endpoint_url": os.getenv('AWS_S3_ENDPOINT'),
            "aws_access_key_id": os.getenv('AWS_ACCESS_KEY_ID'),
            "aws_secret_access_key": os.getenv('AWS_SECRET_ACCESS_KEY'),
            "s3_force_path_style": os.getenv('S3_FORCE_PATH_STYLE'),
            "allow_http": os.getenv('S3_ALLOW_HTTP'),
        }
        return lancedb.connect(lancedb_uri, storage_options=storage_options)

    # Local endpoint
    else:
        return lancedb.connect(lancedb_uri)
