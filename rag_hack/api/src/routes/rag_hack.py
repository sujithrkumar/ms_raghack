# pip install fastapi uvicorn transformers torch azure-search-documents

import json
import logging
from fastapi import File, UploadFile
from fastapi.responses import JSONResponse
import uvicorn
from io import BytesIO
from PIL import Image

from config import INDEX_CONF, EMBED_CONF
from core.nlp.embeddings import EmbeddingGenerator
from core.nlp.data_indexer import DataIndexer
from core.nlp.qa import answer_from_chunks, convert_answer_to_html, answer_to_image_query
from fastapi import APIRouter, Query
# from langchain.vectorstores import AzureSearch
from fastapi.responses import JSONResponse
from schemas.error import NotFoundErrorResponseModel, InternalServerErrorResponseModel
from utils.custom_logging import setup_logging

from scripts.create_graph import get_answer, get_embed_model,get_llm, get_kg

setup_logging()
logger = logging.getLogger("project_logger")

router = APIRouter(
    tags=["raghack_apis"],
    responses={500: {
        "model": InternalServerErrorResponseModel
    }})

embedding_generator = EmbeddingGenerator(EMBED_CONF=EMBED_CONF)
data_indexer = DataIndexer(INDEX_CONF=INDEX_CONF)


@router.post("/search-image/")
async def search_image(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(BytesIO(contents))  # .convert("RGB")

    query_embedding = embedding_generator.get_image_embedding_from_content(
        image_content=image)

    # Perform vector search in Azure AI Search
    try:
        results = data_indexer.search_vector(
            vector=query_embedding,
            index_name=INDEX_CONF["keyframe_index_name"],
            vector_field="keyframe_embedding"
        )

        search_results = [result for result in results]
        logger.info(f"Generating answer from retrieved results...")
        answer = answer_to_image_query(
            query_image_content=contents, chunks=search_results)
        if answer:
            format_instructions = """Convert the answer in HTML format while highlighting important points in bold or using colors.
            You can also include bullet points or conclusion in answer if necessary."""
            html_answer = convert_answer_to_html(
                question="This was an image query.", answer=answer['answer'], format_instructions=format_instructions)
            logger.info(
                f"Returning answer along with other results. Answer: {answer['answer']}")
            return {
                "answer": html_answer["formatted_answer"],
                "answer_references": answer['answer_references'],
                "search_results": search_results
            }
        else:
            logger.info(f"Couldn't find relevant answer")
            return {
                "answer": "Couldn't find a relevant answer in the videos",
                "answer_references": [],
                "search_results": search_results
            }
    except Exception as e:
        logger.exception(e)
        return JSONResponse(status_code=500, content=str(e))


@router.post("/search-text")
async def search_text(query: str, use_graph: bool = True):
    try:
        logger.info(f"Search query received: {query}")
        logger.info(f"Generating embedding...")
        embedding = embedding_generator.get_text_embedding(query)
        logger.info(f"Searching the vector store...")
        results = data_indexer.search_vector(vector=embedding,
                                             index_name=INDEX_CONF["transcripts_index_name"],
                                             vector_field="transcripts_embedding")

        search_results = [result for result in results]
        logger.info(f"Generating answer from retrieved results...")
        if use_graph:
            logger.info(f"Using graph to answer the query...")
            llm = get_llm()
            kg = get_kg(reset=False)
            embed_model = get_embed_model()

            output_answer = get_answer(question=query, llm=llm, kg=kg,
                                       embed_model=embed_model, top_k=10, return_context=False)
            answer = {
                "answer": output_answer,
                "answer_references": []
            }
        else:
            logger.info(f"Using native RAG to answer the query...")
            answer = answer_from_chunks(question=query, chunks=search_results)

        if answer:
            format_instructions = """Convert the answer in HTML format while highlighting important points in bold or using colors.
            You can also include bullet points or conclusion in answer if necessary."""
            html_answer = convert_answer_to_html(
                question=query, answer=answer['answer'], format_instructions=format_instructions)
            logger.info(
                f"Returning answer along with other results. Answer: {answer['answer']}")
            return {
                "answer": html_answer["formatted_answer"],
                "answer_references": answer['answer_references'],
                "search_results": search_results
            }
        else:
            logger.info(f"Couldn't find relevant answer")
            return {
                "answer": "Couldn't find a relevant answer in the videos",
                "answer_references": [],
                "search_results": search_results
            }
    except Exception as e:
        logger.exception(e)
        return JSONResponse(status_code=500, content=str(e))


@router.post("/search-graph")
async def search_graph(query: str):
    try:
        
        logger.info(f"Search query received: {query}")
        question = query
        
        llm = get_llm()
        kg = get_kg(reset=False)
        embed_model = get_embed_model()

        output_answer = get_answer(question, llm=llm, kg=kg, 
                                    embed_model=embed_model, top_k=10,return_context=False)

        format_instructions = """Convert the answer in HTML format while highlighting important points in bold or using colors.
            You can also include bullet points or conclusion in answer if necessary."""

        answer = {
            "answer": output_answer
        }
        html_answer = convert_answer_to_html(
                 question=query, answer=answer['answer'], format_instructions=format_instructions)

        if answer:
            logger.info(
                f"Returning answer along with other results. Answer: {answer['answer']}")
            return {
                "answer": html_answer["formatted_answer"]
            }
        else:
            logger.info(f"Couldn't find relevant answer")
            return {
                "answer": "Couldn't find a relevant answer in the videos",
            }
    except Exception as e:
        logger.exception(e)
        return JSONResponse(status_code=500, content=str(e))
