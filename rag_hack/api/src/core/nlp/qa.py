import base64
import logging
from pathlib import Path

from core.nlp.azure_openai import AzureOpenAILLM
from core.nlp.prompts import convert_text_to_html_system_prompt_v1, qa_system_prompt_v1, image_query_system_prompt_v1
from config import LLM_CONF, BLOB_CONF, VIDEO_INSIGHTS_CONFIG
from utils.custom_logging import setup_logging
from utils.storage_manager import AzureBLOB
from PIL import Image


setup_logging()
logger = logging.getLogger("project_logger")


def answer_to_image_query(query_image_content: bytes, chunks: list):
    llm_messages = [
        {
            "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": image_query_system_prompt_v1()
                        }
                    ]
        }
    ]
    relevant_transcripts = "Relevant Images (Keyframes):"
    relevant_keyframes = []
    for chunk in chunks:
        # relevant_transcripts += f"\nVideo Name:\n{chunk['video_name']}\nVisual Description of Video snippet Keyframes:\n{chunk['keyframes_description']}\nVideo Snippet Transcripts:\n{chunk['transcripts']}\n"
        if chunk['keyframe_paths']:
            relevant_keyframes.extend(
                [f"{chunk['video_name']}/{Path(keyframe_path).name}" for keyframe_path in chunk['keyframe_paths']])

    relevant_keyframes = list(set(relevant_keyframes))
    # considering only the top 4 images to answer the query
    relevant_keyframes = relevant_keyframes[:4]
    storage_manager = AzureBLOB(BLOB_CONF=BLOB_CONF)
    relevant_keyframe_paths = []
    for relevant_keyframe_path in relevant_keyframes:
        download_path = VIDEO_INSIGHTS_CONFIG['keyframes_dir'] / \
            relevant_keyframe_path
        download_path.parent.mkdir(parents=True, exist_ok=True)
        if not download_path.exists():
            storage_manager.download(
                container_name=BLOB_CONF["keyframe_container"],
                blob_name=relevant_keyframe_path,
                download_path=download_path
            )
        relevant_keyframe_paths.append(download_path)
    relevant_keyframes_encodings = [base64.b64encode(
        open(keyframe_path, 'rb').read()).decode('ascii') for keyframe_path in relevant_keyframe_paths]

    user_message_contents = [
        {
            "type": "text",
            "text": relevant_transcripts
        }
    ]
    for relevant_keyframe_encoding in relevant_keyframes_encodings:
        image_content = {
            "type": "image_url",
            "image_url": {
                    "url": f"data:image/jpeg;base64,{relevant_keyframe_encoding}"
            }
        }
        user_message_contents.append(
            image_content
        )

    llm_messages.append(
        {
            "role": "user",
            "content": user_message_contents
        }
    )
    query_image_encoding = base64.b64encode(
        query_image_content).decode('ascii')
    llm_messages.append(
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Query Image: "
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{query_image_encoding}"
                    }
                }
            ]
        }
    )
    llm = AzureOpenAILLM(LLM_CONF=LLM_CONF)
    llm_response = llm.get_llm_response(messages=llm_messages)

    return llm_response

def answer_from_chunks(question: str, chunks: list):
    llm_messages = [
        {
            "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": qa_system_prompt_v1()
                        }
                    ]
        }
    ]
    relevant_transcripts = "Relevant Transcripts:"
    relevant_keyframes = []
    for chunk in chunks:
        relevant_transcripts += f"\nVideo Name:\n{chunk['video_name']}\nVisual Description of Video snippet Keyframes:\n{chunk['keyframes_description']}\nVideo Snippet Transcripts:\n{chunk['transcripts']}\n"
        if chunk['keyframe_paths']:
            relevant_keyframes.extend(
                [f"{chunk['video_name']}/{Path(keyframe_path).name}" for keyframe_path in chunk['keyframe_paths']])

    relevant_keyframes = list(set(relevant_keyframes))
    # considering only the top 4 images to answer the query
    relevant_keyframes = relevant_keyframes[:4]
    storage_manager = AzureBLOB(BLOB_CONF=BLOB_CONF)
    relevant_keyframe_paths = []
    for relevant_keyframe_path in relevant_keyframes:
        download_path = VIDEO_INSIGHTS_CONFIG['keyframes_dir'] / \
            relevant_keyframe_path
        download_path.parent.mkdir(parents=True, exist_ok=True)
        if not download_path.exists():
            storage_manager.download(
                container_name=BLOB_CONF["keyframe_container"],
                blob_name=relevant_keyframe_path,
                download_path=download_path
            )
        relevant_keyframe_paths.append(download_path)
    relevant_keyframes_encodings = [base64.b64encode(
        open(keyframe_path, 'rb').read()).decode('ascii') for keyframe_path in relevant_keyframe_paths]

    user_message_contents = [
        {
            "type": "text",
            "text": relevant_transcripts
        }
    ]
    for relevant_keyframe_encoding in relevant_keyframes_encodings:
        image_content = {
            "type": "image_url",
            "image_url": {
                    "url": f"data:image/jpeg;base64,{relevant_keyframe_encoding}"
            }
        }
        user_message_contents.append(
            image_content
        )

    llm_messages.append(
        {
            "role": "user",
            "content": user_message_contents
        }
    )
    llm_messages.append(
        {
            "role": "user",
            "content": question
        }
    )
    llm = AzureOpenAILLM(LLM_CONF=LLM_CONF)
    llm_response = llm.get_llm_response(messages=llm_messages)

    return llm_response


def convert_answer_to_html(question: str, answer: str, format_instructions: str):
    llm_messages = [
        {
            "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": convert_text_to_html_system_prompt_v1()
                        }
                    ]
        }
    ]
    user_message_contents = [
        {
            "type": "text",
            "text": f"Question: {question}\nAnswer: {answer}"
        },
        {
            "type": "text",
            "text": format_instructions
        }
    ]
    llm_messages.append(
        {
            "role": "user",
            "content": user_message_contents
        }
    )

    llm = AzureOpenAILLM(LLM_CONF=LLM_CONF)
    llm_response = llm.get_llm_response(messages=llm_messages)
    if llm_response:
        return llm_response
    else:
        logger.error(
            f"Couldn't format the summary. Returning without formatting...")
        return {
            "formatted_answer": answer
        }
