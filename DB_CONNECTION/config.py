import os
from sqlalchemy import create_engine, MetaData
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from .env
DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine and metadata
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

