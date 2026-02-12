"""
Property Valuation Model
AI-based property price prediction and valuation
"""

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import pickle


class ValuationModel:
    """ML-based property valuation and price prediction"""
    
    def __init__(self):
        # Initialize models
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        
        # Train with synthetic data (in production, use real market data)
        self._train_model()
    
    def _train_model(self):
        """Train valuation model with synthetic data"""
        # Generate synthetic training data
        # Features: [area_sqft, bedrooms, location_tier, age_years, amenities_count]
        np.random.seed(42)
        n_samples = 1000
        
        X_train = np.column_stack([
            np.random.uniform(500, 5000, n_samples),  # area
            np.random.randint(1, 6, n_samples),  # bedrooms
            np.random.randint(1, 4, n_samples),  # location tier
            np.random.uniform(0, 50, n_samples),  # age
            np.random.randint(0, 20, n_samples)  # amenities
        ])
        
        # Generate prices based on features (simplified formula)
        y_train = (
            X_train[:, 0] * 5000 +  # area factor
            X_train[:, 1] * 500000 +  # bedroom factor
            (4 - X_train[:, 2]) * 1000000 +  # location factor
            -X_train[:, 3] * 10000 +  # age depreciation
            X_train[:, 4] * 50000  # amenities factor
        )
        
        # Add some noise
        y_train += np.random.normal(0, 500000, n_samples)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
    
    def predict_valuation(self, property_data):
        """
        Predict property valuation
        
        Args:
            property_data: Dict with property features
        
        Returns:
            Dict with valuation estimate and confidence interval
        """
        # Extract features
        features = self._extract_features(property_data)
        
        # Scale features
        features_scaled = self.scaler.transform([features])
        
        # Predict
        predicted_value = self.model.predict(features_scaled)[0]
        
        # Calculate confidence interval using tree predictions
        tree_predictions = [tree.predict(features_scaled)[0] 
                          for tree in self.model.estimators_]
        
        std_dev = np.std(tree_predictions)
        confidence_interval = {
            'lower': predicted_value - 1.96 * std_dev,
            'upper': predicted_value + 1.96 * std_dev
        }
        
        # Calculate per-token value
        total_tokens = property_data.get('total_tokens', 1000)
        token_value = predicted_value / total_tokens
        
        return {
            'predicted_value': round(predicted_value, 2),
            'confidence_interval': {
                'lower': round(confidence_interval['lower'], 2),
                'upper': round(confidence_interval['upper'], 2)
            },
            'token_value': round(token_value, 2),
            'valuation_per_sqft': round(predicted_value / property_data.get('area_sqft', 1), 2),
            'confidence_score': self._calculate_confidence(std_dev, predicted_value),
            'comparable_properties': self._find_comparables(property_data)
        }
    
    def _extract_features(self, property_data):
        """Extract numerical features from property data"""
        # Map location to tier
        location_tier = self._get_location_tier(property_data.get('city', ''))
        
        features = [
            property_data.get('area_sqft', 1000),
            property_data.get('bedrooms', 2),
            location_tier,
            property_data.get('age_years', 5),
            len(property_data.get('amenities', []))
        ]
        
        return features
    
    def _get_location_tier(self, city):
        """Map city to tier (1=best, 3=lowest)"""
        city = city.lower()
        
        tier1 = ['mumbai', 'delhi', 'bangalore', 'hyderabad', 'chennai', 'pune']
        tier2 = ['ahmedabad', 'jaipur', 'lucknow', 'kochi', 'indore', 'bhopal']
        
        if any(c in city for c in tier1):
            return 1
        elif any(c in city for c in tier2):
            return 2
        else:
            return 3
    
    def _calculate_confidence(self, std_dev, predicted_value):
        """Calculate confidence score (0-100)"""
        if predicted_value == 0:
            return 0
        
        # Coefficient of variation
        cv = (std_dev / predicted_value) * 100
        
        # Convert to confidence (lower CV = higher confidence)
        confidence = max(0, 100 - cv)
        
        return round(confidence, 2)
    
    def _find_comparables(self, property_data):
        """Find comparable properties (simulated)"""
        # In production, query database for similar properties
        # For demo, return synthetic comparables
        
        base_value = property_data.get('total_value', 5000000)
        
        comparables = []
        for i in range(3):
            variation = np.random.uniform(0.9, 1.1)
            comparables.append({
                'id': f'PROP-{1000 + i}',
                'value': round(base_value * variation, 2),
                'area_sqft': property_data.get('area_sqft', 1000) * np.random.uniform(0.95, 1.05),
                'similarity_score': round(np.random.uniform(0.85, 0.98), 2)
            })
        
        return comparables
    
    def calculate_rental_yield(self, property_value, annual_rental_income):
        """Calculate rental yield percentage"""
        if property_value == 0:
            return 0
        
        yield_percent = (annual_rental_income / property_value) * 100
        
        # Benchmark against market
        market_avg = 3.5  # Average rental yield in India
        
        return {
            'rental_yield': round(yield_percent, 2),
            'market_average': market_avg,
            'performance': 'above_market' if yield_percent > market_avg else 'below_market'
        }
    
    def calculate_roi_projection(self, property_value, annual_rental_income, 
                                 appreciation_rate=5.0, years=5):
        """
        Calculate ROI projection
        
        Args:
            property_value: Current property value
            annual_rental_income: Annual rental income
            appreciation_rate: Expected annual appreciation (%)
            years: Projection period
        
        Returns:
            Dict with ROI projections
        """
        projections = []
        
        current_value = property_value
        total_rental = 0
        
        for year in range(1, years + 1):
            # Apply appreciation
            current_value *= (1 + appreciation_rate / 100)
            total_rental += annual_rental_income
            
            # Calculate cumulative ROI
            total_return = (current_value - property_value) + total_rental
            roi = (total_return / property_value) * 100
            
            projections.append({
                'year': year,
                'property_value': round(current_value, 2),
                'cumulative_rental': round(total_rental, 2),
                'total_return': round(total_return, 2),
                'roi_percent': round(roi, 2)
            })
        
        return {
            'projections': projections,
            'final_roi': round(projections[-1]['roi_percent'], 2),
            'assumptions': {
                'appreciation_rate': appreciation_rate,
                'rental_income': annual_rental_income
            }
        }


# Singleton instance
valuation_model = ValuationModel()
