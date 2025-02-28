# import json
from pathlib import Path
from fastapi import HTTPException
import pandas as pd
import aiofiles
from pypdf import PdfReader
from docx import Document
import mammoth

from utils.lazy_module import LazyModule
# Lazy imports
json = LazyModule('json')
pd = LazyModule('pandas')

# Supported file types
SUPPORTED_MIME_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "application/msword": "doc",
    "text/plain": "txt"
}

async def extract_text_from_file(file_path: str, file_type: str) -> str:
    """Extract text from different file types"""
    try:
        if file_type == "pdf":
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        
        elif file_type == "docx":
            doc = Document(file_path)
            full_text = []
            for paragraph in doc.paragraphs:
                full_text.append(paragraph.text)
            return '\n'.join(full_text)
        
        elif file_type == "doc":
            with open(file_path, "rb") as docx_file:
                result = mammoth.convert_to_html(docx_file)
                return result.value
        
        elif file_type == "txt":
            async with aiofiles.open(file_path, 'r') as f:
                return await f.read()
        
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    except Exception as e:
        print(f"Error extracting text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to extract text: {str(e)}")

class ExcelFileHandler:
    @staticmethod
    def save_to_json(data, output_dir: Path, filename="job_data.json"):
        """Save data to JSON file"""
        json_path = output_dir / filename
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return json_path

    @staticmethod
    def setup_excel_writer(df: pd.DataFrame, writer):
        """Setup Excel writer with formatting"""
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']
        
        # Auto-adjust columns width
        for idx, col in enumerate(df.columns):
            max_length = max(
                df[col].astype(str).apply(len).max(),
                len(str(col))
            )
            worksheet.set_column(idx, idx, max_length + 2)
            
        return workbook, worksheet

    @staticmethod
    def add_hyperlinks(df: pd.DataFrame, workbook, worksheet):
        """Add hyperlinks to Apply URL column"""
        link_format = workbook.add_format({
            'font_color': 'blue',
            'underline': True,
        })
        
        url_col = df.columns.get_loc('Apply URL')
        for row_num, url in enumerate(df['Apply URL'], start=1):
            if url != 'N/A':
                worksheet.write_url(row_num, url_col, url, link_format, url)

    @staticmethod
    def save_to_excel(df: pd.DataFrame, output_dir: Path, filename="job_data.xlsx"):
        """Save DataFrame to Excel with formatting"""
        excel_path = output_dir / filename
        with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
            workbook, worksheet = ExcelFileHandler.setup_excel_writer(df, writer)
            ExcelFileHandler.add_hyperlinks(df, workbook, worksheet)
        return excel_path 