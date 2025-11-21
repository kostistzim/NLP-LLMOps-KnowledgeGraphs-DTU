"""
PDF to text extraction using GROBID
"""
import sys

import os
import requests
from xml.etree import ElementTree as ET


def extract_text_from_pdf(pdf_path: str, grobid_url: str = None) -> str:
    """Extract text from PDF using GROBID"""
    if grobid_url is None:
        grobid_url = os.getenv("GROBID_URL", "http://localhost:8070")
    
    xml_response = send_to_grobid(pdf_path, grobid_url)
    text = parse_grobid_xml(xml_response)
    return text


def send_to_grobid(pdf_path: str, grobid_url: str) -> str:
    """Send PDF to GROBID API"""
    endpoint = f"{grobid_url}/api/processFulltextDocument"
    
    with open(pdf_path, 'rb') as pdf_file:
        files = {'input': pdf_file}
        response = requests.post(endpoint, files=files, timeout=60)
    
    response.raise_for_status()
    return response.text


def parse_grobid_xml(xml_string: str) -> str:
    """Parse GROBID XML and extract body text"""
    root = ET.fromstring(xml_string)
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
    
    paragraphs = root.findall('.//tei:body//tei:p', ns)
    texts = [''.join(p.itertext()).strip() for p in paragraphs if ''.join(p.itertext()).strip()]
    
    return '\n'.join(texts)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        text = extract_text_from_pdf(sys.argv[1])
        print(f"Extracted {len(text)} characters")
        print(text[:500])