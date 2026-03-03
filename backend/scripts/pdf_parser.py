import pdfplumber
import json
import re
import argparse
import sys

def parse_pdf_to_json(pdf_path, output_json_path):
    schemes = []
    
    try:
        print(f"Reading PDF: {pdf_path}...")
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        
        # Split text into potential scheme sections
        # Assuming schemes might be numbered or start with "Scheme Name" or just be distinctive headers
        # This regex tries to find "1. Name" or "Scheme Name:" patterns
        # Adjust logic based on actual document format
        
        # Example: Splits by "Scheme Name:" or Number like "1." 
        # (Very basic heuristic)
        sections = re.split(r'(?:\n\d+\.\s+|Scheme Name:\s*)', text)
        
        for section in sections:
            if not section.strip() or len(section) < 50:
                continue
            
            lines = section.strip().split('\n')
            name = lines[0].strip()
            
            # Extract Benefit if possible
            benefit_match = re.search(r'(?:Benefit|Assistance|Subsidy):\s*(.*)', section, re.IGNORECASE)
            benefit = benefit_match.group(1).strip() if benefit_match else "See details"
            
            # Extract Description
            # Just taking the first few lines as description for now
            description_text = " ".join(lines[1:5]).strip()
            
            scheme = {
                "scheme_name": name,
                "type": "General", # Placeholder
                "benefit": benefit,
                "states": ["All"], # Default
                "crops": ["All"], # Default
                "min_land": 0,
                "max_land": 100,
                "description": {
                    "en": description_text,
                    "hi": "", 
                    "ml": "",
                    "ta": ""
                }
            }
            schemes.append(scheme)

        print(f"Extracted {len(schemes)} schemes.")
        
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(schemes, f, indent=4, ensure_ascii=False)
            
        print(f"Saved to {output_json_path}")
        
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse Scheme PDF to JSON")
    parser.add_argument("input_pdf", help="Path to input PDF file")
    parser.add_argument("output_json", help="Path to output JSON file", default="schemes.json", nargs="?")
    
    args = parser.parse_args()
    
    parse_pdf_to_json(args.input_pdf, args.output_json)
