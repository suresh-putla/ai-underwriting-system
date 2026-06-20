"""
LLM Module for LOUS
Handles OpenAI chat API integration for generating responses with RAG context
"""

import os
from typing import List, Dict, Any, AsyncIterator, Optional
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class LLM:
    """
    LLM class for OpenAI chat functionality.

    Supports both standard and streaming chat completions with RAG context integration.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "claude-haiku-4-5",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ):
        """
        Initialize the LLM client.

        Args:
            api_key: OpenAI API key (if None, reads from OPENAI_API_KEY env var)
            base_url: Optional base URL for OpenAI API (if None, reads from OPENAI_BASE_URL env var)
            model: Model to use (default: claude-haiku-4-5)
                   OpenAI models: gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo
                   Claude models: claude-sonnet-4-5-20250929, claude-haiku-4-5, claude-opus-4-7
            temperature: Sampling temperature (default: 0.7, range: 0.0-2.0)
            max_tokens: Maximum tokens in response (default: 1000)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key must be provided or set in OPENAI_API_KEY environment variable"
            )

        # Support custom base URL for OpenAI-compatible APIs
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")

        # Initialize async OpenAI client
        client_kwargs = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url

        self.client = AsyncOpenAI(**client_kwargs)

        # Model parameters
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Any:
        """
        Send a chat completion request.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
                     Example: [{"role": "user", "content": "Hello"}]
            temperature: Override default temperature
            max_tokens: Override default max_tokens
            stream: Whether to stream the response (default: False)

        Returns:
            If stream=False: Complete response text
            If stream=True: AsyncIterator yielding response chunks
        """
        temp = temperature if temperature is not None else self.temperature
        max_tok = max_tokens if max_tokens is not None else self.max_tokens

        if stream:
            return self._stream_chat(messages, temp, max_tok)
        else:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temp,
                max_tokens=max_tok,
                stream=False
            )
            return response.choices[0].message.content

    async def _stream_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int
    ) -> AsyncIterator[str]:
        """
        Internal method to handle streaming chat completions.

        Args:
            messages: List of message dicts
            temperature: Sampling temperature
            max_tokens: Maximum tokens

        Yields:
            String chunks from the streaming response
        """
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    async def chat_with_context(
        self,
        query: str,
        context_documents: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Any:
        """
        Generate a response using RAG context documents.

        This method formats the retrieved documents into a context string
        and includes it in the chat prompt for the LLM.

        Args:
            query: User's query
            context_documents: List of retrieved documents from RAG search
                             Each should have 'page_content' and optionally 'metadata'
            system_prompt: Optional system prompt (default: RAG-focused prompt)
            temperature: Override default temperature
            max_tokens: Override default max_tokens
            stream: Whether to stream the response

        Returns:
            If stream=False: Complete response text
            If stream=True: AsyncIterator yielding response chunks
        """
        # Default system prompt for RAG
        if system_prompt is None:
            system_prompt = (
                "You are a helpful AI assistant for a loan origination underwriting system. "
                "Use the provided context from policy documents to answer questions accurately. "
                "If the context doesn't contain relevant information, say so clearly. "
                "Always cite which section or policy you're referencing when possible."
            )

        # Format context documents
        context_text = self._format_context(context_documents)

        # Build messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context from policy documents:\n\n{context_text}\n\nQuestion: {query}"}
        ]

        # Call chat method
        return await self.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream
        )

    def _format_context(self, documents: List[Dict[str, Any]]) -> str:
        """
        Format retrieved documents into a context string.

        Args:
            documents: List of document dicts from RAG search

        Returns:
            Formatted context string
        """
        if not documents:
            return "No relevant context found."

        context_parts = []
        for i, doc in enumerate(documents, 1):
            content = doc.get('page_content', '')
            metadata = doc.get('metadata', {})

            # Format document with metadata if available
            source = metadata.get('source', 'Unknown')
            page = metadata.get('page', 'N/A')

            context_parts.append(
                f"[Document {i}]\n"
                f"Source: {source} (Page: {page})\n"
                f"Content: {content}\n"
            )

        return "\n---\n".join(context_parts)

    async def close(self):
        """Close the OpenAI client connection."""
        await self.client.close()
