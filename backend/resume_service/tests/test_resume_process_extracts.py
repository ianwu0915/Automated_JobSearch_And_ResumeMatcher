import pytest
from pathlib import Path
import os
import shutil
import json
from resume_service.utils.file_processors import extract_text_from_file, SUPPORTED_MIME_TYPES
from resume_service.utils.ai_helpers import parse_resume_with_ai

@pytest.fixture
def test_files_dir():
    test_dir = Path("test_files")
    test_dir.mkdir(exist_ok=True)
    
    yield test_dir
    
    # shutil.rmtree(test_dir) #

@pytest.fixture #fixture means that the function will be run before each test
def sample_files(test_files_dir):
    sample_sources = {
        "pdf": "sample_data/resume1.pdf",
        "docx": "sample_data/resume.docx",
    }
    
    files_info = {}
    for file_type, file_path in sample_sources.items():
        if os.path.exists(file_path):
            dest_path = test_files_dir / Path(file_path).name
            shutil.copy(file_path, dest_path)
            files_info[file_type] = dest_path
        else:
            raise FileNotFoundError(f"Sample file not found: {file_path}")
    
    print(f"Created sample files: {files_info}")
    return files_info

@pytest.mark.asyncio
async def test_extract_text_from_pdf(sample_files):
    if "pdf" not in sample_files:
        pytest.skip("PDF file not found")
        
    pdf_path = sample_files["pdf"]
    result = await extract_text_from_file(pdf_path, "pdf")
    
    # Save extracted text to file
    output_path = Path("test_files/extracted_pdf.txt")
    output_path.write_text(result)
    
    print(f"Saved PDF extraction to: {output_path}")
    assert len(result) > 0
    assert any(term in result.lower() for term in ["education", "experience", "skills", "projects"])

@pytest.mark.asyncio
async def test_parse_resume_with_ai(sample_files):
    if "pdf" not in sample_files:
        pytest.skip("PDF file not found")
        
    # First get the text
    pdf_path = sample_files["pdf"]
    extracted_text = await extract_text_from_file(pdf_path, "pdf")
    
    # Then test the parsing
    parsed_result = await parse_resume_with_ai(extracted_text)
    print(f"Parsed result: {parsed_result}")
    
    # Verify parsing results
    assert parsed_result is not None
    assert "skills" in parsed_result
    assert "experience" in parsed_result
    assert "education" in parsed_result
    assert "projects" in parsed_result
    
    # Save parsed result
    output_path = Path("test_files/parsed_pdf.json")
    output_path.write_text(json.dumps(parsed_result, indent=4))
    print(f"Saved parsed result to: {output_path}")

@pytest.mark.asyncio
async def test_extract_text_from_docx(sample_files):
    """Test extracting text from a real DOCX resume"""
    if "docx" not in sample_files:
        pytest.skip("Sample DOCX file not available")
    
    result = await extract_text_from_file(sample_files["docx"], "docx")
    
    # Save extracted text to file
    output_path = Path("test_files/extracted_docx.txt")
    output_path.write_text(result)
    
    print(f"Saved DOCX extraction to: {output_path}")
    assert len(result) > 0
    assert any(term in result.lower() for term in ["resume", "experience", "education", "skills"])
    

def test_supported_mime_types():
    assert "application/pdf" in SUPPORTED_MIME_TYPES
    assert SUPPORTED_MIME_TYPES["application/pdf"] == "pdf"
    assert "text/plain" in SUPPORTED_MIME_TYPES
    assert SUPPORTED_MIME_TYPES["text/plain"] == "txt"

