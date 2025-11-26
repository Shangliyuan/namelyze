"""
Configuration management using pydantic-settings
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file"""

    # OpenAI Compatible API Configuration
    openai_api_base: str = Field(
        default="https://api.openai.com/v1",
        description="Base URL for OpenAI compatible API"
    )
    openai_api_key: str = Field(
        ...,
        description="API key for authentication"
    )
    model_name: str = Field(
        default="gpt-4",
        description="Model name to use for inference"
    )

    # Processing Configuration
    batch_size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Number of names to process in each batch"
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum number of retries for API calls"
    )
    timeout: int = Field(
        default=60,
        ge=10,
        le=300,
        description="API request timeout in seconds"
    )

    # File Paths
    input_csv: str = Field(
        default="data/input/names.csv",
        description="Path to input CSV file"
    )
    output_csv: str = Field(
        default="data/output/results.csv",
        description="Path to output CSV file"
    )
    name_column: str = Field(
        default="name",
        description="Column name containing scholar names in input CSV"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


def load_settings() -> Settings:
    """Load and validate settings from environment"""
    return Settings()
