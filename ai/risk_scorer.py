"""
Risk Scoring Module
Assess property investment risk based on multiple factors
"""

import numpy as np
from datetime import datetime


class RiskScorer:
    """Calculate risk scores for property investments"""
    
    def __init__(self):
        # Risk weights for different factors
        self.weights = {
            'location': 0.25,
            'legal': 0.30,
            'market': 0.20,
            'document': 0.15,
            'financial': 0.10
        }
    
    def calculate_risk_score(self, property_data, fraud_analysis=None):
        """
        Calculate comprehensive risk score (0-100)
        Lower score = lower risk (better)
        
        Args:
            property_data: Dict with property information
            fraud_analysis: Results from fraud detector
        
        Returns:
            Dict with overall score and breakdown
        """
        scores = {}
        
        # 1. Location risk
        scores['location'] = self._assess_location_risk(property_data)
        
        # 2. Legal compliance risk
        scores['legal'] = self._assess_legal_risk(property_data)
        
        # 3. Market volatility risk
        scores['market'] = self._assess_market_risk(property_data)
        
        # 4. Document authenticity risk
        scores['document'] = self._assess_document_risk(fraud_analysis)
        
        # 5. Financial risk
        scores['financial'] = self._assess_financial_risk(property_data)
        
        # Calculate weighted overall score
        overall_score = sum(
            scores[factor] * self.weights[factor]
            for factor in self.weights.keys()
        )
        
        # Determine risk category
        risk_category = self._categorize_risk(overall_score)
        
        return {
            'overall_score': round(overall_score, 2),
            'risk_category': risk_category,
            'factor_scores': scores,
            'recommendations': self._generate_recommendations(scores),
            'timestamp': datetime.now().isoformat()
        }
    
    def _assess_location_risk(self, property_data):
        """Assess risk based on property location"""
        location = property_data.get('location', '').lower()
        city = property_data.get('city', '').lower()
        
        # Tier-1 cities (lower risk)
        tier1_cities = ['mumbai', 'delhi', 'bangalore', 'hyderabad', 'chennai', 'pune']
        
        # Tier-2 cities (medium risk)
        tier2_cities = ['ahmedabad', 'jaipur', 'lucknow', 'kochi', 'indore', 'bhopal']
        
        if any(c in city for c in tier1_cities):
            base_risk = 20
        elif any(c in city for c in tier2_cities):
            base_risk = 35
        else:
            base_risk = 50
        
        # Adjust for specific location factors
        if 'flood' in location or 'coastal' in location:
            base_risk += 10
        
        if 'industrial' in location:
            base_risk += 5
        
        return min(base_risk, 100)
    
    def _assess_legal_risk(self, property_data):
        """Assess legal and compliance risk"""
        risk_score = 30  # Base score
        
        # Check for clear title
        if property_data.get('clear_title'):
            risk_score -= 15
        else:
            risk_score += 20
        
        # Check for encumbrances
        if property_data.get('has_encumbrance'):
            risk_score += 25
        
        # Check for proper documentation
        docs_count = len(property_data.get('documents', []))
        if docs_count >= 3:
            risk_score -= 10
        elif docs_count == 0:
            risk_score += 20
        
        # Check for government approval
        if property_data.get('govt_approved'):
            risk_score -= 10
        
        return max(0, min(risk_score, 100))
    
    def _assess_market_risk(self, property_data):
        """Assess market volatility and demand risk"""
        property_type = property_data.get('type', '').lower()
        
        # Different property types have different market risks
        type_risk = {
            'residential': 30,
            'commercial': 40,
            'industrial': 50,
            'agricultural': 60,
            'campus': 35
        }
        
        base_risk = type_risk.get(property_type, 45)
        
        # Adjust for market conditions (simulated)
        market_trend = property_data.get('market_trend', 'stable')
        
        if market_trend == 'growing':
            base_risk -= 10
        elif market_trend == 'declining':
            base_risk += 15
        
        # Adjust for property age
        age = property_data.get('age_years', 0)
        if age > 30:
            base_risk += 10
        elif age < 5:
            base_risk -= 5
        
        return min(base_risk, 100)
    
    def _assess_document_risk(self, fraud_analysis):
        """Assess risk based on document verification"""
        if not fraud_analysis:
            return 50  # No analysis = medium risk
        
        if not fraud_analysis.get('is_authentic'):
            return 90  # High risk if fraud detected
        
        # Use fraud confidence score
        confidence = fraud_analysis.get('confidence_score', 50)
        
        # Invert confidence to risk (high confidence = low risk)
        risk_score = 100 - confidence
        
        # Adjust for fraud indicators
        fraud_count = len(fraud_analysis.get('fraud_indicators', []))
        risk_score += fraud_count * 10
        
        return min(risk_score, 100)
    
    def _assess_financial_risk(self, property_data):
        """Assess financial viability risk"""
        base_risk = 30
        
        # Check valuation
        value = property_data.get('total_value', 0)
        
        if value < 1000000:  # Less than 10 lakhs
            base_risk += 20
        elif value > 100000000:  # More than 10 crores
            base_risk += 10
        
        # Check rental yield (if applicable)
        rental_income = property_data.get('annual_rental_income', 0)
        if value > 0 and rental_income > 0:
            rental_yield = (rental_income / value) * 100
            
            if rental_yield < 2:
                base_risk += 15
            elif rental_yield > 6:
                base_risk -= 10
        
        # Check tokenization ratio
        tokens = property_data.get('total_tokens', 1)
        if tokens < 100:
            base_risk += 10  # Too few tokens = liquidity risk
        
        return min(base_risk, 100)
    
    def _categorize_risk(self, score):
        """Categorize risk level"""
        if score < 25:
            return 'Very Low'
        elif score < 40:
            return 'Low'
        elif score < 60:
            return 'Medium'
        elif score < 75:
            return 'High'
        else:
            return 'Very High'
    
    def _generate_recommendations(self, scores):
        """Generate risk mitigation recommendations"""
        recommendations = []
        
        if scores['location'] > 50:
            recommendations.append('Consider location-specific insurance')
        
        if scores['legal'] > 50:
            recommendations.append('Conduct thorough legal due diligence')
            recommendations.append('Verify clear title with government registry')
        
        if scores['market'] > 60:
            recommendations.append('Diversify property portfolio')
            recommendations.append('Monitor market trends closely')
        
        if scores['document'] > 50:
            recommendations.append('Request additional documentation')
            recommendations.append('Conduct third-party verification')
        
        if scores['financial'] > 50:
            recommendations.append('Review pricing and valuation')
            recommendations.append('Assess liquidity requirements')
        
        return recommendations


# Singleton instance
risk_scorer = RiskScorer()
