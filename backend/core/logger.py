from logtail import LogtailHandler
import logging 
import sys
import os
from dotenv import load_dotenv

load_dotenv()
betterstack_handler = LogtailHandler(
    source_token=os.getenv('BS_TOKEN'),
    host=os.getenv('BS_HOST')
)
logger = logging.getLogger('uvicorn.error')

formatter = logging.Formatter(
    fmt = "%(asctime)s - %(message)s",
)

stream_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler('app.log')

# set handlers to the logger


stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)
logger.addHandler(betterstack_handler)
