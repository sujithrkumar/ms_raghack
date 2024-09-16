from pathlib import Path
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.models import VectorizedQuery
import logging
from scripts.transcripts import get_video_chunks
from core.nlp.embeddings import EmbeddingGenerator
from core.nlp.data_indexer import DataIndexer
from config import INDEX_CONF, EMBED_CONF

from utils.custom_logging import setup_logging


setup_logging()
logger = logging.getLogger("project_logger")

embedding_generator = EmbeddingGenerator(EMBED_CONF=EMBED_CONF)

def process_video(video_file_path: Path):
    logger.info(f"Getting video chunks...")
    chunked_transcripts_with_keyframes = get_video_chunks(
        input_file=video_file_path)

    chunked_transcripts_with_keyframes_embeddings = []
    keyframes_with_embeddings = []

    for id, chunk in enumerate(chunked_transcripts_with_keyframes):
        chunked_transcripts_with_keyframes_embeddings.append(
            {**chunk, **{"id": video_file_path.stem + "_" + str(id), "transcripts_embedding": embedding_generator.get_text_embedding(chunk["transcripts"] + chunk["keyframes_description"])}})

        if chunk["keyframe_paths"]:
            keyframes_with_embeddings.extend(
                [{**chunk, **{"id": video_file_path.stem + "_" + str(id)+str(n), "keyframe_embedding": embedding_generator.get_image_embedding(Path(keyframe_path)), "keyframe_path": str(keyframe_path)}} for n, keyframe_path in enumerate(chunk["keyframe_paths"]) if keyframe_path])

    data_indexer = DataIndexer(INDEX_CONF=INDEX_CONF)
    data_indexer.upload_text_documents(
        index_name=INDEX_CONF["transcripts_index_name"],
        text_chunks=chunked_transcripts_with_keyframes_embeddings
    )
    data_indexer.upload_image_documents(
        index_name=INDEX_CONF["keyframe_index_name"],
        images=keyframes_with_embeddings
    )
    logger.info(data_indexer.get_text_index_count(
        index_name=INDEX_CONF["transcripts_index_name"]))
    logger.info(data_indexer.get_image_index_count(
        index_name=INDEX_CONF["keyframe_index_name"]))
