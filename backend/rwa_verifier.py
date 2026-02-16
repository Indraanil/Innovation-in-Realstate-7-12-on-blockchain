"""
RWA (Real World Asset) Verifier
Property document verification and ownership validation system
"""

import os
from datetime import datetime
from enum import Enum
import random


class RWAStatus(Enum):
    """RWA verification status"""
    NOT_STARTED = "not_started"
    PENDING = "pending"
    IN_REVIEW = "in_review"
    VERIFIED = "verified"
    REJECTED = "rejected"


class PropertyDocumentType(Enum):
    """Types of property documents"""
    TITLE_DEED = "title_deed"
    ENCUMBRANCE_CERT = "encumbrance_certificate"
    TAX_RECEIPT = "tax_receipt"
    SALE_DEED = "sale_deed"
    MUTATION_CERT = "mutation_certificate"
    OCCUPANCY_CERT = "occupancy_certificate"


class RWAVerifier:
    """Manages RWA verification for property documents"""
    
    def __init__(self):
        self.rwa_records = {}
        self.verification_history = {}
        
        # Configuration
        self.rwa_required = os.getenv('RWA_VERIFICATION_REQUIRED', 'False').lower() == 'true'
        self.auto_verify = os.getenv('RWA_AUTO_VERIFY', 'True').lower() == 'true'  # Demo mode
        
        # Minimum verification score required
        self.min_verification_score = 70
        
    def initialize_rwa(self, property_id, owner_id):
        """Initialize RWA verification record for a property"""
        if property_id not in self.rwa_records:
            self.rwa_records[property_id] = {
                'property_id': property_id,
                'owner_id': owner_id,
                'status': RWAStatus.NOT_STARTED.value,
                'documents': {},
                'verification_checks': {
                    'title_deed_verified': False,
                    'encumbrance_clear': False,
                    'tax_receipts_valid': False,
                    'ownership_validated': False,
                    'legal_compliance': False
                },
                'verification_scores': {},
                'overall_score': 0,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'submitted_at': None,
                'verified_at': None,
                'verifier_notes': ''
            }
        return self.rwa_records[property_id]
    
    def upload_document(self, property_id, doc_type, file_path, metadata=None):
        """
        Upload property document for verification
        
        Args:
            property_id: Property identifier
            doc_type: Type of document (from PropertyDocumentType)
            file_path: Path where document is stored
            metadata: Additional document metadata
        """
        # Get or initialize RWA record
        if property_id not in self.rwa_records:
            return {'success': False, 'error': 'RWA record not initialized'}
        
        rwa_record = self.rwa_records[property_id]
        
        # Store document info
        doc_info = {
            'type': doc_type,
            'file_path': file_path,
            'uploaded_at': datetime.now().isoformat(),
            'verified': False,
            'verification_score': None,
            'issues_found': [],
            'metadata': metadata or {}
        }
        
        rwa_record['documents'][doc_type] = doc_info
        rwa_record['updated_at'] = datetime.now().isoformat()
        
        # Update status to pending if not already
        if rwa_record['status'] == RWAStatus.NOT_STARTED.value:
            rwa_record['status'] = RWAStatus.PENDING.value
        
        return {
            'success': True,
            'document': doc_info,
            'rwa_status': rwa_record['status']
        }
    
    def verify_title_deed(self, property_id, deed_data):
        """
        Verify title deed authenticity and ownership
        
        Args:
            property_id: Property identifier
            deed_data: Extracted data from title deed
        """
        rwa_record = self.rwa_records.get(property_id)
        if not rwa_record:
            return {'success': False, 'error': 'RWA record not found'}
        
        # Simulate title deed verification
        # In production: verify with land registry, check deed number, validate signatures
        
        verification_score = random.randint(85, 98)
        issues = []
        
        # Check for common issues
        if not deed_data.get('deed_number'):
            issues.append('Missing deed number')
            verification_score -= 10
        
        if not deed_data.get('owner_name'):
            issues.append('Owner name not found')
            verification_score -= 10
        
        if not deed_data.get('property_address'):
            issues.append('Property address missing')
            verification_score -= 5
        
        verification_result = {
            'verified': verification_score >= self.min_verification_score,
            'verification_score': max(verification_score, 0),
            'deed_number': deed_data.get('deed_number'),
            'owner_name': deed_data.get('owner_name'),
            'property_address': deed_data.get('property_address'),
            'registration_date': deed_data.get('registration_date'),
            'registry_office': deed_data.get('registry_office', 'Sub-Registrar Office'),
            'issues_found': issues,
            'verified_at': datetime.now().isoformat()
        }
        
        # Update RWA record
        rwa_record['verification_checks']['title_deed_verified'] = verification_result['verified']
        rwa_record['verification_scores']['title_deed'] = verification_score
        rwa_record['updated_at'] = datetime.now().isoformat()
        
        if 'title_deed' in rwa_record['documents']:
            rwa_record['documents']['title_deed']['verified'] = verification_result['verified']
            rwa_record['documents']['title_deed']['verification_score'] = verification_score
            rwa_record['documents']['title_deed']['issues_found'] = issues
        
        return {
            'success': True,
            'verification': verification_result
        }
    
    def verify_encumbrance_certificate(self, property_id, ec_data):
        """
        Verify encumbrance certificate (EC)
        Checks if property is free from legal/monetary liabilities
        
        Args:
            property_id: Property identifier
            ec_data: Extracted data from EC
        """
        rwa_record = self.rwa_records.get(property_id)
        if not rwa_record:
            return {'success': False, 'error': 'RWA record not found'}
        
        # Simulate EC verification
        # In production: verify with sub-registrar office, check for liens/mortgages
        
        verification_score = random.randint(90, 99)
        encumbrance_free = random.choice([True, True, True, False])  # 75% chance of being clear
        
        issues = []
        if not encumbrance_free:
            issues.append('Property has existing encumbrances')
            verification_score -= 30
        
        verification_result = {
            'verified': encumbrance_free,
            'encumbrance_free': encumbrance_free,
            'verification_score': verification_score,
            'certificate_number': ec_data.get('certificate_number', f'EC-{random.randint(100000, 999999)}'),
            'issue_date': ec_data.get('issue_date', datetime.now().date().isoformat()),
            'validity_period': ec_data.get('validity_period', '30 years'),
            'issues_found': issues,
            'verified_at': datetime.now().isoformat()
        }
        
        # Update RWA record
        rwa_record['verification_checks']['encumbrance_clear'] = encumbrance_free
        rwa_record['verification_scores']['encumbrance_cert'] = verification_score
        rwa_record['updated_at'] = datetime.now().isoformat()
        
        if 'encumbrance_certificate' in rwa_record['documents']:
            rwa_record['documents']['encumbrance_certificate']['verified'] = encumbrance_free
            rwa_record['documents']['encumbrance_certificate']['verification_score'] = verification_score
            rwa_record['documents']['encumbrance_certificate']['issues_found'] = issues
        
        return {
            'success': True,
            'verification': verification_result
        }
    
    def verify_tax_receipt(self, property_id, tax_data):
        """
        Verify property tax receipt
        
        Args:
            property_id: Property identifier
            tax_data: Extracted data from tax receipt
        """
        rwa_record = self.rwa_records.get(property_id)
        if not rwa_record:
            return {'success': False, 'error': 'RWA record not found'}
        
        # Simulate tax receipt verification
        # In production: verify with municipal corporation, check payment status
        
        verification_score = random.randint(88, 97)
        issues = []
        
        # Check if tax is paid up to date
        tax_paid_current_year = random.choice([True, True, False])  # 66% chance
        if not tax_paid_current_year:
            issues.append('Tax not paid for current year')
            verification_score -= 15
        
        verification_result = {
            'verified': tax_paid_current_year,
            'verification_score': verification_score,
            'receipt_number': tax_data.get('receipt_number', f'TAX-{random.randint(100000, 999999)}'),
            'payment_year': tax_data.get('payment_year', '2025-26'),
            'amount_paid': tax_data.get('amount_paid'),
            'tax_paid_current_year': tax_paid_current_year,
            'issues_found': issues,
            'verified_at': datetime.now().isoformat()
        }
        
        # Update RWA record
        rwa_record['verification_checks']['tax_receipts_valid'] = tax_paid_current_year
        rwa_record['verification_scores']['tax_receipt'] = verification_score
        rwa_record['updated_at'] = datetime.now().isoformat()
        
        if 'tax_receipt' in rwa_record['documents']:
            rwa_record['documents']['tax_receipt']['verified'] = tax_paid_current_year
            rwa_record['documents']['tax_receipt']['verification_score'] = verification_score
            rwa_record['documents']['tax_receipt']['issues_found'] = issues
        
        return {
            'success': True,
            'verification': verification_result
        }
    
    def validate_ownership(self, property_id, owner_id, owner_kyc_data=None):
        """
        Validate property ownership
        Cross-check owner details with KYC and property documents
        
        Args:
            property_id: Property identifier
            owner_id: Owner user ID
            owner_kyc_data: Owner's KYC data for cross-verification
        """
        rwa_record = self.rwa_records.get(property_id)
        if not rwa_record:
            return {'success': False, 'error': 'RWA record not found'}
        
        # Simulate ownership validation
        # In production: cross-check with land records, KYC data, title deed
        
        ownership_valid = True
        verification_score = 95
        issues = []
        
        # Check if title deed exists
        if 'title_deed' not in rwa_record['documents']:
            issues.append('Title deed not uploaded')
            ownership_valid = False
            verification_score -= 30
        
        validation_result = {
            'ownership_valid': ownership_valid,
            'verification_score': verification_score,
            'owner_id': owner_id,
            'cross_verification_done': owner_kyc_data is not None,
            'issues_found': issues,
            'validated_at': datetime.now().isoformat()
        }
        
        # Update RWA record
        rwa_record['verification_checks']['ownership_validated'] = ownership_valid
        rwa_record['verification_scores']['ownership'] = verification_score
        rwa_record['updated_at'] = datetime.now().isoformat()
        
        return {
            'success': True,
            'validation': validation_result
        }
    
    def check_legal_compliance(self, property_id):
        """
        Check legal compliance for property tokenization
        
        Args:
            property_id: Property identifier
        """
        rwa_record = self.rwa_records.get(property_id)
        if not rwa_record:
            return {'success': False, 'error': 'RWA record not found'}
        
        # Simulate legal compliance check
        # In production: check zoning laws, building codes, tokenization regulations
        
        compliance_checks = {
            'zoning_compliant': True,
            'building_code_compliant': True,
            'tokenization_eligible': True,
            'no_legal_disputes': True
        }
        
        all_compliant = all(compliance_checks.values())
        verification_score = 100 if all_compliant else 60
        
        compliance_result = {
            'compliant': all_compliant,
            'verification_score': verification_score,
            'checks': compliance_checks,
            'checked_at': datetime.now().isoformat()
        }
        
        # Update RWA record
        rwa_record['verification_checks']['legal_compliance'] = all_compliant
        rwa_record['verification_scores']['legal_compliance'] = verification_score
        rwa_record['updated_at'] = datetime.now().isoformat()
        
        return {
            'success': True,
            'compliance': compliance_result
        }
    
    def calculate_overall_score(self, property_id):
        """
        Calculate overall RWA verification score
        
        Args:
            property_id: Property identifier
        """
        rwa_record = self.rwa_records.get(property_id)
        if not rwa_record:
            return 0
        
        scores = rwa_record['verification_scores']
        if not scores:
            return 0
        
        # Weighted average
        weights = {
            'title_deed': 0.35,
            'encumbrance_cert': 0.25,
            'tax_receipt': 0.15,
            'ownership': 0.15,
            'legal_compliance': 0.10
        }
        
        weighted_score = 0
        total_weight = 0
        
        for doc_type, weight in weights.items():
            if doc_type in scores:
                weighted_score += scores[doc_type] * weight
                total_weight += weight
        
        if total_weight == 0:
            return 0
        
        overall_score = int(weighted_score / total_weight)
        rwa_record['overall_score'] = overall_score
        
        return overall_score
    
    def submit_for_verification(self, property_id):
        """
        Submit RWA for verification
        
        Args:
            property_id: Property identifier
        """
        rwa_record = self.rwa_records.get(property_id)
        if not rwa_record:
            return {'success': False, 'error': 'RWA record not found'}
        
        # Check if minimum documents are uploaded
        required_docs = ['title_deed']
        missing_docs = [doc for doc in required_docs if doc not in rwa_record['documents']]
        
        if missing_docs:
            return {
                'success': False,
                'error': 'Missing required documents',
                'missing_documents': missing_docs
            }
        
        # Update status
        rwa_record['status'] = RWAStatus.IN_REVIEW.value
        rwa_record['submitted_at'] = datetime.now().isoformat()
        rwa_record['updated_at'] = datetime.now().isoformat()
        
        # Auto-verify in demo mode
        if self.auto_verify:
            return self.auto_verify_rwa(property_id)
        
        return {
            'success': True,
            'status': RWAStatus.IN_REVIEW.value,
            'message': 'RWA submitted for verification'
        }
    
    def auto_verify_rwa(self, property_id):
        """
        Auto-verify RWA (demo mode only)
        
        Args:
            property_id: Property identifier
        """
        rwa_record = self.rwa_records.get(property_id)
        if not rwa_record:
            return {'success': False, 'error': 'RWA record not found'}
        
        # Calculate overall score
        overall_score = self.calculate_overall_score(property_id)
        
        # Mark as verified if score is above threshold
        if overall_score >= self.min_verification_score:
            rwa_record['status'] = RWAStatus.VERIFIED.value
            rwa_record['verified_at'] = datetime.now().isoformat()
            rwa_record['verifier_notes'] = f'Auto-verified with score: {overall_score}/100'
        else:
            rwa_record['status'] = RWAStatus.REJECTED.value
            rwa_record['verifier_notes'] = f'Verification score too low: {overall_score}/100'
        
        rwa_record['updated_at'] = datetime.now().isoformat()
        
        # Add to verification history
        if property_id not in self.verification_history:
            self.verification_history[property_id] = []
        
        self.verification_history[property_id].append({
            'action': 'verified' if overall_score >= self.min_verification_score else 'rejected',
            'timestamp': datetime.now().isoformat(),
            'verifier': 'system',
            'score': overall_score,
            'notes': rwa_record['verifier_notes']
        })
        
        return {
            'success': True,
            'status': rwa_record['status'],
            'overall_score': overall_score,
            'message': f'RWA verification complete with score: {overall_score}/100',
            'verified_at': rwa_record.get('verified_at')
        }
    
    def get_rwa_status(self, property_id):
        """
        Get RWA verification status for a property
        
        Args:
            property_id: Property identifier
        """
        if property_id not in self.rwa_records:
            return {
                'status': RWAStatus.NOT_STARTED.value,
                'message': 'RWA verification not started'
            }
        
        rwa_record = self.rwa_records[property_id]
        overall_score = self.calculate_overall_score(property_id)
        
        return {
            'status': rwa_record['status'],
            'overall_score': overall_score,
            'verification_checks': rwa_record['verification_checks'],
            'verification_scores': rwa_record['verification_scores'],
            'documents': {
                doc_type: {
                    'uploaded': True,
                    'verified': doc_info.get('verified', False),
                    'score': doc_info.get('verification_score'),
                    'issues': doc_info.get('issues_found', []),
                    'uploaded_at': doc_info.get('uploaded_at')
                }
                for doc_type, doc_info in rwa_record['documents'].items()
            },
            'submitted_at': rwa_record.get('submitted_at'),
            'verified_at': rwa_record.get('verified_at'),
            'updated_at': rwa_record['updated_at']
        }
    
    def is_rwa_verified(self, property_id):
        """
        Check if property has completed RWA verification
        
        Args:
            property_id: Property identifier
        """
        if not self.rwa_required:
            return True  # RWA not required in demo mode
        
        if property_id not in self.rwa_records:
            return False
        
        return self.rwa_records[property_id]['status'] == RWAStatus.VERIFIED.value


# Global instance
rwa_verifier = RWAVerifier()
