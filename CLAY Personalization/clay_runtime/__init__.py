"""CLAY Personalization deterministic reference runtime.

This package composes validated task contracts and renders adapter instructions.
It does not parse natural language, call an LLM, authorize external actions, or persist profiles.
"""
from .engine import ClayRuntime, RuntimeResult
from .config import load_config
__all__ = ["ClayRuntime", "RuntimeResult", "load_config"]
