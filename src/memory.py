"""
Conversation memory: cheap sliding window + optional long-term vector store.
Summarization kicks in when token count crosses a threshold — same pattern we use in prod.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, Sequence, Tuple

import tiktoken
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


class VectorStore(Protocol):
    def add(self, texts: Sequence[str], metadatas: Optional[Sequence[dict]] = None) -> None: ...
    def query(self, text: str, k: int = 4) -> List[Tuple[str, float]]: ...


@dataclass
class MemoryConfig:
    model: str = "gpt-4o-mini"
    max_tokens_window: int = 6_000
    summarize_trigger_tokens: int = 5_000
    recall_top_k: int = 4
    embedding_dims: int = 1536


class ConversationMemory:
    def __init__(
        self,
        cfg: MemoryConfig,
        vector_store: Optional[VectorStore] = None,
        summarizer_llm: Optional[ChatOpenAI] = None,
    ) -> None:
        self._cfg = cfg
        self._vector = vector_store
        self._llm = summarizer_llm or ChatOpenAI(model=cfg.model, temperature=0.2)
        self._encoding = tiktoken.encoding_for_model(cfg.model)
        self._messages: List[BaseMessage] = []
        self._summary: str = ""
        self._turn_counter = 0

    def _count_tokens(self, texts: Sequence[str]) -> int:
        return sum(len(self._encoding.encode(t)) for t in texts)

    def _window_texts(self) -> List[str]:
        out: List[str] = []
        for m in self._messages:
            if isinstance(m, HumanMessage):
                out.append("User: " + str(m.content))
            elif isinstance(m, AIMessage):
                out.append("Assistant: " + str(m.content))
            elif isinstance(m, SystemMessage):
                out.append("System: " + str(m.content))
        if self._summary:
            out.insert(0, "Summary of earlier conversation:\n" + self._summary)
        return out

    def add_user(self, text: str, metadata: Optional[dict] = None) -> None:
        self._append(HumanMessage(content=text), text_for_vector=text, metadata=metadata)

    def add_ai(self, text: str, metadata: Optional[dict] = None) -> None:
        self._append(AIMessage(content=text), text_for_vector=text, metadata=metadata)

    def _append(
        self,
        msg: BaseMessage,
        text_for_vector: str,
        metadata: Optional[dict],
    ) -> None:
        self._messages.append(msg)
        self._turn_counter += 1
        self._maybe_summarize()
        self._trim_window()
        if self._vector and text_for_vector.strip():
            meta = dict(metadata or {})
            meta["turn"] = self._turn_counter
            self._vector.add([text_for_vector], metadatas=[meta])

    def _maybe_summarize(self) -> None:
        texts = self._window_texts()
        total = self._count_tokens(texts)
        if total < self._cfg.summarize_trigger_tokens:
            return
        # Collapse oldest half into summary; keeps latency predictable.
        half = max(1, len(self._messages) // 2)
        old = self._messages[:half]
        self._messages = self._messages[half:]
        transcript = "\n".join(
            f"{'U' if isinstance(m, HumanMessage) else 'A'}: {m.content}" for m in old
        )
        prompt = (
            "Compress the following chat turns into a concise factual summary. "
            "Preserve names, decisions, and open questions. Max ~400 words.\n\n"
            + transcript
        )
        try:
            resp = self._llm.invoke([HumanMessage(content=prompt)])
            chunk = str(resp.content).strip()
            self._summary = (self._summary + "\n" + chunk).strip()[-12_000:]
        except Exception as e:
            logger.warning("summarization failed, dropping old turns anyway: %s", e)

    def _trim_window(self) -> None:
        while self._messages:
            texts = self._window_texts()
            if self._count_tokens(texts) <= self._cfg.max_tokens_window:
                break
            self._messages.pop(0)

    def build_context(self, query: str) -> List[BaseMessage]:
        recalled: List[BaseMessage] = []
        if self._vector and query.strip():
            try:
                hits = self._vector.query(query.strip(), k=self._cfg.recall_top_k)
                if hits:
                    lines = "\n".join(f"- ({score:.3f}) {t[:500]}" for t, score in hits)
                    recalled.append(
                        SystemMessage(
                            content="Relevant prior turns (vector recall):\n" + lines
                        )
                    )
            except Exception as e:
                logger.warning("vector recall failed: %s", e)
        if self._summary:
            recalled.insert(0, SystemMessage(content="Running summary:\n" + self._summary))
        return recalled + list(self._messages)

    @property
    def message_count(self) -> int:
        return len(self._messages)

    @property
    def running_summary_chars(self) -> int:
        return len(self._summary)
