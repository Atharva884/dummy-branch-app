import os

class Config:
    FLASK_ENV: str = os.getenv("FLASK_ENV", "development")
    PORT: int = int(os.getenv("PORT", "8000"))

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@db:5432/microloans",
    )

    SQLALCHEMY_DATABASE_URI: str = DATABASE_URL

    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
