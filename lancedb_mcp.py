import os
import lancedb
from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import LanceDB
from mcp.server.fastmcp import FastMCP
from typing import List, Optional
from langchain_openai import ChatOpenAI
import lancedb_mcp_utils as utils


TABLE_NAME =  os.environ.get("TABLE_NAME", "vectorstore")
EMBEDDING_FUNCTION = "sentence-transformers"
EMBEDDING_MODEL_NAME = os.environ.get("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
QA_MODEL_NAME = os.environ.get("QA_MODEL_NAME", "openai/gpt-oss-20b")
DB_NAME = os.environ.get("DB_NAME", "lancedb")
SERVICE_NAME = os.environ.get("SERVICE_NAME", "lancedb")

embedding_model = SentenceTransformerEmbeddings(
    model_name=EMBEDDING_MODEL_NAME,
    model_kwargs={"trust_remote_code":True}
)

qa_model = ChatOpenAI(
    model=QA_MODEL_NAME,
    temperature=0.1,
)

db = utils.get_lancedb_connection()

dbstore = LanceDB(
    mode="append",
    embedding=embedding_model,
    connection=db,
)

mcp = FastMCP(SERVICE_NAME)

@mcp.tool()
def run_query(query: str, top_k: int = 10):
    """
    Queries the LanceDB using the provided prompt and return the top k results.

    Args:

        query (str): The prompt input.
        top_k (int): The number of results to return. Defaults to 10.

    Returns:

        List[Schema]: A list of prompt results.
    """
    retriever = dbstore.as_retriever(search_kwargs={"k": top_k})
    results = retriever.invoke(query)
    results = utils.unique_documents(results)
    # results = [f"{utils.format_as_text_and_link(r)}" for r in results]
    return results

if __name__ == "__main__":
    mcp.run(
        transport="http",
        port=8080,
        host="0.0.0.0",
    )
