import re
import spacy
import time
import os

# Load NLP model
nlp = spacy.load("en_core_web_sm")

### Constants
SECTIONS = {
    "company": None,
    "responsibilities": [],
    "qualifications": [],
    "technical_skills": [],
    "preferred_qualifications": []
}

RESPONSIBILITIES_HEADERS = ["Duties", "Responsibilities", "Key Responsibilities", "Position Overview", "What You Will Do"]
QUALIFICATIONS_HEADERS = ["Requirements", "Qualifications", "Skills", "Required Skills", "Experience", "Who You Are",
                          "What You Bring", "What You Have", "What We Are looking for", "What You'll be Up to", "What You", "Responsible for", "To be successful in"]
PREFERRED_HEADERS = ["Preferred Qualifications", "Preferred Skills", "Nice to Have", "About You"]
TECHNICAL_SKILLS_KEYWORDS = [
    # Frontend
    "React", "Vue", "Angular", "JavaScript", "TypeScript", "HTML", "CSS", "SASS", "SCSS", "jQuery", "Redux", 
    "Next.js", "Webpack", "Babel", "Bootstrap", "Tailwind", "Material UI", "WebGL", "Three.js", "D3.js",
    
    # Backend
    "Python", "Java", "C#", ".NET", "Node.js", "Express", "Django", "Flask", "Spring Boot", "FastAPI",
    "Ruby", "Rails", "PHP", "Laravel", "Go", "Golang", "Rust", "Kotlin", "Swift", "C++", "Scala",
    
    # Database
    "SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis", "Oracle", "DynamoDB", "Cassandra", "ElasticSearch",
    "GraphQL", "Firebase", "NoSQL", "Neo4j", "MariaDB", "SQLite", "Prisma", "Sequelize",
    
    # Cloud & DevOps
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Jenkins", "GitLab CI", "GitHub Actions",
    "Terraform", "Ansible", "ECS", "Lambda", "S3", "EC2", "Serverless", "CloudFormation", "Pulumi",
    "CircleCI", "Travis CI", "ArgoCD", "Helm", "Prometheus", "Grafana", "EKS", "GKE", "AKS",
    
    # Testing
    "Jest", "Mocha", "Selenium", "Cypress", "JUnit", "PyTest", "TestNG", "Playwright", "WebdriverIO",
    "Postman", "Newman", "Artillery", "K6", "LoadRunner",
    
    # Tools & Version Control
    "Git", "GitHub", "BitBucket", "JIRA", "Confluence", "Swagger", "OpenAPI", "Maven", "Gradle",
    
    # Architecture & Patterns
    "Microservices", "REST API", "gRPC", "WebSocket", "OAuth", "JWT", "MVC", "CQRS", "Event Sourcing",
    "Domain Driven Design", "TDD", "BDD", "Agile", "Scrum", "Kanban",
    
    # AI & ML
    "Machine Learning", "TensorFlow", "PyTorch", "NLP", "Computer Vision", "Deep Learning", "ML", "AI",
    "Scikit-learn", "Pandas", "NumPy", "OpenCV", "CUDA", "Keras", "Hugging Face",
    
    # Mobile
    "iOS", "Android", "React Native", "Flutter", "SwiftUI", "Kotlin", "Xamarin", "Ionic",
    
    # System & Infrastructure
    "Linux", "Unix", "Bash", "Shell Scripting", "Kafka", "RabbitMQ", "Nginx", "Apache",
    "Distributed Systems", "Cloud", "Backend", "Full Stack", "DevOps", "SRE", "CI/CD",
    
    # Security
    "OAuth2", "SAML", "Cybersecurity", "Encryption", "SSL/TLS", "IAM", "WAF", "Penetration Testing",
    
    # Emerging Tech
    "Blockchain", "Web3", "Smart Contracts", "Solidity", "Ethereum", "NFT", "DeFi",
    "AR/VR", "WebXR", "Unity", "Unreal Engine"
]

### Function to extract job sections properly
def extract_sections(text):
    # Initialize sections dictionary
    sections = {}
    headers = [header.lower() for header in RESPONSIBILITIES_HEADERS + QUALIFICATIONS_HEADERS + PREFERRED_HEADERS]
    current_section = None

    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue

        # Detect section headers dynamically (case-insensitive)
        if any(header in line.lower() for header in headers):
            current_section = line.lower()
            sections[current_section] = []
            sections[current_section].append(line)
        elif current_section:
            sections[current_section].append(line)

    return sections

def extract_skills(sections):
    # Extract technical skills (case-insensitive)
    extracted_skills = set()
    for section_name, text_lines in sections.items():
        for sentence in text_lines:
            for skill in TECHNICAL_SKILLS_KEYWORDS:
                if re.search(rf"\b{re.escape(skill)}\b", sentence, re.IGNORECASE):
                    extracted_skills.add(skill)
    return list(extracted_skills)

def extract_experience_level(sections):
    # Extract experience level
    patterns = [
    r"(\d+\s*-\s*\d+|\d+\+?)\s*(?:years|yrs)\s*(?:of\s+)?(?:experience|exp|work)?",  # Matches "5+ years experience", "2-4 years exp"
    r"(?:experience|exp|work)\s*:\s*(\d+\s*-\s*\d+|\d+\+?)\s*(?:years|yrs)?",  # Matches "Experience: 3-5 years"
    r"(?:at least|minimum of|requires)\s*(\d+\+?)\s*(?:years|yrs)\s*(?:of\s+)?(?:experience|exp|work)?"  # Matches "At least 3+ years experience"
    ]

    for section_name, text_lines in sections.items():
        for pattern in patterns:
            match = re.search(pattern, section_name, re.IGNORECASE)
            if match:
                return match.group(0) 
    return "Not specified"

