from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "SiteGuard AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "siteguard"
    
    SECRET_KEY: str = "siteguard-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    VLM_PROVIDER: str = "gemini"
    VLM_API_KEY: Optional[str] = None
    VLM_MODEL: Optional[str] = None
    VLM_TEMPERATURE: float = 0.1
    VLM_MAX_TOKENS: int = 1200
    
    UPLOAD_DIR: str = "/app/uploads"
    MAX_FILE_SIZE_MB: int = 15
    ALLOWED_EXTENSIONS: list = [".jpg", ".jpeg", ".png", ".webp"]
    MAX_IMAGE_DIM: int = 1280
    
    ETHICAL_DISCLAIMER: str = (
        "SiteGuard AI provides automated observations for human safety inspector review. "
        "All alerts are POTENTIAL concerns and must be verified by a qualified human "
        "inspector on-site. This system does NOT confirm violations, does NOT identify "
        "individual workers, and must NOT be used for automated disciplinary action. "
        "Construction safety decisions require on-site human judgment and are subject "
        "to applicable workplace safety regulations."
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
