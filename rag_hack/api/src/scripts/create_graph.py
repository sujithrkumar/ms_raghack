import numpy as np
import time
from tqdm import tqdm
import os
import uuid
import warnings
from dotenv import load_dotenv

from langchain.output_parsers.openai_tools import JsonOutputToolsParser
from langchain.chains import create_extraction_chain, create_extraction_chain_pydantic
from langchain_openai.chat_models import ChatOpenAI, AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain import hub
from langchain_community.callbacks import get_openai_callback
from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings


from langchain_community.graphs import Neo4jGraph
from langchain.pydantic_v1 import BaseModel, Field
from typing import List, Tuple, Literal, Optional

from scripts.agentic_chunking import decompose_to_propositions, AgenticChunker
from config import NEO4J_CONF,PRIVATE_OPEN_AI_CONF

warnings.filterwarnings("ignore")
load_dotenv()


def graph_stats(kg):
    cypher = """
    match (n) return count(n) as node_cnt
    """

    node_count = kg.query(cypher)[0]["node_cnt"]

    cypher = """
    match (n)
    unwind labels(n) as node_labels
    with collect(node_labels) as labels_arr
    return labels_arr
    """

    ent, freq = np.unique(
        kg.query(cypher)[0]["labels_arr"], return_counts=True)
    ent_count = {}
    for i in range(len(ent)):
        ent_count[ent[i]] = freq[i]

    cypher = """
    match (n)-[r]->(m)
    return count(r) as rel_cnt
    """

    rel_cnt = kg.query(cypher)[0]["rel_cnt"]

    cypher = """
    match (m)-[r]->(n)
    return collect(type(r)) as rel_arr
    """
    out = kg.query(cypher)
    rel_unq, rel_freqs = np.unique(out[0]["rel_arr"], return_counts=True)
    rel_dict = {rel_unq[i]: rel_freqs[i] for i in range(len(rel_unq))}

    return {
        "node_count": node_count,
        "ent_count_dict": ent_count,
        "rel_count_dict": rel_dict,
        "rel_cnt": rel_cnt
    }


def clear_db(kg):
    cypher = """
    match (n) detach delete n
    """

    kg.query(cypher)


def clear_db_indexes(kg):
    cypher = """
    show indexes where type <> 'LOOKUP'
    """
    indexes = kg.query(cypher)

    for index in indexes:
        if index["type"] == "RANGE":
            drop_cypher = f"drop constraint {index['name']}"
            kg.query(drop_cypher)
        elif index["type"] == "VECTOR":
            drop_cypher = f"drop index {index['name']}"
            kg.query(drop_cypher)

    kg.query("show indexes")


def get_chunks(data, llm, chunks=None, generate_new_metadata_ind=True, verbose=False, max_sents=10):
    sentences = decompose_to_propositions(data, llm)
    print(f"Retrieved {len(sentences)} propositions from the data")
    chunker = AgenticChunker(llm=llm, chunks=chunks, print_logging=verbose,
                             generate_new_metadata_ind=generate_new_metadata_ind, max_sents=max_sents)
    chunker.add_propositions(sentences)
    retrieved_chunks = chunker.get_chunks(get_type="dict")

    conv_data = []
    for k, v in retrieved_chunks.items():
        conv_data.append("\n".join(v["propositions"]))

    return conv_data


class Summary(BaseModel):
    """
    Get summary and relevant information from the text.
    """
    summary: str = Field(description="Summary of the text")
    sentiment: float = Field(
        description="Sentiment of the text. It should be a float value between 0 to 1. Where 0 denotes bad, 1 denotes good and 0.5 denotes neutral")
    speakers: Optional[List[str]] = Field(
        description="List of the all the speakers in the text")
    issues: Optional[List[str]] = Field(
        description="List of all the issues discussed in the text.")
    topics: Optional[List[str]] = Field(
        description="List of all the topics discussed in the text")
    features: Optional[List[str]] = Field(
        description="List of all the product features discussed.")


