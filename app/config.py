# app/config.py
import os

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:////data/app.db")
    WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()


# to be edited