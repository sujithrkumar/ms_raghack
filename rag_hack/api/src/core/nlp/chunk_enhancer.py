import base64
import logging

from core.nlp.prompts import keyframe_description_system_prompt_v1
from config import LLM_CONF
from core.nlp.azure_openai import AzureOpenAILLM
from utils.custom_logging import setup_logging


setup_logging()
logger = logging.getLogger("project_logger")


def get_keyframes_description(transcripts, keyframe_paths) -> str:
    llm_messages = [
        {
            "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": keyframe_description_system_prompt_v1()
                        }
                    ]
        }
    ]
    relevant_keyframes_encodings = [base64.b64encode(
        open(keyframe_path, 'rb').read()).decode('ascii') for keyframe_path in keyframe_paths]

    relevant_transcripts = f"Transcripts for the video snippet:\n{transcripts}"
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
            "content": "Prepare the keyframes_description in JSON format."
        }
    )
    llm = AzureOpenAILLM(LLM_CONF=LLM_CONF)
    llm_response = llm.get_llm_response(messages=llm_messages)
    if llm_response:
        return llm_response['keyframes_description']
    else:
        return ""
