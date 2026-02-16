"""
BharatPropChain Compliance Engine
Handles KYC whitelisting, verification workflows, and trading eligibility
"""

from enum import Enum
from datetime import datetime


class VerificationStatus(Enum):
    """Property verification status"""
    PENDING = "pending"
    DOCUMENTS_UPLOADED = "documents_uploaded"
    AI_VERIFIED = "ai_verified"
    TOKENIZED = "tokenized"
    REJECTED = "rejected"


class ComplianceEngine:
    """Manages compliance workflows and KYC whitelisting"""
    
    def __init__(self):
        self.kyc_whitelist = {}
        self.verification_workflows = {}
        self.transaction_records = {}
        self.aml_limits = {
            'daily_limit': 1000000,  # ₹10 lakhs
            'monthly_limit': 5000000  # ₹50 lakhs
        }
    
    def add_to_kyc_whitelist(self, user_id, kyc_result):
        """Add user to KYC whitelist"""
        self.kyc_whitelist[user_id] = {
            'verified': True,
            'kyc_result': kyc_result,
            'verified_at': datetime.now().isoformat()
        }
        return {'success': True, 'user_id': user_id}
    
    def is_kyc_verified(self, user_id):
        """Check if user is KYC verified"""
        return user_id in self.kyc_whitelist and self.kyc_whitelist[user_id]['verified']
    
    def initialize_verification_workflow(self, property_id, owner_id):
        """Initialize property verification workflow"""
        workflow = {
            'property_id': property_id,
            'owner_id': owner_id,
            'status': VerificationStatus.PENDING.value,
            'steps': {
                'documents_uploaded': False,
                'ai_verified': False,
                'tokenized': False
            },
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        self.verification_workflows[property_id] = workflow
        return workflow
    
    def update_workflow_status(self, property_id, status, metadata=None):
        """Update verification workflow status"""
        if property_id not in self.verification_workflows:
            return {'success': False, 'error': 'Workflow not found'}
        
        workflow = self.verification_workflows[property_id]
        workflow['status'] = status.value if isinstance(status, VerificationStatus) else status
        workflow['updated_at'] = datetime.now().isoformat()
        
        # Update step completion
        if status == VerificationStatus.DOCUMENTS_UPLOADED:
            workflow['steps']['documents_uploaded'] = True
        elif status == VerificationStatus.AI_VERIFIED:
            workflow['steps']['ai_verified'] = True
        elif status == VerificationStatus.TOKENIZED:
            workflow['steps']['tokenized'] = True
        
        if metadata:
            workflow['metadata'] = metadata
        
        return {'success': True, 'workflow': workflow}
    
    def check_tokenization_eligibility(self, property_id):
        """Check if property is eligible for tokenization"""
        if property_id not in self.verification_workflows:
            return {
                'eligible': False,
                'missing_requirements': ['Verification workflow not initialized']
            }
        
        workflow = self.verification_workflows[property_id]
        missing = []
        
        if not workflow['steps']['documents_uploaded']:
            missing.append('Documents not uploaded')
        
        if not workflow['steps']['ai_verified']:
            missing.append('AI verification not completed')
        
        return {
            'eligible': len(missing) == 0,
            'missing_requirements': missing,
            'workflow_status': workflow['status']
        }
    
    def check_trading_eligibility(self, user_id, property_id, transaction_amount):
        """Check if user is eligible to trade"""
        issues = []
        
        # Check KYC status
        kyc_verified = self.is_kyc_verified(user_id)
        if not kyc_verified:
            issues.append('KYC verification required')
        
        # Check AML limits
        if user_id in self.transaction_records:
            user_txns = self.transaction_records[user_id]
            
            # Calculate daily total
            today = datetime.now().date()
            daily_total = sum(
                txn['amount'] for txn in user_txns 
                if datetime.fromisoformat(txn['timestamp']).date() == today
            )
            
            if daily_total + transaction_amount > self.aml_limits['daily_limit']:
                issues.append(f'Daily transaction limit exceeded (₹{self.aml_limits["daily_limit"]:,})')
        
        return {
            'eligible': len(issues) == 0,
            'issues': issues,
            'kyc_status': 'verified' if kyc_verified else 'not_verified'
        }
    
    def record_transaction(self, user_id, amount, transaction):
        """Record transaction for AML tracking"""
        if user_id not in self.transaction_records:
            self.transaction_records[user_id] = []
        
        self.transaction_records[user_id].append({
            'amount': amount,
            'timestamp': datetime.now().isoformat(),
            'transaction': transaction
        })
        
        return {'success': True}


# Global instance
compliance_engine = ComplianceEngine()