def get_summary(text, llm):
    template = """
    Given a text, Summarize the text and also retrieve the sentiment of the text.
    Sentiment should be a float value between 0 to 1. Where 0 denotes bad, 1 denotes good and 0.5 denotes neutral

    TEXT:
    {text}
    """

    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm.with_structured_output(Summary)
    return chain.invoke({"text": text})


class Entity(BaseModel):
    """
    Extracted Entity from the text
    """
    name: str = Field(
        description="Name denoting the entity. Should be unique and in few words only. Keep the name compact and meaningful.")
    desc: str = Field(description="Description of the entity related to the given text. The description should as mentioned in the text. Do not assume or you use your own knowledge. Just use information provided.")


class Relationship(BaseModel):
    """
    Relationship between two entities.
    """
    name: str = Field(
        description="Name denoting the relationship between two entities. Should be unique and in few words only. Keep the name compact and meaningful.")
    desc: str = Field(description="Description of the relationshiop related to the extracted entities. The description should as mentioned in the text. Do not assume or you use your own knowledge. Just use information provided.")


class Triplet(BaseModel):
    """
    Extracted Triplet i.e. Tuple[Entity, Relationship, Entity from the text]
    A triplet contains relationship between 2 entities.
    """
    entity_1: Entity = Field(description="First entity extracted")
    relation: Relationship = Field(
        description="Relationship between the extracted Entities.")
    entity_2: Entity = Field(description="Second entity extracted")


class Triplets(BaseModel):
    """
    List of Extracted Triplets from the text.
    """
    triplets: List[Triplet] = Field(
        description="List of all the extracted triplets from the text.")


def extract_triplets(text, llm, limit=10):
    template = """
    Extract all the Triplets from the text.
    A triplet is a tuple of [Entity, Relationship, Entity] which signifies relationship between two entities.
    Entity could be a place, organisation, or a concept, feeling, emotion, event described in the text.

    Relationship is the compact description of how the two entities are related.

    **Limit the extracted Triplets to {limit}. Pick the most important {limit} Triplets**

    Here is the text:
    {text}
    """
    chain = ChatPromptTemplate.from_template(
        template) | llm.with_structured_output(Triplets)

    results = chain.invoke({"text": text, "limit": 10}).triplets
    return results


def set_call_and_summary_node_cypher(kg, video_id, video_data, video_sentiment, video_issues, video_summary, video_speakers, video_topics, video_features):
    """
    CREATE VIDEO AND VIDEO_SUMMARY NODE.
    """

    # CREATE VIDEO NODE UNIQUENESS
    cypher_video_constraint = """
    create constraint unique_video if not exists
    for (video : VIDEO) require video.video_id is unique
    """

    # CREATE CALL SUMMARY NODE UNIQUENESS
    cypher_video_summ_constraint = """
    create constraint unique_summary if not exists
    for (summ : VIDEO_SUMMARY) require summ.video_id is unique
    """

    kg.query(cypher_video_constraint)
    kg.query(cypher_video_summ_constraint)

    cypher_create_video_and_summ = """
    merge (video : VIDEO {video_id : $video_id})
    on create
    set
    video.data = $video_data,
    video.sentiment = $video_sentiment,
    video.issues = $video_issues,
    video.speakers = $video_speakers,
    video.topics = $video_topics,
    video.features = $video_features


    merge (summ : VIDEO_SUMMARY {video_id : $video_id})
    on create
    set
    summ.summary = $video_summary,
    summ.sentiment = $video_sentiment,
    summ.issues = $video_issues,
    summ.speakers = $video_speakers,
    summ.topics = $video_topics,
    summ.features = $video_features

    merge (video)-[r : SUMMARY_REL]->(summ)
    on create set
    r.video_id = $video_id
    """

    params = {
        "video_id": video_id,
        "video_data": video_data,
        "video_sentiment": video_sentiment,
        "video_issues": video_issues,
        "video_speakers": video_speakers,
        "video_topics": video_topics,
        "video_features": video_features,
        "video_summary": video_summary
    }
    kg.query(cypher_create_video_and_summ, params=params)


