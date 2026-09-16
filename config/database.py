import os

import psycopg2
from dotenv import load_dotenv


# Load variables from .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    """
    Create and return a PostgreSQL connection
    using the Supabase DATABASE_URL.
    """

    if not DATABASE_URL:
        raise ValueError(
            "DATABASE_URL is not configured. "
            "Check your .env file."
        )

    return psycopg2.connect(DATABASE_URL)
