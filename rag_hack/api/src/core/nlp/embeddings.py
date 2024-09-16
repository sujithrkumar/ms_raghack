from pathlib import Path
from langchain_openai import AzureOpenAIEmbeddings
import torch
from transformers import CLIPProcessor, CLIPModel
import base64
from PIL import Image
from io import BytesIO
import logging
from utils.custom_logging import setup_logging
# from config import EMBED_CONF


setup_logging()
logger = logging.getLogger("project_logger")


class EmbeddingGenerator:
    def __init__(self, EMBED_CONF) -> None:
        self.text_embedder = AzureOpenAIEmbeddings(
            model="rag-hack-ada",
            azure_endpoint=EMBED_CONF["AZURE_OPENAI_ENDPOINT"],
            api_key=EMBED_CONF["AZURE_OPENAI_API_KEY"],
            openai_api_version=EMBED_CONF["AZURE_OPENAI_API_VERSION"]
        )
        self.image_embed_model = CLIPModel.from_pretrained(
            EMBED_CONF["IMAGE_EMBED_MODEL"])
        self.image_embed_model_processor = CLIPProcessor.from_pretrained(
            EMBED_CONF["IMAGE_EMBED_MODEL"])

    def get_text_embedding(self, text):
        return self.text_embedder.embed_query(text)

    def get_documents_embeddings(self, docs):
        return self.text_embedder.embed_documents(docs)

    def base64_to_image(self, base64_str):
        image_data = base64.b64decode(base64_str)
        image = Image.open(BytesIO(image_data))
        return image

    def frames_to_embeddings(self, videoFrames):
        embeddings_list = []
        for base64_frame in videoFrames:
            image = self.base64_to_image(base64_frame)
            inputs = self.image_embed_model_processor(
                images=image, return_tensors="pt")
            with torch.no_grad():
                image_embeddings = self.image_embed_model.get_image_features(
                    **inputs)
            embeddings_list.append(image_embeddings)

        return embeddings_list

    def get_image_embedding(self, image: Path):
        image = Image.open(str(image))
        inputs = self.image_embed_model_processor(
            images=image, return_tensors="pt")
        with torch.no_grad():
            image_embeddings = self.image_embed_model.get_image_features(
                **inputs)
        return image_embeddings.cpu().detach().numpy().squeeze().tolist()

    def get_image_embedding_from_content(self, image_content: Image.Image):
        inputs = self.image_embed_model_processor(
            images=image_content, return_tensors="pt")
        with torch.no_grad():
            image_embeddings = self.image_embed_model.get_image_features(
                **inputs)
        return image_embeddings.cpu().detach().numpy().squeeze().tolist()