def extract_salary(text):
    # Extract salary range
    """Extract salary with improved regex patterns"""
    salary_patterns = [
        r'\$\s*(?:\d{2,3},?\d{3}|\d{2,3}K)\s*[–—-]\s*\$\s*(?:\d{2,3},?\d{3}|\d{2,3}K)',  # Added more dash types
        r'\$\s*\d{2,3},?\d{3}\s*[–—-]\s*\d{2,3},?\d{3}',  # Added more dash types
        r'(?:USD|CAD)?\s*\$\s*\d{2,3},?\d{3}',
        r'(?:salary|compensation|pay).{0,20}\$\s*\d{2,3},?\d{3}'
    ]
    
    for pattern in salary_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0).strip()
    return "Not specified"

def process_job_description(job_description):
    # Main function to process job description
    sections = extract_sections(job_description)
    # print(sections)
    extracted_data = {
        "skills": extract_skills(sections),
        "experience_level": extract_experience_level(sections),
        "salary": extract_salary(job_description),
    }
    return extracted_data

def main():
    # Test job descriptions
    job_description = """
    Tailscale is hiring a Software Engineer.
    Key Responsibilities:
    • Work with CI/CD, Secrets Management, and Observability tools.
    • Build infrastructure as code solutions.
    • Work with Go, SQL, and Networking, Distributed Systems, and Cloud.

    Qualifications:
    - 5+ years of experience in software engineering.
    - Experience with SQL, Go, and Networking.

    Preferred Qualifications:
    - Experience with CI/CD, Secrets Management, and Observability tools.
    - Experience with infrastructure as code solutions.

    US Pay Ranges:
    $163k - $204k USD
    US citizen only 
    Must be authorized to work in the US.
    """

    job_description2 = """
    A leading sell-side equity firm is seeking a highly skilled Java Developer to design, develop, and enhance proprietary algorithmic equity execution models for institutional trading. This role offers the opportunity to build and optimize advanced electronic trading systems, working closely with sales, traders, and clients to deliver innovative execution strategies.ResponsibilitiesDevelop and implement a proprietary algorithmic equity execution platform.Collaborate with traders, quants, and sales teams to create customized execution strategies.Design and build low-latency, high-performance algorithmic trading systems.Work on advanced execution models, including VWAP, TWAP, pairs trading, and program trading.Enhance execution efficiency through data-driven analytics and real-time performance tuning.RequirementsMust have 3+ years of experience developing equity algorithmic execution systems.Strong Java 8+ programming skills, with proficiency in SQL and Python.Deep understanding of equity market structures and algorithmic trading.Hands-on experience in building high-performance trading applications.Excellent communication skills to engage with traders, quants, and clients.Prior experience at a bulge-bracket firm is highly desirable.KeywordsJava, Algorithmic Trading, Equity Execution, Program Trading, VWAP, TWAP, Pairs Trading, Low-Latency Systems, Electronic Trading, High-Frequency Trading (HFT), Market Microstructure
    Please send your resume to Jim Geiger jeg@analyticrecruiting.com
    """

    job_description3 = """
    As a Software Developer, Backend at Gruve, you will build and own key backend services, infrastructure, and data that power our core financial products. This is a unique opportunity to gain an in-depth understanding of how the US financial system operates and strengthen your financial-domain knowledge.
    We strive for high engineering standards while solving scalability challenges, and you will have a significant impact at a relatively small company serving a large user base.
    Key Teams: Brokerage: Our mission is to launch new features, expand into different financial services, and bring millions more people into the financial system.Futures Team: Introduce futures trading and event contracts to millions of users with a seamless, secure, and innovative experience.Crypto Team: Drive the delivery of a seamless, intuitive, and powerful crypto trading experience for millions of crypto users.
    Key Roles & ResponsibilitiesBuild scalable systems and components, balancing stability with long-term maintainability.Design, write, test, and release platform or product-facing features with stringent correctness and scalability requirements.Identify opportunities to improve system performance, team productivity, and reduce risks.Collaborate closely with cross-functional teams, client teams, and vendors.
    Basic Qualifications3+ years of experience as a software developer.Proven track record of collaborating with cross-functional teams and delivering large-scope technical projects.Deep understanding of design, product, and backend development, enabling effective collaboration.Experience with Go or Python.Experience with Kafka and data streaming technologies.Experience handling and processing large volumes of data.Familiarity with technologies such as Postgres, K8s, Redis, AWS (or similar).
    Bonus PointsExperience at a fintech company or financial firm.
    Equal Employment OpportunityGruve is an equal opportunity employer and values diversity. We do not discriminate on the basis of race, religion, color, national origin, gender, sexual orientation, age, marital status, veteran status, or disability status.
    Compliance StatementsThis job description complies with the Fair Labor Standards Act (FLSA) and Americans with Disabilities Act (ADA).The essential functions listed are necessary for ADA compliance.Salary ranges are provided in accordance with New York and California pay transparency laws.
    Physical DemandsAbility to remain in a stationary position for extended periods.Occasionally move about the office to access files and office equipment.
    Work EnvironmentThis position may require working in a fast-paced environment.On-site presence is required.
    Reasonable Accommodation StatementGruve is committed to the full inclusion of all qualified individuals. As part of this commitment, Gruve will ensure that persons with disabilities are provided reasonable accommodations. If reasonable accommodation is needed to participate in the job application or interview process, perform essential job functions, and/or receive other benefits and privileges of employment, please contact hr.usa@gruve.ai.
    """

    # print(process_job_description(job_description))
    print(process_job_description(job_description2))
    print(process_job_description(job_description3))
    
    print(os.cpu_count() * 2)

if __name__ == "__main__":
    main()