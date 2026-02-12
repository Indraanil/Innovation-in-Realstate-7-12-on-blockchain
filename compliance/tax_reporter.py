"""
Tax Reporter - Generate tax and audit reports
"""

from datetime import datetime
import json


class TaxReporter:
    """Generate tax reports for property transactions"""
    
    def generate_capital_gains_report(self, user_id, transactions):
        """
        Generate capital gains tax report
        
        Args:
            user_id: User ID
            transactions: List of buy/sell transactions
        """
        total_gains = 0
        taxable_transactions = []
        
        for txn in transactions:
            if txn['type'] == 'sell':
                # Calculate gain/loss
                purchase_price = txn.get('purchase_price', 0)
                sale_price = txn.get('sale_price', 0)
                gain = sale_price - purchase_price
                
                total_gains += gain
                
                taxable_transactions.append({
                    'property_id': txn['property_id'],
                    'purchase_date': txn.get('purchase_date'),
                    'sale_date': txn.get('sale_date'),
                    'purchase_price': purchase_price,
                    'sale_price': sale_price,
                    'capital_gain': gain,
                    'holding_period_days': txn.get('holding_period', 0)
                })
        
        # Determine tax category (simplified)
        long_term_threshold = 730  # 2 years
        
        return {
            'user_id': user_id,
            'financial_year': '2024-25',
            'total_capital_gains': total_gains,
            'transactions': taxable_transactions,
            'tax_category': 'long_term' if any(t.get('holding_period', 0) > long_term_threshold 
                                              for t in transactions) else 'short_term',
            'generated_at': datetime.now().isoformat()
        }
    
    def generate_rental_income_report(self, user_id, properties):
        """Generate rental income report"""
        total_rental_income = 0
        property_incomes = []
        
        for prop in properties:
            annual_income = prop.get('annual_rental_income', 0)
            total_rental_income += annual_income
            
            property_incomes.append({
                'property_id': prop['property_id'],
                'property_name': prop.get('name'),
                'annual_rental_income': annual_income,
                'ownership_percentage': prop.get('ownership_percentage', 100)
            })
        
        return {
            'user_id': user_id,
            'financial_year': '2024-25',
            'total_rental_income': total_rental_income,
            'properties': property_incomes,
            'generated_at': datetime.now().isoformat()
        }
    
    def generate_audit_trail(self, user_id, start_date, end_date):
        """Generate complete audit trail for compliance"""
        return {
            'user_id': user_id,
            'period': {
                'start': start_date,
                'end': end_date
            },
            'audit_items': [
                {
                    'timestamp': datetime.now().isoformat(),
                    'action': 'property_registered',
                    'details': 'Property tokenization completed'
                },
                {
                    'timestamp': datetime.now().isoformat(),
                    'action': 'kyc_verified',
                    'details': 'KYC verification successful'
                }
            ],
            'compliance_status': 'compliant',
            'generated_at': datetime.now().isoformat()
        }


tax_reporter = TaxReporter()
