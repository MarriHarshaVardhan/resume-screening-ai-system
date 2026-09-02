from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Resume Upload Settings
    UPLOAD_DIRECTORY: str = "uploads"
    MAX_RESUME_FILE_SIZE: int = 10485760  # 10 MB

    # AI Model Settings
    GROQ_API_KEY: str
    #GROQ_MODEL: str = "llama3-70b-8192"
    GROQ_MODEL: str = "openai/gpt-oss-20b"


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
