import asyncio
import json
from typing import Dict
import tiktoken
import openai
import os

openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def parse_resume_with_ai(resume_text: str) -> Dict:
    """Use OpenAI to parse resume text into structured format"""
    try:
        # Generate system prompt for consistent parsing
        system_prompt = """
        You are an AI resume parser that extracts structured information from resumes.
        Extract the following sections:
        1. Skills (as a list of individual skills)
        2. Experience (including company, title, dates, location, and description)
        3. Education (including institution, degree, field, dates, and location)
        4. Projects (including name, technologies used, and description)
        
        Return the data in valid JSON format with these exact keys: 
        {
            "skills": ["skill1", "skill2", ...],
            "experience": [{"company": "", "title": "", "date": "", "location": "", "description": ""}],
            "education": [{"institution": "", "degree": "", "field": "", "date": "", "location": "", "gpa": ""}],
            "projects": [{"name": "", "technologies": [], "description": ""}]
        }
        """
        
        # Estimate token count to avoid exceeding model limits
        enc = tiktoken.get_encoding("cl100k_base")
        tokens = len(enc.encode(resume_text))
        
        # Truncate if necessary (leaving room for response and prompt)
        max_tokens = 16000 - 2000  # Leaving room for system prompt and response
        if tokens > max_tokens:
            encoded_text = enc.encode(resume_text)[:max_tokens]
            resume_text = enc.decode(encoded_text)
            
        response = await asyncio.to_thread(
            openai_client.chat.completions.create,
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Parse this resume:\n\n{resume_text}"}
            ]
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
    
    except Exception as e:
        print(f"Error parsing resume with AI: {str(e)}")
        # Return empty structure if parsing fails
        return {
            "skills": [],
            "experience": [],
            "education": [],
            "projects": []
        }