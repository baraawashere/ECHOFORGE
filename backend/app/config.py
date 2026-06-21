"""
Central settings object. Everything that could change between your machine
and someone else's (API keys, file paths, thresholds) lives here, not
scattered through the code.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    anthropic_api_key: str = ""
    groq_api_key: str = ""
    use_provider: str = "anthropic"  # "anthropic" or "groq"

    chroma_persist_dir: str = "./chroma_data"
    embedding_model_name: str = "all-MiniLM-L6-v2"

    # Cosine similarity cutoff for "this past mistake might share a root cause
    # with the new one". Start at 0.45 and tune after seeding real demo data —
    # this number is the single most important knob in the whole project.
    similarity_threshold: float = 0.45
    
    clusters_file: str = "./clusters.json"

    # How many past mistakes to pull back when checking for a pattern
    neighbor_search_k: int = 5

    class Config:
        env_file = ".env"


settings = Settings()
