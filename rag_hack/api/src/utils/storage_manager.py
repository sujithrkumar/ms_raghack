from datetime import datetime, timedelta
import os
from pathlib import Path
import uuid
import logging
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, generate_blob_sas
from utils.custom_logging import setup_logging


setup_logging()
logger = logging.getLogger("project_logger")


class AzureBLOB:
    def __init__(self, BLOB_CONF) -> None:
        connect_str = BLOB_CONF['connection_string']
        # Create the BlobServiceClient object
        self.blob_service_client = BlobServiceClient.from_connection_string(
            connect_str)
        self.account_key = BLOB_CONF['account_key']

    def upload(self, container_name: str, blob_name: str, file_path: Path):
        try:
            # Create a blob client using the local file name as the name for the blob
            blob_client = self.blob_service_client.get_blob_client(
                container=container_name, blob=blob_name)

            logger.info(f"Uploading to Azure Storage as blob: {file_path}")

            # Upload the created file
            if not blob_client.exists():
                with open(file=file_path, mode="rb") as data:
                    blob_client.upload_blob(data)

            # Generate the blob client for the uploaded file
            container_client = self.blob_service_client.get_container_client(
                container=container_name)
            blob_client = container_client.get_blob_client(blob_name)

            # Generate a public URL with a SAS token (optional: set expiry time for the URL)
            expiry_time = datetime.now() + timedelta(days=7)  # URL will be valid for 7 days
            sas_token = generate_blob_sas(
                account_name=str(self.blob_service_client.account_name),
                account_key=self.account_key,
                container_name=container_name,
                blob_name=blob_name,
                permission="r",  # Read permission
                expiry=expiry_time
            )

            # Construct the full URL
            blob_url = f"{blob_client.url}?{sas_token}"
            return blob_url
        except Exception as ex:
            logger.exception(ex)
            return None

    def download(self, container_name: str, blob_name: str, download_path: Path):
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=container_name, blob=blob_name)

            container_client = self.blob_service_client.get_container_client(
                container=container_name)
            logger.info(f"Downloading blob to:{download_path}")

            with open(file=download_path, mode="wb") as download_file:
                download_file.write(container_client.download_blob(
                    blob_client.blob_name).readall())
        except Exception as ex:
            logger.exception(ex)
            raise IOError("Couldn't download blob")
