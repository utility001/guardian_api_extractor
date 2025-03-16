import awswrangler as wr
import logging

logging.basicConfig(
    level=logging.INFO,
    format="{asctime} - {levelname} - {message}",
    style="{", datefmt="%Y-%m-%d %H:%M:%S")

# Make sure you have configured aws and you have required permission
LOCAL_FILEPATH = "./extracted_files/mydata.csv"
S3_OBJECT_PATH = "s3://lettuceleaf/mydata.csv"

# Upload the file
try:
    wr.s3.upload(local_file=LOCAL_FILEPATH, path=S3_OBJECT_PATH)
    logging.info(f"Succesfully moved local_file::{LOCAL_FILEPATH}"
                 f"to s3 bucket::{S3_OBJECT_PATH}")
except Exception as e:
    logging.error(e)
    raise