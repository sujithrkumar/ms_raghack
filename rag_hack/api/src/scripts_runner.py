import logging
import os
import json
import base64

from pathlib import Path

from scripts.create_graph import get_answer, get_embed_model, get_kg, get_llm, get_summary_node, get_summary_of_summaries, graph_stats, push_video_to_graph_db
from core.nlp.data_indexer import DataIndexer
from core.nlp.azure_openai import AzureOpenAILLM
from core.speech_processor.azure_stt import AzureSTT
from core.nlp.qa import convert_answer_to_html
from utils.custom_logging import setup_logging
from scripts.transcripts import get_video_chunks, get_video_chunks_for_kg
from scripts.data_processor import process_video
from config import STT_CONFIG, BLOB_CONF, INDEX_CONF, LLM_CONF
from utils.storage_manager import AzureBLOB

setup_logging()
logger = logging.getLogger("project_logger")


def test_transcription():
    try:
        azure_stt = AzureSTT(STT_CONFIG=STT_CONFIG)
        input_file = Path(
            '/home/sujithkumar/git/rag_hack/api/src/data/test_audio.mp4')
        transcripts_df = azure_stt.recognize_from_file(input_file=input_file)
        print(transcripts_df)
    except Exception as err:
        logger.exception(err)


def test_video_indexing():
    input_file = Path(
        '/home/sujithkumar/git/rag_hack/api/src/data/top_5_best_phones_under_20K.mp4')
    process_video(video_file_path=input_file)
    # blob_manager = AzureBLOB(BLOB_CONF=BLOB_CONF)
    # blob_url = blob_manager.upload(container_name="videos",
    #                                blob_name=input_file.name, file_path=input_file)
    # print(blob_url)


def test_llm():
    IMAGE_PATH = "/home/sujithkumar/git/rag_hack/api/src/data/keyframes/test_audio/001-0_00_03-800000.png"
    encoded_image = base64.b64encode(
        open(IMAGE_PATH, 'rb').read()).decode('ascii')
    llm = AzureOpenAILLM(LLM_CONF=LLM_CONF)
    messages = [
        {
            "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": "You are an AI assistant that helps people find information."
                        }
                    ]
        },
        {
            "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encoded_image}"
                            }
                        },
                        {
                            "type": "text",
                            "text": "how many laptops are there?"
                        }
                    ]
        }
    ]
    llm_response = llm.get_llm_response(messages=messages)
    print(llm_response)


def create_indexes():
    data_indexer = DataIndexer(INDEX_CONF)
    text_result = data_indexer.create_text_vector_index(
        INDEX_CONF["transcripts_index_name"], delete_index_if_found=True)
    image_result = data_indexer.create_image_vector_index(
        INDEX_CONF["keyframe_index_name"], delete_index_if_found=True)


def clear_graph():
    kg = get_kg(reset=True)


def test_kg():
    input_file = Path(
        '/home/sujithkumar/git/rag_hack/api/src/data/top_5_best_phones_under_20K.mp4')
    logger.info(f"Getting video chunks...")
    chunked_transcripts_with_keyframes = get_video_chunks_for_kg(
        input_file=input_file)

    video_transcripts = [chunk['transcripts']
                         for chunk in chunked_transcripts_with_keyframes]
    video_transcripts = '\n'.join(video_transcripts)

    # with open("sample_transcript.txt") as f:
    #     video_data = f.read()
    video_id = input_file.name

    llm = get_llm()
    kg = get_kg(reset=False)
    embed_model = get_embed_model()

    push_video_to_graph_db(video_transcripts, video_id,
                           embed_model, llm, kg, verbose=True)


def test_kg_query():
    llm = get_llm()
    kg = get_kg(reset=False)
    embed_model = get_embed_model()

    question = "Which is phone is popular because of its design?"
    out = get_answer(question, llm=llm, kg=kg, embed_model=embed_model, top_k=10,
                     return_context=False)
    print(out)


def test_kg_summary():
    llm = get_llm()
    kg = get_kg(reset=False)
    summary = get_summary_of_summaries(kg, llm)
    print(json.dumps(summary, indent=4))
    format_instructions = """Convert the summary to bullet points in HTML format.
Summary should contain a minimum of 6 bullet points which are insightful for decision making.
You can include a conclusion as well after the bullet points.
You may use bold fonts and colors for best viewing experience while reading the formatted summary."""
    formatted_summary = convert_answer_to_html(question="Prepare a summary of all video transcripts",
                                               answer=summary['summary'],
                                               format_instructions=format_instructions)
    summary["summary"] = formatted_summary["formatted_answer"]
    print(json.dumps(summary, indent=4))


def test_kg_summary_for_video():
    input_file = Path(
        '/home/sujithkumar/git/rag_hack/api/src/data/best_phones_under_15K.mp4')
    # llm = get_llm()
    kg = get_kg(reset=False)
    video_summary = get_summary_node(input_file.name, kg)
    print(json.dumps(video_summary, indent=4))


if __name__ == '__main__':
    # create_indexes()
    # test_video_indexing()
    # test_llm()
    # clear_graph()
    # test_kg()
    test_kg_query()
    # test_kg_summary()
    # test_kg_summary_for_video()
    # kg = get_kg(reset=False)
    # print(graph_stats(kg=kg))
