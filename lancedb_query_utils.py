
import traceback

import subprocess

import lancedb

import pyarrow as pa

import pyarrow.parquet as pq

import os

from minio import Minio

from minio.error import S3Error

def dowwnload_index(target_dir: str):
    """
    Downloads the GraphRAG index from MinIO to a local directory.

    Args:
        target_dir (str): The local directory to which the index should be downloaded.
    """
    print(f"Downloading GraphRAG index from MinIO tp {target_dir}...")

    bucket_name = os.getenv("AWS_S3_BUCKET")

    db_name = os.getenv("DB_NAME")

    try:

        client = Minio(
            os.getenv("AWS_S3_ENDPOINT").removeprefix("https://").removeprefix(
                "http://"),

            access_key=os.getenv("AWS_ACCESS_KEY_ID"),

            secret_key=os.getenv("AWS_SECRET_ACCESS_KEY"),

            secure=False
        )

        objects = client.list_objects(bucket_name, prefix=db_name,
                                      recursive=True)

        for obj in objects:
            relative_path = os.path.relpath(obj.object_name, db_name)

            local_file_path = os.path.join(target_dir, relative_path)

            local_subdir = os.path.dirname(local_file_path)

            os.makedirs(local_subdir, exist_ok=True)

            client.fget_object(bucket_name, obj.object_name, local_file_path)

    except Exception as e:

        print(f"An error occurred while downloading GraphRAG index: {e}")

        traceback.print_exc()


def initialize_index():
    """
    Initializes a local version of the configured LanceDB database by
    downloading the GraphRAG index from MinIO to a local directory and
    setting up a local LanceDB connection to the downloaded index.
    """

    target_dir = os.getenv("LANCEDB_DOWNLOAD_DIR")

    try:

        os.makedirs(f"{target_dir}/output", exist_ok=True)

        dowwnload_index(target_dir)

        local_db = lancedb.connect(target_dir)

        db = lancedb.connect(os.getenv("LANCEDB_URI"),

             storage_options={
                 "endpoint_url": os.getenv("AWS_S3_ENDPOINT"),

                 "aws_access_key_id": os.getenv(
                     "AWS_ACCESS_KEY_ID"),

                 "aws_secret_access_key": os.getenv(
                     "AWS_SECRET_ACCESS_KEY"),

                 "s3_force_path_style": "true",

                 "allow_http": "true",
             }
        )

        for table_name in db.table_names():
            print(f"Copying table: {table_name}")

            table = db.open_table(table_name)

            data_to_copy = table.to_pandas()

            local_db.create_table(table_name, data=data_to_copy,
                                  mode="overwrite")

            if isinstance(data_to_copy, pa.Table):

                pq.write_table(data_to_copy,
                               f"{target_dir}/output/{table_name}.parquet")

            else:
                data_to_copy.to_parquet(
                    f"{target_dir}/output/{table_name}.parquet")

        print("DB index initialization complete.")

    except Exception as e:

        print(f"An error occurred while initializing GraphRAG index: {e}")

        traceback.print_exc()


def query_index(prompt: str):
    try:
        result = subprocess.run(["graphrag",
                                 "query",
                                 "--root",
                                 os.getenv("LANCEDB_DOWNLOAD_DIR"),
                                 "--config",
                                 os.getenv('LANCEDB_CONFIG'),
                                 "--method",
                                 "global",
                                 "--query",
                                 prompt],
                                capture_output=True, text=True, check=True)

        if result.stderr:
            raise Exception(
                f"Error processing GraphRAG command: {result.stderr}")

        output = result.stdout

        return output

    except Exception as e:

        print(f"Error querying GraphRAG DB: {e}")

        traceback.print_exc()