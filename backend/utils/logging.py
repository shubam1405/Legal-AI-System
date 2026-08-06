"""
Structured logger for the Legal AI System.
Outputs JSON-style log lines for easy parsing by log aggregators.
"""
from __future__ import annotations

import json
import logging
import sys
import time
from datetime import datetime, timezone
from typing import Any

__all__ = [
    "get_logger",
    "log_node_execution",
    "log_retrieval",
    "log_token_usage",
]

_LOG_FORMAT = "%(message)s"  # All formatting done in JSON payload


def get_logger(name: str) -> logging.Logger:
    """
    Return a structured logger.

    Args:
        name: Logger name (typically __name__ of the calling module).

    Returns:
        Configured Logger that emits JSON lines to stdout.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(_LOG_FORMAT))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger


def _emit(logger: logging.Logger, level: str, payload: dict[str, Any]) -> None:
    """Emit a JSON log line with a timestamp."""
    payload["timestamp"] = datetime.now(timezone.utc).isoformat()
    payload["level"] = level
    line = json.dumps(payload, ensure_ascii=False, default=str)
    getattr(logger, level.lower(), logger.info)(line)


def log_node_execution(
    logger: logging.Logger,
    *,
    node_name: str,
    conversation_id: str,
    duration_ms: float,
    success: bool,
    error: str | None = None,
) -> None:
    """
    Log the execution result of a LangGraph node.

    Args:
        logger: Logger instance.
        node_name: Name of the node (e.g. 'chatbot_node').
        conversation_id: Current conversation / thread ID.
        duration_ms: Wall-clock execution time in milliseconds.
        success: True if node completed without error.
        error: Error message string if success is False.
    """
    payload: dict[str, Any] = {
        "event": "node_execution",
        "node": node_name,
        "conversation_id": conversation_id,
        "duration_ms": round(duration_ms, 2),
        "success": success,
    }
    if error:
        payload["error"] = error
    _emit(logger, "ERROR" if not success else "INFO", payload)


def log_retrieval(
    logger: logging.Logger,
    *,
    collection: str,
    query: str,
    results_count: int,
    latency_ms: float,
) -> None:
    """
    Log a ChromaDB retrieval operation.

    Args:
        logger: Logger instance.
        collection: ChromaDB collection name queried.
        query: The search query string.
        results_count: Number of chunks returned.
        latency_ms: Time taken for the retrieval in milliseconds.
    """
    _emit(logger, "INFO", {
        "event": "rag_retrieval",
        "collection": collection,
        "query_preview": query[:100],
        "results_count": results_count,
        "latency_ms": round(latency_ms, 2),
    })


def log_token_usage(
    logger: logging.Logger,
    *,
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> None:
    """
    Log Gemini token usage for cost tracking.

    Args:
        logger: Logger instance.
        model: Gemini model identifier used.
        input_tokens: Number of prompt tokens consumed.
        output_tokens: Number of completion tokens generated.
    """
    _emit(logger, "INFO", {
        "event": "token_usage",
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
    })


class NodeTimer:
    """Context manager for timing node execution."""

    def __init__(self) -> None:
        self._start: float = 0.0

    def __enter__(self) -> "NodeTimer":
        self._start = time.perf_counter()
        return self

    def __exit__(self, *_: Any) -> None:
        pass

    @property
    def elapsed_ms(self) -> float:
        return (time.perf_counter() - self._start) * 1000
