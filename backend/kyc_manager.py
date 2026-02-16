"""
KYC Manager - Comprehensive KYC Management System
Handles multi-step KYC verification workflow with document upload
"""

import os
from datetime import datetime
from enum import Enum


class KYCStatus(Enum):
    """KYC verification status"""
    NOT_STARTED = "not_started"
    PENDING = "pending"
    IN_REVIEW = "in_review"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"


class KYCDocumentType(Enum):
    """Types of KYC documents"""
    AADHAAR = "aadhaar"
    PAN = "pan"
    SELFIE = "selfie"
    DRIVING_LICENSE = "driving_license"
    PASSPORT = "passport"


class KYCManager:
    """Manages KYC verification workflow and document storage"""
    
    def __init__(self):
        self.kyc_records = {}
        self.verification_history = {}
        
        # Configuration
        self.kyc_required = os.getenv('KYC_REQUIRED', 'False').lower() == 'true'
        self.auto_verify = os.getenv('KYC_AUTO_VERIFY', 'True').lower() == 'true'  # Demo mode
        
    def initialize_kyc(self, user_id):
        """Initialize KYC record for a user"""
        if user_id not in self.kyc_records:
            self.kyc_records[user_id] = {
                'user_id': user_id,
                'status': KYCStatus.NOT_STARTED.value,
                'documents': {},
                'verification_steps': {
                    'aadhaar_uploaded': False,
                    'aadhaar_verified': False,
                    'pan_uploaded': False,
                    'pan_verified': False,
                    'selfie_uploaded': False,
                    'face_matched': False,
                    'aml_cleared': False
                },
                'verification_data': {},
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'submitted_at': None,
                'verified_at': None,
                'verifier_notes': ''
            }
        return self.kyc_records[user_id]
    
    def upload_document(self, user_id, doc_type, file_path, metadata=None):
        """
        Upload and store KYC document
        
        Args:
            user_id: User identifier
            doc_type: Type of document (from KYCDocumentType)
            file_path: Path where document is stored
            metadata: Additional document metadata
        """
        # Initialize KYC if not exists
        kyc_record = self.initialize_kyc(user_id)
        
        # Store document info
        doc_info = {
            'type': doc_type,
            'file_path': file_path,
            'uploaded_at': datetime.now().isoformat(),
            'verified': False,
            'verification_score': None,
            'metadata': metadata or {}
        }
        
        kyc_record['documents'][doc_type] = doc_info
        kyc_record['updated_at'] = datetime.now().isoformat()
        
        # Update verification steps
        if doc_type == KYCDocumentType.AADHAAR.value:
            kyc_record['verification_steps']['aadhaar_uploaded'] = True
        elif doc_type == KYCDocumentType.PAN.value:
            kyc_record['verification_steps']['pan_uploaded'] = True
        elif doc_type == KYCDocumentType.SELFIE.value:
            kyc_record['verification_steps']['selfie_uploaded'] = True
        
        # Update status to pending if not already
        if kyc_record['status'] == KYCStatus.NOT_STARTED.value:
            kyc_record['status'] = KYCStatus.PENDING.value
        
        return {
            'success': True,
            'document': doc_info,
            'kyc_status': kyc_record['status']
        }
    
    def verify_aadhaar_document(self, user_id, aadhaar_data):
        """
        Verify Aadhaar document
        
        Args:
            user_id: User identifier
            aadhaar_data: Extracted Aadhaar data from OCR
        """
        kyc_record = self.kyc_records.get(user_id)
        if not kyc_record:
            return {'success': False, 'error': 'KYC record not found'}
        
        # Simulate verification (in production, call UIDAI API)
        verification_result = {
            'verified': True,
            'aadhaar_number': aadhaar_data.get('aadhaar_number'),
            'name': aadhaar_data.get('name'),
            'dob': aadhaar_data.get('dob'),
            'address': aadhaar_data.get('address'),
            'verification_score': 95,
            'verified_at': datetime.now().isoformat()
        }
        
        # Update KYC record
        kyc_record['verification_steps']['aadhaar_verified'] = True
        kyc_record['verification_data']['aadhaar'] = verification_result
        kyc_record['updated_at'] = datetime.now().isoformat()
        
        if 'aadhaar' in kyc_record['documents']:
            kyc_record['documents']['aadhaar']['verified'] = True
            kyc_record['documents']['aadhaar']['verification_score'] = 95
        
        return {
            'success': True,
            'verification': verification_result
        }
    
    def verify_pan_document(self, user_id, pan_data):
        """
        Verify PAN document
        
        Args:
            user_id: User identifier
            pan_data: Extracted PAN data from OCR
        """
        kyc_record = self.kyc_records.get(user_id)
        if not kyc_record:
            return {'success': False, 'error': 'KYC record not found'}
        
        # Simulate verification (in production, call Income Tax API)
        verification_result = {
            'verified': True,
            'pan_number': pan_data.get('pan_number'),
            'name': pan_data.get('name'),
            'verification_score': 98,
            'verified_at': datetime.now().isoformat()
        }
        
        # Update KYC record
        kyc_record['verification_steps']['pan_verified'] = True
        kyc_record['verification_data']['pan'] = verification_result
        kyc_record['updated_at'] = datetime.now().isoformat()
        
        if 'pan' in kyc_record['documents']:
            kyc_record['documents']['pan']['verified'] = True
            kyc_record['documents']['pan']['verification_score'] = 98
        
        return {
            'success': True,
            'verification': verification_result
        }
    
    def perform_face_matching(self, user_id):
        """
        Perform face matching between Aadhaar photo and selfie
        
        Args:
            user_id: User identifier
        """
        kyc_record = self.kyc_records.get(user_id)
        if not kyc_record:
            return {'success': False, 'error': 'KYC record not found'}
        
        # Check if both documents exist
        if 'aadhaar' not in kyc_record['documents'] or 'selfie' not in kyc_record['documents']:
            return {
                'success': False,
                'error': 'Both Aadhaar and selfie required for face matching'
            }
        
        # Simulate face matching (in production, use face recognition ML model)
        match_result = {
            'matched': True,
            'confidence_score': 92.5,
            'liveness_detected': True,
            'matched_at': datetime.now().isoformat()
        }
        
        # Update KYC record
        kyc_record['verification_steps']['face_matched'] = True
        kyc_record['verification_data']['face_match'] = match_result
        kyc_record['updated_at'] = datetime.now().isoformat()
        
        if 'selfie' in kyc_record['documents']:
            kyc_record['documents']['selfie']['verified'] = True
            kyc_record['documents']['selfie']['verification_score'] = 92.5
        
        return {
            'success': True,
            'match_result': match_result
        }
    
    def submit_for_review(self, user_id):
        """
        Submit KYC for manual review
        
        Args:
            user_id: User identifier
        """
        kyc_record = self.kyc_records.get(user_id)
        if not kyc_record:
            return {'success': False, 'error': 'KYC record not found'}
        
        # Check if all required documents are uploaded
        required_docs = ['aadhaar', 'pan', 'selfie']
        missing_docs = [doc for doc in required_docs if doc not in kyc_record['documents']]
        
        if missing_docs:
            return {
                'success': False,
                'error': 'Missing required documents',
                'missing_documents': missing_docs
            }
        
        # Update status
        kyc_record['status'] = KYCStatus.IN_REVIEW.value
        kyc_record['submitted_at'] = datetime.now().isoformat()
        kyc_record['updated_at'] = datetime.now().isoformat()
        
        # Auto-verify in demo mode
        if self.auto_verify:
            return self.auto_verify_kyc(user_id)
        
        return {
            'success': True,
            'status': KYCStatus.IN_REVIEW.value,
            'message': 'KYC submitted for review'
        }
    
    def auto_verify_kyc(self, user_id):
        """
        Auto-verify KYC (demo mode only)
        
        Args:
            user_id: User identifier
        """
        kyc_record = self.kyc_records.get(user_id)
        if not kyc_record:
            return {'success': False, 'error': 'KYC record not found'}
        
        # Mark all steps as complete
        kyc_record['verification_steps']['aml_cleared'] = True
        kyc_record['status'] = KYCStatus.VERIFIED.value
        kyc_record['verified_at'] = datetime.now().isoformat()
        kyc_record['updated_at'] = datetime.now().isoformat()
        kyc_record['verifier_notes'] = 'Auto-verified in demo mode'
        
        # Add to verification history
        if user_id not in self.verification_history:
            self.verification_history[user_id] = []
        
        self.verification_history[user_id].append({
            'action': 'verified',
            'timestamp': datetime.now().isoformat(),
            'verifier': 'system',
            'notes': 'Auto-verified in demo mode'
        })
        
        return {
            'success': True,
            'status': KYCStatus.VERIFIED.value,
            'message': 'KYC verified successfully',
            'verified_at': kyc_record['verified_at']
        }
    
    def get_kyc_status(self, user_id):
        """
        Get KYC status for a user
        
        Args:
            user_id: User identifier
        """
        if user_id not in self.kyc_records:
            return {
                'status': KYCStatus.NOT_STARTED.value,
                'message': 'KYC not started'
            }
        
        kyc_record = self.kyc_records[user_id]
        
        return {
            'status': kyc_record['status'],
            'verification_steps': kyc_record['verification_steps'],
            'documents': {
                doc_type: {
                    'uploaded': True,
                    'verified': doc_info.get('verified', False),
                    'uploaded_at': doc_info.get('uploaded_at')
                }
                for doc_type, doc_info in kyc_record['documents'].items()
            },
            'submitted_at': kyc_record.get('submitted_at'),
            'verified_at': kyc_record.get('verified_at'),
            'updated_at': kyc_record['updated_at']
        }
    
    def is_kyc_verified(self, user_id):
        """
        Check if user has completed KYC verification
        
        Args:
            user_id: User identifier
        """
        if not self.kyc_required:
            return True  # KYC not required in demo mode
        
        if user_id not in self.kyc_records:
            return False
        
        return self.kyc_records[user_id]['status'] == KYCStatus.VERIFIED.value
    
    def get_verification_progress(self, user_id):
        """
        Get verification progress percentage
        
        Args:
            user_id: User identifier
        """
        if user_id not in self.kyc_records:
            return 0
        
        steps = self.kyc_records[user_id]['verification_steps']
        total_steps = len(steps)
        completed_steps = sum(1 for v in steps.values() if v)
        
        return int((completed_steps / total_steps) * 100)


# Global instance
kyc_manager = KYCManager()
