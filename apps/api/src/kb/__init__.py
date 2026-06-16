"""Regulatory knowledge base — ingestion and retrieval.

Gathers and structures regulatory sources, embeds them, and serves grounded retrieval to the
compliance agent. Embeddings live in the same Postgres via pgvector. See
docs/06-regulatory-knowledge-base.md.
"""