def create_video_and_summary_nodes(video_data, video_id, llm, kg):
    summary_dct = get_summary(video_data, llm)
    video_id = video_id
    video_data = video_data
    video_sentiment = summary_dct.sentiment
    video_issues = summary_dct.issues
    video_speakers = summary_dct.speakers
    video_topics = summary_dct.topics
    video_features = summary_dct.features
    video_summary = summary_dct.summary

    set_call_and_summary_node_cypher(kg, video_id, video_data, video_sentiment,
                                     video_issues, video_summary, video_speakers, video_topics, video_features)
    print(f"Created Video Node : {video_id}")


def get_summary_node(video_id, kg):
    get_summary_node_cypher = """
    match (summ : VIDEO_SUMMARY {video_id : $video_id})
    return summ
    """
    return kg.query(get_summary_node_cypher, params={"video_id": video_id})[0]["summ"]


def create_video_chunks_cypher(video_chunks, video_id, kg, embed_model, verbose=False):
    cypher_video_unique = """
    create constraint unique_chunk if not exists
    for (chunk : Chunk) require chunk.chunk_id is unique
    """
    kg.query(cypher_video_unique)
    if verbose:
        print("Created unique chunk constraint")

    cypher_chunk_vector_index = """
    create vector index chunk_vector_index if not exists
    for (chunk : Chunk) on (chunk.embed)
    options{
        indexConfig : {
            `vector.dimensions` : 1536,
            `vector.similarity_function` : 'cosine'
        }
    }
    """
    kg.query(cypher_chunk_vector_index)
    if verbose:
        print("Created chunk vector index")

    cypher_create_video_chunk = """
    merge (chunk : Chunk {chunk_id : $chunk_id})
    on create 
    set
        chunk.data = $data,
        chunk.video_id = $video_id
    on match
    set
        chunk.data = $data

    with chunk
    match (video : VIDEO {video_id : $video_id})
    merge (video)-[r : CHUNK_OF]->(chunk)
    on create set
    r.video_id = $video_id
    """

    cypher_video_embed_fill = """
    match (chunk:Chunk {chunk_id : $chunk_id})
    with chunk, $chunk_embed as chunk_embed
    set chunk.embed = chunk_embed
    """

    if verbose:
        print("Starting chunk and chunk_embed creation")

    for i in tqdm(range(len(video_chunks))):
        chunk_id = f"{video_id}_chunk{i}"
        data = video_chunks[i]

        params = {
            "chunk_id": chunk_id,
            "data": data,
            "video_id": video_id
        }

        kg.query(cypher_create_video_chunk, params=params)

        chunk_embed = embed_model.embed_query(data)
        kg.query(cypher_video_embed_fill, params={
                 "chunk_id": chunk_id, "chunk_embed": chunk_embed})

    if verbose:
        print("Completed chunk and chunk_embed creation")


def check_to_match(ent_1, ent_2, llm):
    template = """
    Given 2 entities. Tell, whether the entities should be merged together i.e. the two entities are denoting the same thing.
    Only Return `yes` or `no`

    Entity 1 :
    {ent_1}

    Entity_2 :
    {ent_2}
    """
    chain = ChatPromptTemplate.from_template(template) | llm
    return chain.invoke({"ent_1": ent_1, "ent_2": ent_2}).content


def find_ent_name_to_merge_with(main_entity, ent_list, llm):
    main_ent = {
        "ent_name": main_entity["name"],
        "ent_desc": main_entity["desc"]
    }

    # ent_list : [(ent_name, ent_desc)]
    # main_ent : (ent_name, ent_desc)

    for find_ent in ent_list:
        out = check_to_match(str(main_ent), str(find_ent), llm)
        if out.lower() == 'yes':
            return find_ent
    return


