"""
OCR Processor for Document Verification
Extracts text from property documents and identity proofs
"""

import cv2
import pytesseract
import numpy as np
from PIL import Image
import re


class OCRProcessor:
    """Process and extract text from property documents"""
    
    def __init__(self):
        # Configure Tesseract (update path for Windows if needed)
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        pass
    
    def preprocess_image(self, image_path):
        """
        Preprocess image for better OCR accuracy
        - Convert to grayscale
        - Apply thresholding
        - Remove noise
        """
        img = cv2.imread(image_path)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        # Noise removal
        kernel = np.ones((1, 1), np.uint8)
        processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return processed
    
    def extract_text(self, image_path, lang='eng+hin'):
        """
        Extract text from image using Tesseract OCR
        Supports English and Hindi
        """
        try:
            # Preprocess image
            processed_img = self.preprocess_image(image_path)
            
            # Perform OCR
            text = pytesseract.image_to_string(processed_img, lang=lang)
            
            return text.strip()
        except Exception as e:
            print(f"OCR Error: {e}")
            return ""
    
    def extract_property_deed_info(self, image_path):
        """
        Extract structured information from property deed
        Returns: dict with property details
        """
        text = self.extract_text(image_path)
        
        # Extract common property deed fields
        property_info = {
            'raw_text': text,
            'property_id': self._extract_property_id(text),
            'owner_name': self._extract_owner_name(text),
            'address': self._extract_address(text),
            'area': self._extract_area(text),
            'survey_number': self._extract_survey_number(text)
        }
        
        return property_info
    
    def extract_identity_info(self, image_path, doc_type='aadhaar'):
        """
        Extract information from identity documents
        Supports: Aadhaar, PAN, Passport
        """
        text = self.extract_text(image_path)
        
        if doc_type.lower() == 'aadhaar':
            return self._extract_aadhaar_info(text)
        elif doc_type.lower() == 'pan':
            return self._extract_pan_info(text)
        else:
            return {'raw_text': text}
    
    def _extract_property_id(self, text):
        """Extract property ID using regex patterns"""
        patterns = [
            r'Property\s+ID[:\s]+([A-Z0-9\-]+)',
            r'Registration\s+No[:\s]+([A-Z0-9\-]+)',
            r'Document\s+No[:\s]+([A-Z0-9\-]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def _extract_owner_name(self, text):
        """Extract owner name"""
        patterns = [
            r'Owner[:\s]+([A-Za-z\s]+)',
            r'Name[:\s]+([A-Za-z\s]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Clean up (take first line only)
                return name.split('\n')[0]
        return None
    
    def _extract_address(self, text):
        """Extract property address"""
        # Look for address keywords
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if 'address' in line.lower() or 'location' in line.lower():
                # Return next few lines as address
                return ' '.join(lines[i+1:i+4]).strip()
        return None
    
    def _extract_area(self, text):
        """Extract property area (sq ft, sq m, acres)"""
        patterns = [
            r'(\d+\.?\d*)\s*(sq\.?\s*ft|square\s+feet)',
            r'(\d+\.?\d*)\s*(sq\.?\s*m|square\s+meter)',
            r'(\d+\.?\d*)\s*acres?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return f"{match.group(1)} {match.group(2)}"
        return None
    
    def _extract_survey_number(self, text):
        """Extract survey/plot number"""
        patterns = [
            r'Survey\s+No[:\s]+([A-Z0-9\-/]+)',
            r'Plot\s+No[:\s]+([A-Z0-9\-/]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def _extract_aadhaar_info(self, text):
        """Extract Aadhaar card information"""
        # Aadhaar number pattern: XXXX XXXX XXXX
        aadhaar_pattern = r'\b\d{4}\s\d{4}\s\d{4}\b'
        aadhaar_match = re.search(aadhaar_pattern, text)
        
        return {
            'raw_text': text,
            'aadhaar_number': aadhaar_match.group(0) if aadhaar_match else None,
            'document_type': 'aadhaar'
        }
    
    def _extract_pan_info(self, text):
        """Extract PAN card information"""
        # PAN pattern: ABCDE1234F
        pan_pattern = r'\b[A-Z]{5}\d{4}[A-Z]\b'
        pan_match = re.search(pan_pattern, text)
        
        return {
            'raw_text': text,
            'pan_number': pan_match.group(0) if pan_match else None,
            'document_type': 'pan'
        }
    
    def calculate_confidence(self, extracted_data):
        """
        Calculate confidence score for extracted data
        Returns: 0-100 score
        """
        score = 0
        total_fields = 0
        
        for key, value in extracted_data.items():
            if key != 'raw_text':
                total_fields += 1
                if value:
                    score += 1
        
        if total_fields == 0:
            return 0
        
        confidence = (score / total_fields) * 100
        return round(confidence, 2)


# Singleton instance
ocr_processor = OCRProcessor()
