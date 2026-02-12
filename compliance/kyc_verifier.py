"""
KYC Verifier - Mock implementation for hackathon
Simulates Aadhaar and PAN verification
"""

import re
import random
from datetime import datetime


class KYCVerifier:
    """KYC/AML verification system (mock implementation)"""
    
    def __init__(self):
        self.verified_users = {}
    
    def verify_aadhaar(self, aadhaar_number, name, dob):
        """
        Mock Aadhaar verification
        In production: integrate with UIDAI API
        """
        # Validate Aadhaar format (12 digits)
        if not re.match(r'^\d{12}$', aadhaar_number.replace(' ', '')):
            return {
                'success': False,
                'message': 'Invalid Aadhaar format',
                'verified': False
            }
        
        # Simulate verification (always pass for demo)
        return {
            'success': True,
            'verified': True,
            'aadhaar_number': aadhaar_number,
            'name': name,
            'dob': dob,
            'verification_id': f'AADHAAR-{random.randint(100000, 999999)}',
            'timestamp': datetime.now().isoformat()
        }
    
    def verify_pan(self, pan_number, name):
        """
        Mock PAN verification
        In production: integrate with Income Tax Department API
        """
        # Validate PAN format (ABCDE1234F)
        if not re.match(r'^[A-Z]{5}\d{4}[A-Z]$', pan_number):
            return {
                'success': False,
                'message': 'Invalid PAN format',
                'verified': False
            }
        
        # Simulate verification
        return {
            'success': True,
            'verified': True,
            'pan_number': pan_number,
            'name': name,
            'verification_id': f'PAN-{random.randint(100000, 999999)}',
            'timestamp': datetime.now().isoformat()
        }
    
    def perform_aml_screening(self, user_data):
        """
        AML (Anti-Money Laundering) screening
        Check against watchlists and sanctions
        """
        # Simulate AML check
        risk_score = random.randint(0, 100)
        
        if risk_score < 30:
            risk_level = 'low'
            cleared = True
        elif risk_score < 70:
            risk_level = 'medium'
            cleared = True
        else:
            risk_level = 'high'
            cleared = False
        
        return {
            'cleared': cleared,
            'risk_score': risk_score,
            'risk_level': risk_level,
            'watchlist_match': False,
            'sanctions_match': False,
            'timestamp': datetime.now().isoformat()
        }
    
    def complete_kyc(self, user_id, aadhaar_data, pan_data, aml_data):
        """Complete KYC process"""
        if not (aadhaar_data['verified'] and pan_data['verified'] and aml_data['cleared']):
            return {
                'success': False,
                'kyc_status': 'failed',
                'message': 'KYC verification failed'
            }
        
        # Store verified user
        self.verified_users[user_id] = {
            'aadhaar': aadhaar_data,
            'pan': pan_data,
            'aml': aml_data,
            'kyc_status': 'verified',
            'verified_at': datetime.now().isoformat()
        }
        
        return {
            'success': True,
            'kyc_status': 'verified',
            'user_id': user_id,
            'message': 'KYC completed successfully'
        }
    
    def check_kyc_status(self, user_id):
        """Check if user has completed KYC"""
        if user_id in self.verified_users:
            return self.verified_users[user_id]
        return {'kyc_status': 'not_verified'}


kyc_verifier = KYCVerifier()