def merge_the_entities_in_graph(kg, ent_1_name, ent_2_name):
    cypher = """
    match (ent_1 : Entity {name : $ent_1_name}), (ent_2 : Entity {name : $ent_2_name})
    with ent_1, ent_2
    set
    ent_1.name = coalesce(ent_1.name, ent_2.name),
    ent_1.desc = coalesce(ent_1.desc, ent_2.desc)    
    with ent_1, ent_2
    call apoc.refactor.mergeNodes([ent_1, ent_2]) YIELD node
    return node
    """
    return kg.query(cypher, params={"ent_1_name": ent_1_name, "ent_2_name": ent_2_name})[0]["node"]


def create_entity_and_relation_cypher(kg, video_chunks, video_id, embed_model, llm):
    # ENTITY CONSTRAINT
    cypher_unq_entity = """
    create constraint unique_entity if not exists
    for (ent : Entity) require ent.name is unique
    """
    kg.query(cypher_unq_entity)

    # RELATION CONSTRAINT
    cypher_unq_rel = """
    create constraint unique_relation if not exists
    for (rel : Relation) require rel.name is unique
    """
    kg.query(cypher_unq_rel)

    cypher_ent_vector_index = """
    create vector index entity_vector_index if not exists
    for (ent : Entity) on (ent.embed)
    options{
        indexConfig : {
            `vector.dimensions` : 1536,
            `vector.similarity_function` : 'cosine'
        }
    }
    """
    kg.query(cypher_ent_vector_index)

    cypher_ent_name_vector_index = """
    create vector index entity_name_vector_index if not exists
    for (ent : Entity) on (ent.name_embed)
    options{
        indexConfig : {
            `vector.dimensions` : 1536,
            `vector.similarity_function` : 'cosine'
        }
    }
    """
    kg.query(cypher_ent_name_vector_index)

    #####################################################################

    # INPUT : ent_name_1, ent_desc_1, ent_name_2, ent_desc_2, rel_name,
    cypher_create_ent = """
        merge (ent_1 : Entity {name : $ent_name_1})
        on create set
        ent_1.desc = $ent_desc_1

        merge (ent_2 : Entity {name : $ent_name_2})
        on create set
        ent_2.desc = $ent_desc_2

        merge (ent_1)-[r : Relation {name : $rel_name}]->(ent_2)
        on create set
        r.desc = $rel_desc


        with ent_1, ent_2

        match (chunk : Chunk {chunk_id : $chunk_id})

        with chunk, ent_1, ent_2

        merge (chunk)-[r_1 : MENTIONS]->(ent_1)
        on create set
        r_1.video_id = chunk.video_id

        merge (chunk)-[r_2 : MENTIONS]->(ent_2)
        on create set
        r_2.video_id = chunk.video_id
    """

    cypher_find_similar_ent = """
    with $ent_embed as q_emb
    call db.index.vector.queryNodes($index_name, $top_k, q_emb) yield node, score
    with score, node.name as ent_name, node.desc as ent_desc
    where ent_name <> $entity_name and score > $cutoff
    return score, ent_name, ent_desc
    """

    cypher_find_connected_chunks = """
    match (chunk : Chunk)-[:MENTIONS]->(ent : Entity {name : $ent_name})
    with chunk.embed as chunk_embed
    return collect(chunk_embed) as chunk_embed_list
    """

    cypher_fill_ent_embed = """
    match (ent : Entity {name : $ent_name})
    set ent.embed = $ent_embed
    """

    cypher_fill_ent_name_embed = """
    match (ent : Entity {name : $ent_name})
    set ent.name_embed = $ent_name_embed
    """

    for i in tqdm(range(len(video_chunks))):
        try:
            out_vals = extract_triplets(video_chunks[i], llm=llm, limit=10)
            print("triplets")
            print(out_vals)
            for out in out_vals:
                ent_1_name = out.entity_1.name
                ent_1_desc = out.entity_1.desc

                rel_name = out.relation.name
                rel_desc = out.relation.desc

                ent_2_name = out.entity_2.name
                ent_2_desc = out.entity_2.desc

                chunk_id = f"{video_id}_chunk{i}"

                params = {
                    "ent_name_1": ent_1_name,
                    "ent_desc_1": ent_1_desc,
                    "ent_name_2": ent_2_name,
                    "ent_desc_2": ent_2_desc,
                    "rel_name": rel_name,
                    "rel_desc": rel_desc,
                    "chunk_id": chunk_id
                }

                kg.query(cypher_create_ent, params=params)

                ent_1_name_embed = embed_model.embed_query(ent_1_name)
                ent_2_name_embed = embed_model.embed_query(ent_2_name)

                kg.query(cypher_fill_ent_name_embed, params={
                         "ent_name": ent_1_name, "ent_name_embed": ent_1_name_embed})
                kg.query(cypher_fill_ent_name_embed, params={
                         "ent_name": ent_2_name, "ent_name_embed": ent_2_name_embed})

                try:

                    params = {
                        "entity_name": ent_1_name,
                        "ent_embed": embed_model.embed_query(ent_1_name),
                        "index_name": "entity_name_vector_index",
                        "top_k": 5,
                        "cutoff": 0.85
                    }
                    similar_ents = kg.query(
                        cypher_find_similar_ent, params=params)
                    ent_1 = kg.query("match (ent : Entity {name : $ent_name}) return ent", params={
                                     "ent_name": ent_1_name})[0]["ent"]
                    name_to_merge_1 = find_ent_name_to_merge_with(
                        ent_1, similar_ents, llm)

                    params = {
                        "entity_name": ent_2_name,
                        "ent_embed": embed_model.embed_query(ent_2_name),
                        "index_name": "entity_name_vector_index",
                        "top_k": 5,
                        "cutoff": 0.85
                    }
                    similar_ents = kg.query(
                        cypher_find_similar_ent, params=params)
                    ent_2 = kg.query("match (ent : Entity {name : $ent_name}) return ent", params={
                                     "ent_name": ent_2_name})[0]["ent"]
                    name_to_merge_2 = find_ent_name_to_merge_with(
                        ent_2, similar_ents, llm)

                    if name_to_merge_1 is not None:
                        merge_1_name = name_to_merge_1["ent_name"]
                        print(f"Merging {ent_1_name} and {merge_1_name}")
                        ent_1 = merge_the_entities_in_graph(kg,
                                                            ent_1_name, merge_1_name)
                        ent_1_name = ent_1["name"]

                    if name_to_merge_2 is not None:
                        merge_2_name = name_to_merge_2["ent_name"]
                        print(f"Merging {ent_2_name} and {merge_2_name}")
                        ent_2 = merge_the_entities_in_graph(kg,
                                                            ent_2_name, merge_2_name)
                        ent_2_name = ent_2["name"]
                except Exception as e:
                    print(e)
                    continue

                ent_1_embed = list(np.array(kg.query(cypher_find_connected_chunks, params={
                                   "ent_name": ent_1_name})[0]["chunk_embed_list"]).mean(axis=0))
                ent_2_embed = list(np.array(kg.query(cypher_find_connected_chunks, params={
                                   "ent_name": ent_2_name})[0]["chunk_embed_list"]).mean(axis=0))

                # print(f"ent_1_embed : {ent_1_embed[:5]}")
                # print(f"ent_2_embed : {ent_2_embed[:5]}")

                kg.query(cypher_fill_ent_embed, params={
                         "ent_name": ent_1_name, "ent_embed": ent_1_embed})
                kg.query(cypher_fill_ent_embed, params={
                         "ent_name": ent_2_name, "ent_embed": ent_2_embed})
        except Exception as e:
            time.sleep(10)
            print("Exception: ", e)
            continue


