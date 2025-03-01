# app/utils/feature_extraction.py
import re
from collections import Counter
from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar
from typing import Dict, List, Any, Optional, Set, Tuple, Union
import logging
from text_processor import TextProcessor
from skills_taxonomy import SkillTaxonomy

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FeatureExtractor:
    def __init__(self):
        self.text_processor = TextProcessor()
        self.skill_taxonomy = SkillTaxonomy()
    
    def extract_resume_skills(self, text: str, sections: Dict[str, str]) -> List[str]:
        """
        Extract all skills from resume text and sections
        
        Args:
            text: Full normalized resume text
            sections: Dictionary of resume sections
            
        Returns:
            List of unique skills found in the resume
        """
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
        # Normalize text for processing
        normalized_text = self.text_processor.normalize_text(resume_text)
        print("Normalized text: ", normalized_text)
        # If sections not provided, try to extract them
        if not sections:
            sections = self._extract_resume_sections(normalized_text)
        
        # Extract features
        work_experience_years = self._calculate_experience_years_from_resume(normalized_text)
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
    
        # Extract job sections
        sections = self._extract_job_sections(normalized_text)
        
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
        
        # Common section headers in resumes
        section_patterns = {
            'experience': r'(?:work\s+experience|professional\s+experience|employment|work\s+history)',
            'skills': r'(?:skills|technical\s+skills|core\s+competencies|expertise)',
            'projects': r'(?:projects|personal\s+projects|academic\s+projects)',
            'certifications': r'(?:certifications|certificates|accreditations)',
            'summary': r'(?:summary|profile|objective|about\s+me)'
        }
        
        # Find potential section starts
        section_matches = []
        for section, pattern in section_patterns.items():
            for match in re.finditer(rf"\b{pattern}\b.*?(?:\n|\r\n?)", text, re.IGNORECASE):
                section_matches.append((match.start(), section, match.group(0)))
        
        # Sort matches by position in text
        section_matches.sort()
        
        # Extract section contents
        for i, (start_pos, section_name, header) in enumerate(section_matches):
            # Determine end position (next section or end of text)
            end_pos = len(text)
            if i < len(section_matches) - 1:
                end_pos = section_matches[i+1][0]
            
            # Extract section content without the header
            header_end = start_pos + len(header)
            content = text[header_end:end_pos].strip()
            sections[section_name] = content
        
        return sections
    
    def _extract_job_sections(self, text: str) -> Dict[str, str]:
        """Extract main sections from job description"""
        sections = {}
        
        # Common section headers in job descriptions
        section_patterns = {
            'responsibilities': r'(?:responsibilities|duties|what\s+you\'ll\s+do|role\s+description|key\s+responsibilities|position\s+overview)',
            'requirements': r'(?:requirements|qualifications|what\s+you\'ll\s+need|what\s+we\'re\s+looking\s+for|minimum\s+qualifications|basic\s+qualifications)',
            'preferred': r'(?:preferred\s+qualifications|nice\s+to\s+have|preferred\s+skills|desired\s+skills|bonus\s+points)',
            'benefits': r'(?:benefits|what\s+we\s+offer|perks|compensation)',
            'company': r'(?:about\s+us|company\s+overview|who\s+we\s+are)'
        }
        
        # Find potential section starts
        section_matches = []
        for section, pattern in section_patterns.items():
            for match in re.finditer(rf"\b{pattern}\b.*?(?:\n|\r\n?)", text, re.IGNORECASE):
                section_matches.append((match.start(), section, match.group(0)))
        
        # Sort matches by position in text
        section_matches.sort()
        
        # Extract section contents
        for i, (start_pos, section_name, header) in enumerate(section_matches):
            # Determine end position (next section or end of text)
            end_pos = len(text)
            if i < len(section_matches) - 1:
                end_pos = section_matches[i+1][0]
            
            # Extract section content without the header
            header_end = start_pos + len(header)
            content = text[header_end:end_pos].strip()
            sections[section_name] = content
        
        return sections
    
    def _calculate_months_between(self, start_date: datetime, end_date: datetime) -> int:
        """Calculate number of months between two dates"""
        print(f"Calculating months between {start_date.strftime('%b %Y')} and {end_date.strftime('%b %Y')}")
        if not start_date or not end_date:
            return 0
        
        # Calculate years and months separately
        years = end_date.year - start_date.year
        months = end_date.month - start_date.month
        
        # Total months
        total_months = (years * 12) + months
        
        print(f"Calculating months between {start_date.strftime('%b %Y')} and {end_date.strftime('%b %Y')}: {total_months} months")
        return total_months
    
    def _parse_date_range(self, date_range: str) -> Tuple[datetime, datetime]:
        """Parse a date range string into start and end dates"""
        try:
            # Split into start and end dates
            start_str, end_str = re.split(r'\s*-\s*', date_range)
            
            # Handle 'present' case
            if 'present' in end_str.lower():
                end_date = datetime.now()
            else:
                # Parse end date (e.g., 'dec 2019')
                end_date = datetime.strptime(end_str.strip(), '%b %Y')
            
            # Parse start date (e.g., 'jan 2020')
            start_date = datetime.strptime(start_str.strip(), '%b %Y')
            
            return start_date, end_date
        
        except (ValueError, IndexError) as e:
            print(f"Date parsing error: {e} for range: {date_range}")
            return None, None
    
    def _calculate_experience_years_from_resume(self, text: str) -> float:
        """Calculate total years of professional experience from resume text"""
        print(f"\nAnalyzing experience text:\n{text}\n")  # Debug print
        
        # Convert text to lowercase for consistent matching
        text = text.lower()
        
        # Find all month-year combinations and "present"
        dates = re.findall(
            r'(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{4}|present',
            text
        )
        print(f"Found dates: {dates}")  # Debug print
        
        # Create date ranges, handling 'present' specially
        job_entries = []
        i = 0
        while i < len(dates):
            if i + 1 < len(dates):
                if 'present' in dates[i]:
                    i += 1
                    continue
                if 'present' in dates[i+1]:
                    job_entries.append(f"{dates[i]} - present")
                else:
                    job_entries.append(f"{dates[i]} - {dates[i+1]}")
            i += 1
        
        print(f"Final job entries: {job_entries}")  # Debug print
        
        total_months = 0
        for date_range in job_entries:
            start_date, end_date = self._parse_date_range(date_range)
            if start_date and end_date:
                months = self._calculate_months_between(start_date, end_date)
                print(f"Calculated {months} months for range: {date_range}")  # Debug print
                total_months += months
        
        # Convert to years (rounded to 1 decimal place)
        years = round(total_months / 12, 1)
        print(f"Total years calculated: {years}")  # Debug print
        return years
    
    def _extract_required_experience(self, text: str) -> Optional[float]:
        """Extract required years of experience from job description"""
        # Match patterns for experience requirements
        experience_patterns = [
            # General experience
            r'(\d+)\+?\s*(?:-|\s*to\s*)?\s*(\d*)\s*(?:years|yrs)(?:\s*of)?(?:\s*experience)?',
            r'experience(?:\s*of)?\s*(\d+)\+?\s*(?:-|\s*to\s*)?\s*(\d*)\s*(?:years|yrs)',
            r'(?:with|having)\s*(\d+)\+?\s*(?:-|\s*to\s*)?\s*(\d*)\s*(?:years|yrs)(?:\s*of)?(?:\s*experience)?',
            r'(?:minimum|at\s+least)\s*(\d+)\+?\s*(?:years|yrs)'
        ]
        
        for pattern in experience_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            experience_values = []
            
            for match in matches:
                groups = match.groups()
                if len(groups) >= 1 and groups[0]:
                    # Handle "X+" format (minimum)
                    if '+' in groups[0]:
                        value = float(groups[0].replace('+', ''))
                        experience_values.append(value)
                    # Handle range "X-Y" or "X to Y"
                    elif len(groups) >= 2 and groups[1] and groups[1].isdigit():
                        min_value = float(groups[0])
                        max_value = float(groups[1])
                        # Use average of range
                        experience_values.append((min_value + max_value) / 2)
                    else:
                        experience_values.append(float(groups[0]))
            
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
    # Initialize with mock implementations for testing
    
    # Create feature extractor
    extractor = FeatureExtractor()
    
    # Example resume text
    resume_text = """
    PROFESSIONAL EXPERIENCE
    
    Senior Software Engineer | TechCorp | Jan 2023 - Present
    - Led development of microservices using Python, Django, and FastAPI
    - Implemented CI/CD pipelines using Docker and Kubernetes
    - Managed PostgreSQL databases and Redis caching
    
    Software Engineer | StartupCo | Dec 2018 - Dec 2019
    - Developed React.js frontend applications
    - Built RESTful APIs using Node.js and Express
    - Worked with MongoDB and AWS services
    
    EDUCATION
    
    Bachelor of Science in Computer Science
    University of Technology | 2014 - 2018
    
    SKILLS
    
    Languages: Python, JavaScript, TypeScript
    Frameworks: Django, FastAPI, React, Node.js
    Databases: PostgreSQL, MongoDB, Redis
    Cloud: AWS, Docker, Kubernetes
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
    print("\nSkills:", job_features["skills"])  # Now shows all skills together
    print("\nWord Frequencies (top 10):", dict(list(job_features["word_frequencies"].items())[:10]))