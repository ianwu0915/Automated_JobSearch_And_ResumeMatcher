import re
import os
import PyPDF2
import docx2txt
from pprint import pprint

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
    return text

def extract_text_from_docx(docx_path):
    try:
        return docx2txt.process(docx_path)
    except Exception as e:
        print(f"Error extracting text from DOCX: {e}")
        return ""

def extract_text(file_path):
    if file_path.endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith('.docx'):
        return extract_text_from_docx(file_path)
    elif file_path.endswith('.txt'):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error reading text file: {e}")
            return ""
    else:
        return "Unsupported file format"

def extract_email(text):
    """Extract email from text"""
    # Email pattern
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z0-9-.]{2,}'
    
    matches = []
    for match in re.finditer(email_pattern, text):
        email = match.group(0)
        matches.append(email)
    
    # Prioritize .edu emails
    edu_emails = [e for e in matches if e.endswith('.edu')]
    if edu_emails:
        return edu_emails[0]
    
    # Then Gmail
    gmail_emails = [e for e in matches if '@gmail.com' in e]
    if gmail_emails:
        return gmail_emails[0]
    
    return matches[0] if matches else None

def extract_phone(text):
    """Extract phone number"""
    # Look for phone patterns with parentheses
    patterns = [
        r'\(\d{3}\)[-\s]?\d{3}[-\s]?\d{4}',  # (617)-372-4007
        r'\+\d{1,2}\s\(\d{3}\)\s\d{3}[-\s]?\d{4}',  # +1 (123) 456-7890
        r'\d{3}[-\s]?\d{3}[-\s]?\d{4}',  # 123-456-7890
    ]
    
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            return match.group(0)
    
    return None

def extract_linkedin(text):
    """Extract LinkedIn URL or handle"""
    # Check for various forms of LinkedIn URLs
    patterns = [
        r'linkedin\.com/in/[\w-]+',
        r'www\.linkedin\.com/in/[\w-]+'
    ]
    
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            return match.group(0)
    
    return None

def extract_website(text):
    """Extract personal website URL"""
    # Check for personal website
    patterns = [
        r'www\.([\w-]+)\.com',  # www.jazzcort.com 
        r'([\w-]+)\.netlify\.app',  # somename.netlify.app
        r'([\w-]+)\.github\.io',  # username.github.io
    ]
    
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            full_url = match.group(0)
            # Check if it's not LinkedIn or GitHub
            if "linkedin" not in full_url.lower() and "github" not in full_url.lower():
                return full_url
    
    return None

def extract_github(text):
    """Extract GitHub URL or handle"""
    patterns = [
        r'github\.com/[\w-]+',
        r'www\.github\.com/[\w-]+'
    ]
    
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            return match.group(0)
    
    return None

def clean_section_content(content):
    """Clean up section content"""
    # Remove single-letter lines at the beginning
    content = re.sub(r'^\s*[A-Z]\s*\n', '', content)
    
    # Fix bullet points
    content = re.sub(r'^\s*•', '• ', content, flags=re.MULTILINE)
    content = re.sub(r'^\s*\\bullet', '• ', content, flags=re.MULTILINE)
    content = re.sub(r'^\s*-', '• ', content, flags=re.MULTILINE)
    content = re.sub(r'^\s*\*', '• ', content, flags=re.MULTILINE)
    
    # Fix formatting like em dashes
    content = content.replace('–', '-')
    
    # Remove non-printable and non-ASCII characters
    content = re.sub(r'[^\x20-\x7E\n]', ' ', content)
    
    # Fix multiple spaces
    content = re.sub(r' {2,}', ' ', content)
    
    return content.strip()

def identify_section_headers(text):
    """Identify section headers in the resume using multiple methods"""
    common_headers = [
        "EDUCATION",
        "WORK EXPERIENCE", 
        "EXPERIENCE",
        "PROJECTS",
        "TECHNICAL SKILLS",
        "SKILLS",
        "CERTIFICATIONS",
        "PUBLICATIONS",
        "LEADERSHIP",
        "AWARDS",
        "VOLUNTEER",
    ]
    
    # Find all potential section headers
    header_positions = []
    
    # Method 1: Look for all-caps section headers
    for header in common_headers:
        # Simple pattern: header on its own line (most common)
        pattern = r'(?:\n|\r|\A)\s*' + re.escape(header) + r'\s*(?:\n|\r)'
        for match in re.finditer(pattern, text, re.IGNORECASE):
            header_positions.append((match.start(), match.group().strip()))
    
    # Method 2: Look for bold/underlined headers (often in PDFs)
    lines = text.split('\n')
    for i, line in enumerate(lines):
        line = line.strip()
        if line.upper() in [h.upper() for h in common_headers]:
            # Find the position in the original text
            pos = text.find(line)
            if pos >= 0:
                header_positions.append((pos, line))
    
    # Method 3: Look for headers with specific formats often found in resumes
    # (like headers followed by dates or other specific patterns)
    header_patterns = [
        # Education followed by degree
        r'EDUCATION(?:\n|\r)(?:[^\n\r]*(?:Master|Bachelor|Ph\.D|degree))',
        # Work Experience followed by job title
        r'WORK EXPERIENCE(?:\n|\r)(?:[^\n\r]*(?:Engineer|Developer|Manager|Intern))',
        # Projects section
        r'PROJECTS(?:\n|\r)(?:[^\n\r]*(?:GitHub|http|www|project))',
        # Skills section
        r'TECHNICAL SKILLS(?:\n|\r)(?:[^\n\r]*(?:Programming|Language|Technology|Tool))'
    ]
    
    for pattern in header_patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            # Extract just the header part, not the content
            header_text = match.group(0).split('\n')[0].strip()
            header_positions.append((match.start(), header_text))
    
    # Remove duplicates (headers found by multiple methods)
    unique_positions = {}
    for pos, header in header_positions:
        # Group headers that are close together (within 10 chars)
        grouped = False
        for existing_pos in list(unique_positions.keys()):
            if abs(pos - existing_pos) < 10:
                grouped = True
                # Keep the one with the cleaner header text
                if len(header) < len(unique_positions[existing_pos]):
                    unique_positions[existing_pos] = header
                break
        
        if not grouped:
            unique_positions[pos] = header
    
    # Convert back to list and sort by position
    result = [(pos, header) for pos, header in unique_positions.items()]
    result.sort()
    
    return result

