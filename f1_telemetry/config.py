"""Configure env vars."""
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

F1_UDP_SERVER_ADDRESS = str(os.environ.get("F1_UDP_SERVER_ADDRESS", "0.0.0.0"))
F1_UDP_SERVER_PORT = int(os.environ.get("F1_UDP_SERVER_PORT", 20777))
