from __future__ import annotations

from typing import List
import os
import openai
import spacy

# Load spaCy model only once
NLP = spacy.load("en_core_web_sm")

openai.api_key = os.getenv("OPENAI_API_KEY", "")


def summarize(text: str) -> str:
    """Return a short summary of the text using OpenAI."""
    prompt = (
        "Summarize the following well document in two sentences:"\
    )
    response = openai.ChatCompletion.create(
        model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
        messages=[{"role": "user", "content": f"{prompt}\n{text}"}],
        temperature=0.3,
    )
    return response.choices[0].message["content"].strip()


def extract_tags(text: str) -> List[str]:
    """Extract key noun phrases from text."""
    doc = NLP(text)
    return list({chunk.text.lower() for chunk in doc.noun_chunks})


def prune_content(text: str) -> str:
    """Return lines likely containing operational data."""
    relevant = []
    for line in text.splitlines():
        lower = line.lower()
        if any(
            kw in lower
            for kw in ["pressure", "log", "event", "operator", "flow", "reading"]
        ) or any(char.isdigit() for char in line):
            relevant.append(line)
    return "\n".join(relevant)


def get_embedding(text: str) -> List[float]:
    """Generate an embedding using OpenAI."""
    resp = openai.Embedding.create(
        input=text,
        model=os.getenv("EMBED_MODEL", "text-embedding-ada-002"),
    )
    vector = resp["data"][0]["embedding"]
    if len(vector) != 1536:
        raise ValueError("Unexpected embedding size")
    return vector