def get_context(question, llm, kg, embed_model, top_k=10):
    cypher = """
    with $q_emb as q_emb
    call db.index.vector.queryNodes($index_name, $top_k, q_emb) yield node, score
    with node, score
    match (node)-[r : Relation]-(ent : Entity)
    match (node)<-[r_m : MENTIONS]-(chunk : Chunk)
    return node {.name, .desc}, r {.name, .desc}, ent {.name, .desc}, chunk {.chunk_id, .data, .sentiment, .issues, .features, .topics, .speakers}
    """

    params = {
        "q_emb": embed_model.embed_query(question),
        "index_name": "entity_vector_index",
        "top_k": top_k
    }

    results = kg.query(cypher, params=params)

    info = ""
    rel_chunks = set()
    rel_chunks_ids = set()
    for res in results:
        info += f"{res['node']['name']} : {res['node']['desc']} ---- IS RELATED VIA ---- {res['r']['name']} : {res['r']['desc']} ---- TO ---- {res['ent']['name']} : {res['ent']['desc']}"
        info += "\n"
        if res['chunk']['chunk_id'] not in rel_chunks_ids:
            chunk_info = f"""
            {res['chunk']['data']}
            The sentiment of chunk is {res['chunk']['sentiment']}
            The issues related are {res['chunk']['issues']}
            The features related are {res['chunk']['features']}
            The topics related are {res['chunk']['topics']}
            The speakers related are {res['chunk']['speakers']}
            """
            rel_chunks.add(chunk_info)
            rel_chunks_ids.add(res['chunk']['chunk_id'])

    info += "\n\n"
    info += "The further relevant data chunks information is as follows: "
    info += "\n\n".join(list(rel_chunks))

    return info


