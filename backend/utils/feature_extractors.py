import re
from collections import Counter
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple, Union
import logging
from backend.utils.text_processor import TextProcessor
from backend.utils.skills_taxonomy import SkillTaxonomy

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FeatureExtractor:
    def __init__(self):
        self.text_processor = TextProcessor()
        self.skill_taxonomy = SkillTaxonomy()
    
    def extract_resume_skills(self, text: str, sections: Dict[str, str]) -> List[str]:
        """Extract all skills from resume text and sections"""
        all_skills = set()
        
        # First try to extract from dedicated skills section
        if 'skills' in sections and sections['skills']:
            skills_from_section = self.skill_taxonomy.extract_skills(sections['skills'])
            all_skills.update(skills_from_section)
        
        # Extract from each relevant section
        for section_name in ['experience', 'projects', 'certifications', 'summary']:
            if section_name in sections and sections[section_name]:
                section_skills = self.skill_taxonomy.extract_skills(sections[section_name])
                all_skills.update(section_skills)
        
        # Also scan full text to catch any missed skills
        full_text_skills = self.skill_taxonomy.extract_skills(text)
        all_skills.update(full_text_skills)
        
        # If we still didn't find skills, just use the full text
        if len(all_skills) == 0:
            all_skills.update(self.skill_taxonomy.extract_skills(text))
    
        return list(all_skills)
    
    def extract_job_skills(self, text: str, sections: Dict[str, str]) -> List[str]:
        """Extract all skills (required + preferred) from job description"""
        all_skills = set()
        
        # Check requirements section
        if 'requirements' in sections and sections['requirements']:
            req_skills = self.skill_taxonomy.extract_skills(sections['requirements'])
            all_skills.update(req_skills)
        
        # Check responsibilities section
        if 'responsibilities' in sections and sections['responsibilities']:
            resp_skills = self.skill_taxonomy.extract_skills(sections['responsibilities'])
            all_skills.update(resp_skills)
        
        # Check preferred section
        if 'preferred' in sections and sections['preferred']:
            pref_skills = self.skill_taxonomy.extract_skills(sections['preferred'])
            all_skills.update(pref_skills)
        
        # If no sections found, scan full text
        if len(all_skills) < 3 or not sections:
            all_skills.update(self.skill_taxonomy.extract_skills(text))
        
        return list(all_skills)
    
    def extract_resume_features(self, resume_text: str, sections: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Extract standardized features from resume text"""
        # Important: Work with the original text for section extraction
        # Normalize text for processing
        normalized_text = self.text_processor.normalize_text(resume_text)
        print("Normalized text length: ", len(normalized_text))
        
        # If sections not provided, try to extract them from the ORIGINAL text
        if not sections:
            sections = self._extract_resume_sections(resume_text)  # Use original text with capitalization
        
        print("Sections found: ", list(sections.keys()))
        
        # Extract work_experience_years from experience section only, not from education
        work_experience_years = 0
        if 'experience' in sections and sections['experience']:
            work_experience_years = self._calculate_experience_years_from_resume(sections['experience'])
            print(f"Experience years calculated from 'experience' section: {work_experience_years}")
        else:
            # Fallback: Try to find the substring between "WORK EXPERIENCE" and "PROJECTS" or end of text
            work_exp_match = re.search(r'WORK\s+EXPERIENCE(.*?)(?:PROJECTS|TECHNICAL\s+SKILLS|$)', resume_text, re.DOTALL | re.IGNORECASE)
            if work_exp_match:
                experience_text = work_exp_match.group(1).strip()
                work_experience_years = self._calculate_experience_years_from_resume(experience_text)
                print(f"Experience years calculated from extracted 'WORK EXPERIENCE' section: {work_experience_years}")
                # Add this to sections
                sections['experience'] = experience_text
        
        skills = self.extract_resume_skills(normalized_text, sections)
        word_frequencies = self._extract_word_frequencies(normalized_text)
        
        return {
            "work_experience_years": work_experience_years,
            "skills": skills,
            "word_frequencies": word_frequencies
        }
    
    def extract_job_features(self, job_text: str) -> Dict[str, Any]:
        """Extract standardized features from job description"""
        # Normalize text
        normalized_text = self.text_processor.normalize_text(job_text)
    
        # Extract job sections from original text
        sections = self._extract_job_sections(job_text)  # Use original for better section detection
        
        # Extract features
        required_experience_years = self._extract_required_experience(normalized_text)
        skills = self.extract_job_skills(normalized_text, sections)
        word_frequencies = self._extract_word_frequencies(normalized_text)
        
        return {
            "required_experience_years": required_experience_years,
            "skills": skills,  # Combined required and preferred skills
            "word_frequencies": word_frequencies
        }
    
    def _extract_resume_sections(self, text: str) -> Dict[str, str]:
        """Extract main sections from resume text"""
        sections = {}
        
        # Common section headers in resumes - using uppercase since many resumes have section headers in caps
        section_patterns = {
            'experience': r'(?:WORK\s+EXPERIENCE|PROFESSIONAL\s+EXPERIENCE|EMPLOYMENT|WORK\s+HISTORY)',
            'education': r'(?:EDUCATION|ACADEMIC\s+BACKGROUND|ACADEMIC\s+HISTORY)',
            'skills': r'(?:TECHNICAL\s+SKILLS|SKILLS|CORE\s+COMPETENCIES|EXPERTISE)',
            'projects': r'(?:PROJECTS|PERSONAL\s+PROJECTS|ACADEMIC\s+PROJECTS)',
            'certifications': r'(?:CERTIFICATIONS|CERTIFICATES|ACCREDITATIONS)',
            'summary': r'(?:SUMMARY|PROFILE|OBJECTIVE|ABOUT\s+ME)'
        }
        
        # Find each section header in the document
        section_positions = []
        for section_name, pattern in section_patterns.items():
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            for match in matches:
                section_positions.append((match.start(), section_name))
        
        # Sort positions to determine section boundaries
        section_positions.sort()
        
        # Extract content between consecutive section headers
        for i, (start_pos, section_name) in enumerate(section_positions):
            # Find the end of the header line
            header_end = text.find('\n', start_pos)
            if header_end == -1:  # If no newline found, use the entire rest of the document
                header_end = len(text)
            
            # Determine section end (start of next section or end of text)
            section_end = len(text)
            if i < len(section_positions) - 1:
                section_end = section_positions[i + 1][0]
            
            # Extract content
            content = text[header_end:section_end].strip()
            sections[section_name] = content
        
        return sections
    
    def _extract_job_sections(self, text: str) -> Dict[str, str]:
        """Extract main sections from job description"""
        sections = {}
        
        # Common section headers in job descriptions
        section_patterns = {
            'responsibilities': r'(?:Responsibilities|Duties|What\s+You\'ll\s+Do|Role\s+Description|Key\s+Responsibilities)',
            'requirements': r'(?:Requirements|Qualifications|What\s+You\'ll\s+Need|What\s+We\'re\s+Looking\s+For)',
            'preferred': r'(?:Preferred\s+Qualifications|Nice\s+to\s+Have|Preferred\s+Skills|Desired\s+Skills)',
            'benefits': r'(?:Benefits|What\s+We\s+Offer|Perks|Compensation)',
            'company': r'(?:About\s+Us|Company\s+Overview|Who\s+We\s+Are)'
        }
        
        # Find each section header in the document
        section_positions = []
        for section_name, pattern in section_patterns.items():
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            for match in matches:
                section_positions.append((match.start(), section_name))
        
        # Sort positions to determine section boundaries
        section_positions.sort()
        
        # Extract content between consecutive section headers
        for i, (start_pos, section_name) in enumerate(section_positions):
            # Find the end of the header line
            header_end = text.find('\n', start_pos)
            if header_end == -1:  # If no newline found, use the entire rest of the document
                header_end = len(text)
            
            # Determine section end (start of next section or end of text)
            section_end = len(text)
            if i < len(section_positions) - 1:
                section_end = section_positions[i + 1][0]
            
            # Extract content
            content = text[header_end:section_end].strip()
            sections[section_name] = content
        
        return sections
    
    def _calculate_months_between(self, start_date: datetime, end_date: datetime) -> int:
        """Calculate number of months between two dates"""
        if not start_date or not end_date:
            return 0
        
        # Ensure end_date is not before start_date
        if end_date < start_date:
            print(f"Warning: End date {end_date} is before start date {start_date}. Swapping dates.")
            start_date, end_date = end_date, start_date
        
        # Calculate years and months separately
        years = end_date.year - start_date.year
        months = end_date.month - start_date.month
        
        # Total months
        total_months = (years * 12) + months
        
        print(f"Calculating months between {start_date.strftime('%b %Y')} and {end_date.strftime('%b %Y')}: {total_months} months")
        return max(0, total_months)  # Ensure we don't return negative months
    
    def _parse_date_range(self, date_range: str) -> Tuple[Optional[datetime], Optional[datetime]]:
        """Parse a date range string into start and end dates"""
        try:
            # Split into start and end dates
            parts = re.split(r'\s*[–\-]\s*', date_range)  # Handle both hyphen and en-dash
            
            if len(parts) != 2:
                print(f"Invalid date range format: {date_range}")
                return None, None
            
            start_str, end_str = parts
            
            # Handle 'present' case
            if 'present' in end_str.lower():
                end_date = datetime.now()
            else:
                # Parse end date
                try:
                    end_date = datetime.strptime(end_str.strip(), '%b %Y')
                except ValueError:
                    print(f"Could not parse end date: {end_str}")
                    return None, None
            
            # Parse start date
            try:
                start_date = datetime.strptime(start_str.strip(), '%b %Y')
            except ValueError:
                print(f"Could not parse start date: {start_str}")
                return None, None
            
            return start_date, end_date
            
        except Exception as e:
            print(f"Date parsing error: {e} for range: {date_range}")
            return None, None
    
    def _calculate_experience_years_from_resume(self, text: str) -> float:
        """Calculate total years of professional experience from resume text"""
        
        # Preprocess text: normalize and lowercase
        text = text.lower()
        
        # Identify job positions (these often have dates associated with them)
        # Look for date patterns in format "Month Year - Month Year" or "Month Year - Present"
        job_entries = []
        
        # Find all "Month Year - Month Year" or "Month Year - Present" patterns
        date_patterns = [
            r'(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{4}\s*[–\-]\s*(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{4}',
            r'(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{4}\s*[–\-]\s*present'
        ]
        
        for pattern in date_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                job_entries.append(match.group(0))
        
        print(f"Found job date ranges: {job_entries}")
        
        # If no clear date ranges found, try to find individual dates and construct ranges
        if not job_entries:
            dates = re.findall(
                r'(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{4}|present',
                text, re.IGNORECASE
            )
            print(f"Found individual dates: {dates}")
            
            # Work experience typically lists recent experience first
            # So we need to be careful about pairing dates: each date might be start or end
            # We'll look for context clues to determine if date is a start or end date
            
            # Extract positions with dates
            position_blocks = re.findall(
                r'([^\n]+?(?:engineer|developer|analyst|manager|intern|specialist|consultant|director)[^\n]*?)' +
                r'([^\n]*?(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{4}[^\n]*)', 
                text, re.IGNORECASE
            )
            
            print(f"Found position blocks: {position_blocks}")
            
            # Process position blocks to extract date ranges
            for i in range(len(position_blocks)):
                block_text = position_blocks[i][0] + ' ' + position_blocks[i][1]
                block_dates = re.findall(
                    r'(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{4}|present',
                    block_text, re.IGNORECASE
                )
                
                if len(block_dates) >= 2:
                    job_entries.append(f"{block_dates[0]} - {block_dates[1]}")
                elif len(block_dates) == 1 and 'present' in block_text.lower():
                    job_entries.append(f"{block_dates[0]} - present")
        
        print(f"Final job entries: {job_entries}")
        
        # Calculate total experience
        total_months = 0
        for date_range in job_entries:
            start_date, end_date = self._parse_date_range(date_range)
            if start_date and end_date:
                months = self._calculate_months_between(start_date, end_date)
                print(f"Calculated {months} months for range: {date_range}")
                if months > 0:  # Only add positive month values
                    total_months += months
        
        # Convert to years (rounded to 1 decimal place)
        years = round(total_months / 12, 1)
        print(f"Total years calculated: {years}")
        return max(0, years)  # Ensure non-negative result
    
    def _extract_required_experience(self, text: str) -> Optional[float]:
        """Extract required years of experience from job description"""
        # Match patterns for experience requirements
        experience_patterns = [
            # General experience
            r'(\d+)(?:\+|\s*\+)?\s*(?:-|\s*to\s*)?\s*(\d*)\s*(?:years|yrs)(?:\s*of)?(?:\s*experience)?',
            r'experience(?:\s*of)?\s*(\d+)(?:\+|\s*\+)?\s*(?:-|\s*to\s*)?\s*(\d*)\s*(?:years|yrs)',
            r'(?:with|having)\s*(\d+)(?:\+|\s*\+)?\s*(?:-|\s*to\s*)?\s*(\d*)\s*(?:years|yrs)(?:\s*of)?(?:\s*experience)?',
            r'(?:minimum|at\s+least)\s*(\d+)(?:\+|\s*\+)?\s*(?:years|yrs)'
        ]
        
        for pattern in experience_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            experience_values = []
            
            for match in matches:
                groups = match.groups()
                if len(groups) >= 1 and groups[0]:
                    # Handle "X+" format (minimum)
                    value_str = groups[0]
                    if '+' in value_str:
                        value_str = value_str.replace('+', '')
                    
                    try:
                        min_value = float(value_str)
                        
                        # Handle range "X-Y" or "X to Y"
                        if len(groups) >= 2 and groups[1] and groups[1].strip().isdigit():
                            max_value = float(groups[1])
                            # Use average of range
                            experience_values.append((min_value + max_value) / 2)
                        else:
                            experience_values.append(min_value)
                    except ValueError:
                        print(f"Could not parse experience value: {value_str}")
            
            if experience_values:
                # Return the median experience value to avoid outliers
                experience_values.sort()
                if len(experience_values) % 2 == 0:
                    return (experience_values[len(experience_values)//2 - 1] + 
                            experience_values[len(experience_values)//2]) / 2
                else:
                    return experience_values[len(experience_values)//2]
        
        # Check for entry-level indicators if no specific experience mentioned
        entry_level_patterns = [
            r'entry[- ]level',
            r'junior',
            r'no experience required',
            r'0-1 years',
            r'recent graduate'
        ]
        
        for pattern in entry_level_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return 0.0
        
        # Default to None if no experience requirements found
        return None
    
    def _extract_word_frequencies(self, text: str) -> Dict[str, int]:
        """Extract word frequencies for contextual matching"""
        # Tokenize and process text
        tokens = self.text_processor.preprocess(text, lemmatize=True)
        
        # Count word frequencies
        word_counts = Counter(tokens)
        
        # Return top 100 most frequent words
        return dict(word_counts.most_common(100))

# Example usage
if __name__ == "__main__":
    # Create feature extractor
    extractor = FeatureExtractor()
    
    # Example resume text
    resume_text = """
    IAN(HSINYEN ) WU
Chicago, IL
♂phone(469) 497-7719 /envel⌢pewu.hsin@northeastern.edu /linkedinlinkedin.com/in/ianwu0915 /gl⌢beianwu.netlify.app
EDUCATION
Northeastern University Sep 2022 – May 2025
Master of Science in Computer Science, GPA: 3.73/4.0 Boston, MA
•Courses: Algorithm, Object-Oriented Design, Cloud Computing, Computer Networking, Mobile Development,
Database Design, Web Development, Machine Learning
WORK EXPERIENCE
Stealth Startup Oct 2024 – Present
Software Engineer Intern Chicago, IL
•Parallelized 1,000+ high-frequency trading simulations , by redesigning monolithic task scheduling system into a
distributed, cloud-native platform using Rust.
•Designed fault-tolerant master-worker architecture for asynchronous task communication using NATS JetStream,
Kubernetes, and AWS S3 storage.
•Ensuring system resilience and continuous operation through leader election with etcd for master node.
AI Roboto Edu May 2024 – Oct 2024
Full Stack Engineer Intern Los Angeles, CA
•Developed a full-stack solution for an online education startup using Spring Boot, MySQL, React, and Redux.
•Optimized backend APIs, cutting response time by 20% through MySQL query optimization, caching, and
efficient data handling.
•Improved responsiveness and reducing TTI by 15% by implementing asynchronous Redux state management.
•Automated development workflows with Bash scripts, accelerating release cycles and enhancing team efficiency.
PROJECTS
AI Job Search & Match platform (Python |Open AI |FastAPI) /github
•Developed an AI-driven job matching system using OpenAI embeddings and FAISS, improving match accuracy by
40% through vectorized resume-to-job comparison.
•Reduced job processing time by 70% , using multi-threading and Redis caching to eliminate redundant API calls.
•Automated job data processing and structured storage by designing scalable ETL pipeline with FastAPI, Redis,
and PostgreSQL.
High-Performance E-Commerce Platform (Java |Spring Cloud |AWS) /github
•Architected scalable microservices e-commerce platform using Spring Cloud, AWS RDS, API Gateway and MySQL,
delivering end-to-end user journeys from product discovery to checkout completion.
•Improved system throughput by 40%, handling 1,200 messages per second with load balancing and
asynchronous processing using Kafka.
•Reduced shopping cart query latency by 87.5% (from 800ms to 100ms) using Redis for high-concurrency
caching.
Distributed KV Storage System (Java |Distributed System) /github
•Achieved 14,000 QPS for mixed read/write workloads and a P99 latency of 200ms , by developing a distributed
Key-Value store using Java.
•Ensured strong consistency with dynamic leader election and log replication , by implementing Raft consensus
algorithm.
•Improve stability by reducing master-switching frequency , using Prevote optimization technique.
TECHNICAL SKILLS
Programming Languages: Java, Python, Rust, SQL, Shell, HTML/CSS, JavaScript, TypeScript
Frameworks: Spring Boot, Spring Cloud, React.js, Next.js, Express.js, FastAPI, Redux
Databases: MySQL, PostgreSQL, Redis, MongoDB, etcd
System & Cloud: Linux, AWS, GCP , Kubernetes, Git
Others: Nginx, Kafka, Agile Development
    """
    
    # Example job description
    job_text = """
    Senior Software Engineer
    
    Requirements:
    - 5+ years of experience in software development
    - Strong proficiency in Python and JavaScript
    - Experience with Django or similar web frameworks
    - Knowledge of containerization (Docker, Kubernetes)
    - Experience with PostgreSQL and NoSQL databases
    
    Nice to have:
    - Experience with React.js
    - AWS cloud services
    - CI/CD implementation
    
    Education:
    Bachelor's degree in Computer Science or related field
    """
    
    # Extract features from resume
    print("\nExtracting Resume Features:")
    resume_features = extractor.extract_resume_features(resume_text)
    print("\nWork Experience Years:", resume_features["work_experience_years"])
    print("\nSkills:", resume_features["skills"])
    print("\nWord Frequencies (top 10):", dict(list(resume_features["word_frequencies"].items())[:10]))
    
    # Extract features from job description
    print("\nExtracting Job Features:")
    job_features = extractor.extract_job_features(job_text)
    print("\nRequired Experience:", job_features["required_experience_years"])
    print("\nSkills:", job_features["skills"])
    print("\nWord Frequencies (top 10):", dict(list(job_features["word_frequencies"].items())[:10]))