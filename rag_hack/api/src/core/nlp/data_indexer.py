import json
import logging
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SearchIndex, SimpleField, SearchFieldDataType
from azure.core.credentials import AzureKeyCredential

from azure.search.documents import SearchClient, SearchIndexingBufferedSender
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    ExhaustiveKnnAlgorithmConfiguration,
    ExhaustiveKnnParameters,
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    SearchIndex,
    SearchField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    HnswParameters,
    SemanticSearch,
    VectorSearch,
    VectorSearchAlgorithmKind,
    VectorSearchProfile,
    SearchIndex,
    SemanticConfiguration,
    SemanticPrioritizedFields,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    VectorSearch,
    ExhaustiveKnnParameters,
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    SearchIndex,
    SearchField,
    SemanticConfiguration,
    SemanticField,
    VectorSearch,
    HnswParameters,
    VectorSearch,
    VectorSearchAlgorithmKind,
    VectorSearchAlgorithmMetric,
    VectorSearchProfile,
)
from azure.search.documents.models import VectorizedQuery
import requests

from utils.custom_logging import setup_logging

setup_logging()
logger = logging.getLogger("project_logger")


class DataIndexer:
    def __init__(self, INDEX_CONF) -> None:
        self.end_point = INDEX_CONF["end_point"]
        self.api_key = INDEX_CONF["api_key"]
        self.index_client = SearchIndexClient(
            endpoint=self.end_point, credential=AzureKeyCredential(self.api_key))
        self.vector_search = VectorSearch(
            algorithms=[
                HnswAlgorithmConfiguration(
                    name="myHnsw",
                    kind=VectorSearchAlgorithmKind.HNSW,
                    parameters=HnswParameters(
                        m=4,
                        ef_construction=400,
                        ef_search=500,
                        metric=VectorSearchAlgorithmMetric.COSINE
                    )
                ),
                ExhaustiveKnnAlgorithmConfiguration(
                    name="myExhaustiveKnn",
                    kind=VectorSearchAlgorithmKind.EXHAUSTIVE_KNN,
                    parameters=ExhaustiveKnnParameters(
                        metric=VectorSearchAlgorithmMetric.COSINE
                    )
                )
            ],
            profiles=[
                VectorSearchProfile(
                    name="myHnswProfile",
                    algorithm_configuration_name="myHnsw",
                ),
                VectorSearchProfile(
                    name="myExhaustiveKnnProfile",
                    algorithm_configuration_name="myExhaustiveKnn",
                )
            ]
        )

    def create_text_vector_index(self, text_index_name: str, delete_index_if_found=False):

        text_fields = [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SimpleField(name="transcripts",
                        type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="keyframes_description",
                        type=SearchFieldDataType.String),
            SearchField(name="transcripts_embedding", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                        searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
            SimpleField(name="chunk_number", type=SearchFieldDataType.Int32),
            SimpleField(name="keyframe_paths", type=SearchFieldDataType.Collection(
                SearchFieldDataType.String)),
            SimpleField(name="keyframe_blob_paths", type=SearchFieldDataType.Collection(
                SearchFieldDataType.String)),
            SimpleField(name="video_name", type=SearchFieldDataType.String),
            SimpleField(name="video_path", type=SearchFieldDataType.String),
            SimpleField(name="start_time", type=SearchFieldDataType.String),
            SimpleField(name="end_time", type=SearchFieldDataType.String),

        ]

        text_index = SearchIndex(
            name=text_index_name, fields=text_fields, vector_search=self.vector_search)

        if delete_index_if_found:
            self.index_client.delete_index(text_index)

        text_result = self.index_client.create_or_update_index(text_index)
        logger.info(f' {text_result.name} created')
        return text_result

    def create_image_vector_index(self, image_index_name: str, delete_index_if_found=False):

        image_fields = [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SimpleField(name="transcripts",
                        type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="keyframes_description",
                        type=SearchFieldDataType.String),
            SearchField(name="keyframe_embedding", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                        searchable=True, vector_search_dimensions=512, vector_search_profile_name="myHnswProfile"),
            SimpleField(name="chunk_number",
                        type=SearchFieldDataType.Int32),
            SimpleField(name="keyframe_path", type=SearchFieldDataType.String),
            SimpleField(name="keyframe_paths", type=SearchFieldDataType.Collection(
                SearchFieldDataType.String)),
            SimpleField(name="keyframe_blob_paths", type=SearchFieldDataType.Collection(
                SearchFieldDataType.String)),
            SimpleField(name="video_name", type=SearchFieldDataType.String),
            SimpleField(name="video_path", type=SearchFieldDataType.String),
            SimpleField(name="start_time", type=SearchFieldDataType.String),
            SimpleField(name="end_time", type=SearchFieldDataType.String),
        ]

        image_index = SearchIndex(
            name=image_index_name, fields=image_fields, vector_search=self.vector_search)

        if delete_index_if_found:
            self.index_client.delete_index(image_index)

        image_result = self.index_client.create_or_update_index(image_index)
        logger.info(f' {image_result.name} created')
        return image_result

    def upload_text_documents(self, index_name: str, text_chunks: list):
        text_search_client = SearchClient(
            endpoint=self.end_point, index_name=index_name, credential=AzureKeyCredential(self.api_key))
        text_search_client.upload_documents(documents=text_chunks)

    def upload_image_documents(self, index_name: str, images: list):
        image_search_client = SearchClient(
            endpoint=self.end_point, index_name=index_name, credential=AzureKeyCredential(self.api_key))
        image_search_client.upload_documents(documents=images)

    def get_text_index_count(self, index_name: str):
        text_search_client = SearchClient(
            endpoint=self.end_point, index_name=index_name, credential=AzureKeyCredential(self.api_key))
        text_count = text_search_client.get_document_count()
        logger.info(f'Text index has {text_count} documents.')
        return text_count

    def get_image_index_count(self, index_name: str):
        image_search_client = SearchClient(
            endpoint=self.end_point, index_name=index_name, credential=AzureKeyCredential(self.api_key))
        image_count = image_search_client.get_document_count()
        logger.info(f'Image index has {image_count} documents.')
        return image_count

    def search_vector_with_api(self, index_name: str, vector, vector_field, k=5, weight=0.5):
        url = f"{self.end_point}/indexes/{index_name}/docs/search?api-version=2024-07-01"

        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }

        payload = {
            "count": True,
            "select": "*",
            "vectorQueries": [
                {
                    "kind": "vector",
                    "vector": vector,
                    "exhaustive": True,
                    "fields": vector_field,
                    "weight": weight,
                    "k": k
                }
            ]
        }
        response = requests.post(url, headers=headers,
                                 data=json.dumps(payload))

        if response.status_code == 200:
            return response.json()  # Return the JSON response if the request was successful
        else:
            raise Exception(f"Error: {response.status_code}, {response.text}")

    def search_vector(self, index_name: str, vector, vector_field, k=5, weight=0.5, top=5):
        search_client = SearchClient(
            endpoint=self.end_point, index_name=index_name, credential=AzureKeyCredential(self.api_key))
        vector_query = VectorizedQuery(
            vector=vector, k_nearest_neighbors=3, fields=vector_field, exhaustive=True)
        results = search_client.search(
            search_text="", vector_queries=[vector_query], top=top)
        return results
