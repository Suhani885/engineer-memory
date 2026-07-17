"""Utility for generating OpenAI embeddings."""
from __future__ import annotations

import logging

from openai import OpenAI

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def generate_embeddings(texts: list[str]) -> list[list[float]] | None:
    """Generate embeddings for a list of strings using OpenAI.
    
    Returns a list of vectors (list of floats) corresponding to the input texts.
    If the API key is missing or an error occurs, returns None.
    """
    settings = get_settings()
    if not settings.openai_api_key:
        return None

    client = OpenAI(api_key=settings.openai_api_key)

    try:
        response = client.embeddings.create(
            input=texts,
            model="text-embedding-3-small",
        )
        # Re-order just in case, though the API returns them in order
        sorted_data = sorted(response.data, key=lambda x: x.index)
        return [item.embedding for item in sorted_data]
    except Exception as e:
        logger.error(f"Failed to generate embeddings: {e}")
        return None
