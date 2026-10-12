import os


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://statistics:statistics@127.0.0.1:5434/statistics",
)