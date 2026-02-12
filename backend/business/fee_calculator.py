"""
Fee Calculator - Calculate platform fees
"""

import os
from dotenv import load_dotenv

load_dotenv()


class FeeCalculator:
    """Calculate various platform fees"""
    
    def __init__(self):
        self.tokenization_fee_percent = float(os.getenv('TOKENIZATION_FEE_PERCENT', 2.5))
        self.transaction_fee_percent = float(os.getenv('TRANSACTION_FEE_PERCENT', 1.0))
    
    def calculate_tokenization_fee(self, property_value):
        """Calculate fee for tokenizing a property"""
        fee = (property_value * self.tokenization_fee_percent) / 100
        return {
            'fee_amount': fee,
            'fee_percent': self.tokenization_fee_percent,
            'property_value': property_value
        }
    
    def calculate_transaction_fee(self, transaction_amount):
        """Calculate fee for buying/selling tokens"""
        fee = (transaction_amount * self.transaction_fee_percent) / 100
        return {
            'fee_amount': fee,
            'fee_percent': self.transaction_fee_percent,
            'transaction_amount': transaction_amount
        }
    
    def calculate_total_cost(self, base_amount, fee_type='transaction'):
        """Calculate total cost including fees"""
        if fee_type == 'tokenization':
            fee_data = self.calculate_tokenization_fee(base_amount)
        else:
            fee_data = self.calculate_transaction_fee(base_amount)
        
        total = base_amount + fee_data['fee_amount']
        
        return {
            'base_amount': base_amount,
            'fee': fee_data['fee_amount'],
            'total': total
        }


fee_calculator = FeeCalculator()