def extract_sections(text):
    """Extract sections from resume text"""
    # Get section headers
    header_positions = identify_section_headers(text)
    
    # Print headers for debugging
    print("\nDetected section headers:")
    for pos, header in header_positions:
        print(f"Position {pos}: '{header}'")
    
    # Extract sections
    sections = {}
    
    for i in range(len(header_positions)):
        start_pos, header = header_positions[i]
        header_text = header.strip()
        
        # Determine end position
        if i < len(header_positions) - 1:
            end_pos = header_positions[i+1][0]
        else:
            end_pos = len(text)
        
        # Get section content
        content_start = start_pos + len(header_text)
        section_content = text[content_start:end_pos].strip()
        
        # Clean section content
        section_content = clean_section_content(section_content)
        
        # Normalize header name (remove extra whitespace, etc.)
        normalized_header = re.sub(r'\s+', ' ', header_text).strip().upper()
        
        # Store section
        sections[normalized_header] = section_content
    
    return sections

def extract_name(text):
    """Extract name from resume text using multiple strategies"""
    # Strategy 1: Look for the name at the top of the resume
    lines = text.split('\n')
    
    # Try the first few non-empty lines
    for i in range(min(5, len(lines))):
        line = lines[i].strip()
        
        # Skip empty lines
        if not line:
            continue
        
        # If it's a short line at the top (likely a name)
        if len(line) < 40 and not re.search(r'@|\d{3}|www|http|resume|cv', line.lower()):
            # Names are typically 2-3 words
            words = line.split()
            if 1 <= len(words) <= 3:
                return line
    
    # Strategy 2: Look for common name patterns
    name_patterns = [
        r'([A-Z][a-z]+[\s-]+[A-Z][a-z]+)',  # First Last
        r'([A-Z][a-z]+-[A-Z][a-z]+\s+[A-Z][a-z]+)',  # First-Middle Last
        r'([A-Z][a-z]+\s+[A-Z][a-z]+)',  # First Last (simple)
    ]
    
    for pattern in name_patterns:
        matches = re.findall(pattern, text[:500])  # Look in first 500 chars
        if matches:
            return matches[0]
    
    return None

def fix_formatting(text):
    """Fix common formatting issues in extracted text"""
    # Fix dates like "2022 2024" to "2022 - 2024"
    text = re.sub(r'(\d{4})\s+(\d{4})', r'\1 - \2', text)
    
    # Fix GPA format
    text = re.sub(r'GPA\s+(\d+\.\d+)\s+(\d+\.\d+)', r'GPA \1/\2', text)
    
    # Fix range indicators
    text = re.sub(r'(\w+)\s+(\d{4})\s+-\s+(\w+)\.?\s+(\d{4})', r'\1 \2 - \3 \4', text)
    
    return text

def parse_resume(file_path):
    """Parse resume file and extract structured information"""
    # Extract text from file
    text = extract_text(file_path)
    if not text or text == "Unsupported file format":
        return {"error": "Could not extract text from file"}
    
    # Print first few characters for debugging
    print(f"Text preview: {text[:100].replace(chr(10), ' ')}")
    
    # Fix formatting issues
    text = fix_formatting(text)
    
    # Extract contact information
    name = extract_name(text)
    email = extract_email(text)
    phone = extract_phone(text)
    linkedin = extract_linkedin(text)
    website = extract_website(text)
    github = extract_github(text)
    
    # Extract sections
    sections = extract_sections(text)
    
    # Compile results
    result = {
        "name": name,
        "email": email,
        "phone": phone,
        "linkedin": linkedin,
        "website": website,
        "github": github,
        "sections": sections
    }
    
    return result

# Example usage
if __name__ == "__main__":
    resume_path = "data/YYResume.docx"  # Update this path to your resume file
    parsed_data = parse_resume(resume_path)
    print(parsed_data)
    print("\n=== CONTACT INFO ===")
    print(f"Name: {parsed_data['name']}")
    print(f"Email: {parsed_data['email']}")
    print(f"Phone: {parsed_data['phone']}")
    print(f"LinkedIn: {parsed_data['linkedin']}")
    print(f"Website: {parsed_data['website']}")
    print(f"GitHub: {parsed_data['github']}")
    
    print("\n=== RESUME SECTIONS ===")
    for section, content in parsed_data['sections'].items():
        print(f"\n--- {section} ---")
        print(f"{content[:1000]}...")