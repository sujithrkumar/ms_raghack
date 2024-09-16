# VidSage
https://www.youtube.com/watch?v=IUSCWtB9jWk

Vidsage focuses on processing video data, storing it in Azure AI services, and enabling advanced local and global querying through techniques - Azure AI Search (Native RAG), Graph-based Retrieval (Graph RAG), Open AI CLIP Model (Image Embeddings), Azure GPT-4o.

## Table of Contents

- [Introduction](#introduction)
- [Architecture](#architecture)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Querying](#querying)
  - [Local Querying](#local-querying)
  - [Global Querying](#global-querying)
- [Contributing](#contributing)
- [License](#license)

## Introduction

VidSage provides detailed business insights of videos using Azure AI Search, Advanced Graph RAG capability to analyze all the videos. 
Platform intelligent multi-modal chunking strategy helps it to point to the exact section in the video where a particular topic is discussed.

## Architecture

<!-- ![Architecture Diagram]![fin_img](https://github.com/user-attachments/assets/da9c49c4-b043-4063-b0ef-7b795ad6f6fe) -->
![](./rag_hack/api/assets/raghack-architecture.jpg)

The architecture consists of several stages:

1. **Video Upload**: Videos are uploaded to the repository.
2. **Processing**: Extract text using Azure Speech-to-Text (STT) service with speaker diarization and image keyframes from the videos.
3. **Embedding Creation**: 
   - Text embeddings are generated using the **Azure OpenAI Ada embedding model**.
   - Image embeddings are generated using **OpenAI CLIP model**.
4. **Azure AI Search**:
   - Store text embeddings in a **text index**.
   - Store image embeddings in an **image index**.
5. **Transcript Enhancement**: 
   - Text transcripts are enhanced with keyframe descriptions using **Azure OpenAI GPT-4o**.
    
6. **GRAPH RAG**:
   - Graph database to create a graph for our enhanced transcripts.
   - For any video, we create a Video node and summary node which contains video text transcript, Summary of the transcript as well as all the topics, features, issues, speakers and sentiment of the video.
   - Agentic chunking to convert all the sentences in a transcript to standalone sentences and then chunk the transcripts into relevant and meaningful chunks using GPT 4o mini. These chunks are connected to Video node.
   - For every chunk we extract triplets in form of entities and relationships and connect it the respective chunks.
   - Entity Disambiguation to ensure that the entities with similar name and meaning are not repeated.
    
6. **Storage**: Enhanced text transcripts and image keyframes are stored in **Azure Vector Index** for efficient retrieval.

## Features

- **Speaker Diarization**: Distinguish between multiple speakers in the video transcripts.
- **Keyframe Extraction**: Extract image keyframes to associate with text data.
- **Advanced Embeddings**: Use OpenAI models for generating text and image embeddings.
- **Graph Database Integration**: Store and retrieve data in a structured graph format using **Graph RAG**.
- **Entity Disambiguation**: Avoid repetition of entities with similar names and meanings.
- **Local and Global Querying**: Retrieve information specific to a video or across the entire video repository.

## Technology Stack

- **Azure Speech-to-Text** (STT) with speaker diarization
- **Azure OpenAI** (Ada embedding model, GPT-4o)
- **OpenAI CLIP** for image embeddings
- **Azure AI Search** for text and image indexes
- **Graph RAG** for graph-based retrieval
- **Entity and Relationship Extraction** for knowledge graph construction

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/your-repo.git
   cd your-repo
   ```

2. **Install Dependencies**:
   Make sure you have Python 3.8+ installed. Then, install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. **Azure Configuration**:
   Set up the following Azure services:
   - **Azure Speech-to-Text**
   - **Azure OpenAI** for text and image embeddings
   - **Azure AI Search** for vector indexing

4. **Environment Variables**:
   Set your Azure credentials in an `.env` file in the root directory:
   ```bash
   AZURE_API_KEY=<your-azure-api-key>
   AZURE_ENDPOINT=<your-azure-endpoint>
   ```
   
## Querying

### Local Querying

Local querying is performed for questions based on a specific video.

1. **Native Retrieval-Augmented Generation (RAG)**: Uses **Azure AI Search** to retrieve relevant text chunks and image keyframes related to the query.
2. **Response Generation**: The retrieved information is passed through **Azure GPT-4o** to generate answers.

### Global Querying

Global querying is performed across the entire video repository, including summary-based questions.

1. **Graph RAG**: Extracts relevant nodes from the graph using **vector search** and **graph traversal**.
2. **Response Generation**: Passes the structured data to **Azure GPT-4o** to generate a detailed response.

## Contributing

We welcome contributions to improve the project! Please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a Pull Request.