def get_output(question, llm, kg, embed_model, top_k=10):
    context = get_context(question, llm=llm, kg=kg,
                          embed_model=embed_model, top_k=top_k)
    template = """
    You are analyzing mobile phone video reviews to answer a given question. 
Given a question and the relevant context retrieved from mobile phone video reviews transcripts you need to return a detailed answer to the question.

    Relevant Context :
    {context}

    Question :
    {question}
    """

    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm
    out = chain.invoke({"question": question, "context": context}).content
    return out, context


def push_video_to_graph_db(video_data, video_id, embed_model, llm, kg, verbose=True):
    create_video_and_summary_nodes(video_data, video_id, llm, kg)
    if verbose:
        print("Created Video and Summary Nodes")
    video_chunks = get_chunks(video_data, llm)
    if verbose:
        print("Found Video Chunks")
    create_video_chunks_cypher(
        video_chunks, video_id, kg, embed_model, verbose=False)
    if verbose:
        print("Created Video Chunks")
    create_entity_and_relation_cypher(
        kg, video_chunks, video_id, embed_model, llm)
    if verbose:
        print("Create Entity and Relations")

    if verbose:
        kg.refresh_schema()
        print(kg.schema)
        print("-" * 100)
        print(graph_stats(kg))

    return


def get_answer(question, llm, kg, embed_model, top_k=10, return_context=False):
    out, context = get_output(question, llm=llm, kg=kg,
                              embed_model=embed_model, top_k=10)
    if return_context:
        return out, context
    return out


class SUMMARY_OF_SUMMARIES(BaseModel):
    summary: str = Field(
        description="Overall summary of the videos in 10 sentences in HTML format.")
    issues: Optional[List[str]] = Field(
        description="All the issues mentioned.")
    features: Optional[List[str]] = Field(
        description="All the features mentioned.")
    topics: Optional[List[str]] = Field(
        description="All the topics mentioned.")


