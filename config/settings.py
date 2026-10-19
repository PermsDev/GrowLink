import os

from dotenv import load_dotenv

load_dotenv()

OWNER_ID = int(os.getenv("OWNER_ID", "0"))