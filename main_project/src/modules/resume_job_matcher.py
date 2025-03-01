import json 
import numpy as np 
import faiss 
import openai 
import os 
from dotenv import load_dotenv 
from typing import List, Dict, Tuple, Any, Optional
from pathlib import Path 
import pandas as pd 
from data_processing.job_data_extraction import process_job_description
from backend.utils.lazy_module import LazyModule

# Lazy imports 
json = LazyModule("json")
openai = LazyModule("openai")
load_dotenv = LazyModule("dotenv").load_dotenv

# Load environment variables 
load_dotenv()

class ResumeJobMatcher:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = self.openai_api_key
