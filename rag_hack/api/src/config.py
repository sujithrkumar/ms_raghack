import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PORT = 8405

STT_CONFIG = {
    'speech_key': os.environ.get('SPEECH_KEY'),
    'speech_region': os.environ.get('SPEECH_REGION'),
    'audio_output_dir': Path("/home/sujithkumar/git/rag_hack/api/src/data/audio"),
    'transcripts_dir': Path("/home/sujithkumar/git/rag_hack/api/src/data/transcripts"),
    'use_cache': True,
    'speech_recognition_language': "en-US",
}

CHUNKING_CONFIG = {
    "chunk_length": 8,
    "stride": 1
}


VIDEO_INSIGHTS_CONFIG = {
    "video_clips_dir": "video_clips",
    "keyframes_dir": Path("data/keyframes"),
    "keyframe_cutoff_score": "0.4"
}

BLOB_CONF = {
    "connection_string": os.environ.get("AZURE_STORAGE_CONNECTION_STRING"),
    "keyframe_container": "keyframes",
    "video_container": "videos",
    "doc_container": "docs",
    "account_key": os.environ.get("BLOB_ACCOUNT_KEY")
}

LLM_CONF = {
    "api_key": os.environ.get("AZURE_OPENAI_KEY"),
    "end_point": os.environ.get("AZURE_OPENAI_ENDPOINT")
}

INDEX_CONF = {
    "api_key": os.getenv("AZURE_SEARCH_API_KEY"),
    "end_point": os.getenv("AZURE_SEARCH_ENDPOINT"),
    "transcripts_index_name": "text-embeddings-index",
    "keyframe_index_name": "image-embeddings-index"
}

EMBED_CONF = {
    "AZURE_OPENAI_ENDPOINT": os.getenv("AZURE_OPENAI_ENDPOINT_EMBED"),
    "AZURE_OPENAI_API_KEY": os.getenv("AZURE_OPENAI_API_KEY_EMBED"),
    "AZURE_OPENAI_API_VERSION": os.getenv("AZURE_OPENAI_API_VERSION_EMBED"),
    "IMAGE_EMBED_MODEL": "openai/clip-vit-base-patch16"
}

KG_CHUNKING_CONFIG = {
    "chunk_length": 8,
    "stride": 0
}

NEO4J_CONF = {
    "NEO4J_URI": os.getenv("NEO4J_URI"),
    "NEO4J_USERNAME": os.getenv("NEO4J_USERNAME"),
    "NEO4J_PASSWORD": os.getenv("NEO4J_PASSWORD"),
    "AURA_INSTANCEID": os.getenv("AURA_INSTANCEID"),
    "AURA_INSTANCENAME": os.getenv("AURA_INSTANCENAME")
}

PRIVATE_OPEN_AI_CONF = {
    "PRIVATE_OPENAI_API_KEY":os.getenv("PRIVATE_OPENAI_API_KEY")
}
