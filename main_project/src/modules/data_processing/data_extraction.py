import re
import spacy
# import pandas as pd
from typing import Dict, Any

# Load the spacy model
nlp=spacy.load("en_core_web_sm")

def extract_job_sections(job_description: str) -> Dict[str, Any]:
    """
    Extracts structured sections (responsibilities, qualifications, skills, etc.) from a job description.
    Uses regex and NLP-based pattern detection to dynamically extract key details.
    """
    
    sections = {
        "company": None,
        "responsibilities": [],
        "qualifications": [],
        "technical_skills": [],
        "preferred_qualifications": []
    }
    
    # Define section headers
    responsibilities_headers = ["Duties", "Responsibilities", "Key Responsibilities", "Position Overview", "What You Will Do"]
    qualifications_headers = ["Requirements", "Qualifications", "Skills", "Required Skills", "Experience", "Who You Are"]
    preferred_headers = ["Preferred Qualifications", "Preferred Skills", "Nice to Have"]
    technical_skills_keywords = [
        # Frontend
        "React", "Vue", "Angular", "JavaScript", "TypeScript", "HTML", "CSS", "SASS", "jQuery", "Redux", 
        "Next.js", "Webpack", "Babel", "Bootstrap", "Tailwind", "Material UI",
        
        # Backend
        "Python", "Java", "C#", ".NET", "Node.js", "Express", "Django", "Flask", "Spring Boot", 
        "Ruby", "Rails", "PHP", "Laravel", "Go", "Rust", "Kotlin", "Swift", "Spring", "C++", "Linux"
        
        # Database
        "SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis", "Oracle", "DynamoDB", "Cassandra", 
        "GraphQL", "ElasticSearch", "Firebase", "NoSQL", "GraphQL", 
        
        # Cloud & DevOps
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Jenkins", "GitLab CI", "GitHub Actions",
        "Terraform", "Ansible", "ECS", "Lambda", "S3", "EC2", "Serverless", 
        
        # Testing
        "Jest", "Mocha", "Selenium", "Cypress", "JUnit", "PyTest", "TestNG",
        
        # Tools & Version Control
        "Git", "GitHub", "BitBucket", "JIRA", "Confluence", "Swagger", "Postman",
        
        # Architecture & Patterns
        "Microservices", "REST API", "gRPC", "WebSocket", "OAuth", "JWT", "MVC",
        
        # AI & ML
        "Machine Learning", "TensorFlow", "PyTorch", "NLP", "Computer Vision", "Deep Learning", "ML", "AI"
        
        # Mobile
        "iOS", "Android", "React Native", "Flutter", "Swift", "Kotlin",
        
        # Other
        "Agile", "Scrum", "CI/CD", "Linux", "Unix", "Bash", "Shell Scripting", "Kafka", "RabbitMQ", "Nginx",
        
    ]
    
    current_section = None
    
    for line in job_description.split('\n'):
        line = line.strip()
        if not line:
            continue
        
        # Detect sections
        if any(header in line for header in responsibilities_headers):
            current_section = "responsibilities"
            continue
        elif any(header in line for header in qualifications_headers):
            current_section = "qualifications"
            continue
        elif any(header in line for header in preferred_headers):
            current_section = "preferred_qualifications"
            continue
        
        # Add content to the detected section
        if current_section:
            items = [item.strip() for item in re.split(r'[-•]', line) if item.strip()]
            for item in items:
                if item and not item.endswith(':'):
                    sections[current_section].append(item)
    
    # Clean up the lists by removing duplicates
    for key in ["responsibilities", "qualifications", "technical_skills", "preferred_qualifications"]:
        if sections[key]:
            sections[key] = list(dict.fromkeys(filter(None, sections[key])))
    
    # Use NLP (SpaCy) for entity recognition to extract company name
    doc = nlp(job_description)
    
    # Look for explicit "Company: ..." pattern first
    company_match = re.search(r'Company: ([\w\s&.-]+)', job_description)
    if company_match:
        sections["company"] = company_match.group(1).strip()
    else:
        for ent in doc.ents:
            if ent.label_ == "ORG" and ent.text not in {"NYSE", "Develop"}:  # Exclude incorrect names
                sections["company"] = ent.text
                break  # Take the first relevant match
    
    # Extract technical skills from qualifications and responsibilities
    extracted_skills = set()
    for section in ["qualifications", "responsibilities"]:
        for sentence in sections[section]:
            for skill in technical_skills_keywords:
                if skill.lower() in sentence.lower():
                    extracted_skills.add(skill)
    
    sections["technical_skills"] = list(extracted_skills)
    
    return sections
    

    
    
    
