# 🎙️ AI Meeting Intelligence Assistant

An AI-powered Meeting Intelligence System built with Streamlit, NLP, RAG, and Generative AI.

This application can:

- 🎧 Transcribe meetings
- 📝 Generate summaries
- ✅ Extract action items
- 📌 Detect key decisions
- ❓ Identify open questions
- 💬 Chat with meetings using AI

Built for AI/ML portfolio projects, productivity tools, and meeting automation systems.

---

# 🚀 Features

## 🎥 Multiple Input Sources

- YouTube URL support
- Local audio/video upload

Supported formats:

- MP3
- WAV
- MP4
- M4A
- WEBM

---

## 🧠 AI Capabilities

### Meeting Transcription
Convert meeting audio/video into text.

### Smart Summarization
Generate concise AI-powered summaries.

### Action Item Extraction
Automatically detect tasks and responsibilities.

### Key Decision Detection
Identify important decisions discussed in meetings.

### Open Questions Extraction
Find unresolved discussion points.

### RAG-Based AI Chat
Ask questions directly from meeting context using Retrieval-Augmented Generation (RAG).

---

# 🛠️ Tech Stack

## Frontend
- Streamlit

## Backend / AI
- Python
- LangChain
- OpenAI / LLMs
- RAG Pipeline

## NLP / ML
- NLP
- Embeddings
- Vector Search

## Utilities
- dotenv
- tempfile

---

# 📂 Project Structure

```bash
project/
│
├── app.py
├── main.py
├── requirements.txt
├── .env
│
├── core/
│   ├── rag_engine.py
│   ├── transcription.py
│   ├── summarizer.py
│   └── embeddings.py
│
├── data/
├── outputs/
└── assets/