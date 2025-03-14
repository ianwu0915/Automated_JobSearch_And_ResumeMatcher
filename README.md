🚧 Work in Progress 🚧

### To implement:
- Don't use uuid to store data?
- Implement scheduling pre-fetch jobs to solve search job bottle-necks
- Postgres add volume to persist data
- Implement Middleware for CORS
- Implement FAISS for matching and compare with current method
- Check Redis Implementation
- Migrate to AWS (Lambda? and RDS and API GateWay)
- UI design

# AI-Powered Job Search and Resume Matcher

## Architecture Overview

This project implements an AI-powered job search and resume matching system with a microservices-based architecture. The system combines real-time job searching, intelligent resume parsing, and advanced matching algorithms to help users find relevant job opportunities.

### System Components

```
├── Backend Services
│   ├── Resume Service
│   ├── Job Service
│   ├── Matching Service
│   └── Feature Service
├── Data Storage
│   ├── PostgreSQL (Primary Database)
│   └── Redis (Cache Layer)
├── External Services
│   └── LinkedIn API
└── API Layer
    └── FastAPI Endpoints
```

## Core Services

### 1. Resume Service

- Handles resume upload and processing
- Extracts key features from resumes:
  - Skills identification
  - Experience calculation
  - Keyword extraction
- Stores processed resume data in PostgreSQL
- Caches frequently accessed resume data in Redis

### 2. Job Service

- Integrates with LinkedIn API for job searches
- Implements parallel job fetching
- Features:
  - Caching layer for job data (24-hour TTL)
  - Automatic job data refresh
  - Concurrent job processing
  - Custom filtering and blacklist support

### 3. Matching Service

- Implements intelligent resume-to-job matching
- Scoring components:
  - Skills matching (50% weight)
  - Experience matching (30% weight)
  - Keyword similarity (20% weight)
- Uses advanced algorithms:
  - Cosine similarity for keyword matching
  - Custom skill taxonomy matching
  - Experience level correlation

## Data Flow

1. **Resume Upload Flow**

## Technical Stack

### Backend

- **Framework**: FastAPI
- **Language**: Python 3.8+
- **API Documentation**: OpenAPI (Swagger)

### Data Storage

- **Primary Database**: PostgreSQL
  - Stores user data, resumes, jobs, and match results
  - Optimized for complex queries and full-text search
- **Cache Layer**: Redis
  - Caches job data and search results
  - Reduces API calls and improves response time

### External Services

- LinkedIn API for job data
- NLP libraries for text processing
- Machine Learning for matching algorithms

## Key Features

1. **Intelligent Resume Processing**

   - Automatic skill extraction
   - Experience calculation
   - Education detail parsing
   - Keyword frequency analysis

2. **Advanced Job Matching**

   - Multi-factor scoring system
   - Customizable weights
   - Real-time matching
   - Historical match tracking

3. **Performance Optimizations**
   - Parallel job processing
   - Distributed caching
   - Asynchronous operations
   - Rate limiting and request throttling

## API Endpoints

### Resume Operations

- `POST /api/resumes/upload`: Upload and process new resume
- `GET /api/resumes/{resume_id}`: Retrieve resume details

### Job Operations

- `GET /api/jobs/search_and_match`: Search jobs and match with resume
- `GET /api/jobs/{job_id}`: Get specific job details

### Match Operations

- `GET /api/matches/history`: Retrieve match history

## Setup and Deployment

### Prerequisites

- Python 3.8+
- PostgreSQL
- Redis
- LinkedIn API credentials

### Environment Variables

```
LINKEDIN_USERNAME=your_username
LINKEDIN_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
REDIS_HOST=localhost
REDIS_PORT=6379
```

### Installation

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Unix
venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt

# Set up Redis and Postgres Server
docker compose up -d

# Run application

## Performance Considerations

- Job data cached for 24 hours
- Parallel processing for multiple job searches
- Optimized database queries with proper indexing
- Rate limiting for external API calls
- Efficient memory usage through Redis caching

## Job Search Parameters"

* **experience**: Experience level required
    * '1' = Internship
    * '2' = Entry level
    * '3' = Associate
    * '4' = Mid-Senior
    * '5' = Director
    * '6' = Executive

* **remote**: Work location type
    * 1 = On-site
    * 2 = Remote
    * 3 = Hybrid

* **job_type**: Employment type
    * 'F' = Full-time
    * 'P' = Part-time
    * 'C' = Contract
    * 'T' = Temporary
    * 'I' = Internship
    * 'V' = Volunteer

## Future Enhancements

1. **AI Improvements**

   - Enhanced skill matching algorithms
   - Machine learning-based ranking
   - Sentiment analysis for job descriptions

2. **System Scalability**

   - Kubernetes deployment support
   - Microservices architecture
   - Load balancing implementation

3. **Feature Additions**
   - Multiple resume support
   - Custom matching preferences
   - Job application tracking
   - Email notifications

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE.md file for details