def get_summary_of_summaries(kg, llm):
    summary_nodes = kg.query("match (vid_sum : VIDEO_SUMMARY) return vid_sum")
    text = ""
    for node in summary_nodes:
        text += str(node)
        text += "\n\n"

    template = """
    Given below are some video summaries prepared from video transcripts. Summarize them to get a final summary for all videos.
    Video Summaries:
    {text}
    """
    chain = ChatPromptTemplate.from_template(
        template) | llm.with_structured_output(SUMMARY_OF_SUMMARIES)
    response = chain.invoke({"text": text})
    summary = {
        "summary": response.summary,
        "topics": response.topics,
        "features": response.features,
        "issues": response.issues
    }
    return summary


# 3
def get_llm():
    # LLM_CONF = {
    #     "api_key": os.environ.get("AZURE_OPENAI_KEY"),
    #     "end_point": os.environ.get("AZURE_OPENAI_ENDPOINT")
    # }

    # llm = AzureChatOpenAI(
    #     deployment_name = "rag-hack-gpt4o",
    #     api_key = LLM_CONF["api_key"],
    #     model_name = "gpt-4o",
    #     temperature = 0.1,
    #     verbose = True,
    #     azure_endpoint = LLM_CONF["end_point"],
    #     api_version = "2024-02-15-preview"
    # )

    os.environ["OPENAI_API_KEY"] = PRIVATE_OPEN_AI_CONF["PRIVATE_OPENAI_API_KEY"]
    llm = ChatOpenAI(model="gpt-4o-mini")
    return llm


def get_kg(reset=False):

    os.environ["NEO4J_URI"] = NEO4J_CONF["NEO4J_URI"]
    os.environ["NEO4J_USERNAME"] = NEO4J_CONF["NEO4J_USERNAME"]
    os.environ["NEO4J_PASSWORD"] = NEO4J_CONF["NEO4J_PASSWORD"]
    os.environ["AURA_INSTANCEID"] = NEO4J_CONF["AURA_INSTANCEID"]
    os.environ["AURA_INSTANCENAME"] = NEO4J_CONF["AURA_INSTANCENAME"]

    kg = Neo4jGraph()

    if reset:
        clear_db(kg)
        clear_db_indexes(kg)
    return kg


def get_embed_model():
    # EMBED_CONF = {
    #     "AZURE_OPENAI_ENDPOINT": os.getenv("AZURE_OPENAI_ENDPOINT_EMBED"),
    #     "AZURE_OPENAI_API_KEY": os.getenv("AZURE_OPENAI_API_KEY_EMBED"),
    #     "AZURE_OPENAI_API_VERSION": os.getenv("AZURE_OPENAI_API_VERSION_EMBED"),
    #     "IMAGE_EMBED_MODEL": "openai/clip-vit-base-patch16"
    # }

    # print(EMBED_CONF)
    # embed_model = AzureOpenAIEmbeddings(
    #     model = "rag-hack-ada",
    #     azure_endpoint = EMBED_CONF["AZURE_OPENAI_ENDPOINT"],
    #     api_key = EMBED_CONF["AZURE_OPENAI_API_KEY"],
    #     openai_api_version = EMBED_CONF["AZURE_OPENAI_API_VERSION"]
    # )
    # return embed_model
    os.environ["OPENAI_API_KEY"] = PRIVATE_OPEN_AI_CONF["PRIVATE_OPENAI_API_KEY"]
    embed_model = OpenAIEmbeddings(model='text-embedding-ada-002')
    return embed_model


if __name__ == "__main__":
    with open("sample_transcript.txt") as f:
        video_data = f.read()
    video_id = "video_0"

    llm = get_llm()
    kg = get_kg(reset=False)
    embed_model = get_embed_model()

    push_video_to_graph_db(video_data, video_id,
                           embed_model, llm, kg, verbose=True)
    question = "What kind of devices are being discussed about ?"
    out = get_answer(question, llm=llm, kg=kg, embed_model=embed_model, top_k=10,
                     return_context=False)
    print(out)
