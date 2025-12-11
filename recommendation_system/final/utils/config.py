"""
Configuration management for the recommendation system.
"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    app_name: str = "Recommendation System API"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Paths
    base_dir: Path = Path(__file__).parent.parent
    data_dir: Path = base_dir / "data"
    models_dir: Path = base_dir / "trained_models"
    logs_dir: Path = base_dir / "logs"
    static_dir: Path = base_dir / "static"
    
    # Model paths
    customer_model_path: Path = base_dir / "trained_models" / "customer_recommender.pkl"
    owner_model_path: Path = base_dir / "trained_models" / "owner_recommender.pkl"
    
    # Model parameters
    customer_top_k_default: int = 5
    owner_top_k_default: int = 5
    lightfm_epochs: int = 30
    lightfm_num_threads: int = 4
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def ensure_directories():
    """Ensure all required directories exist."""
    directories = [
        settings.data_dir,
        settings.models_dir,
        settings.logs_dir,
        settings.static_dir,
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
