"""
Fraud Detection Module
ML-based document authenticity and fraud detection
"""

import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestClassifier
import cv2
from datetime import datetime
import hashlib


class FraudDetector:
    """AI-based fraud detection for property documents"""
    
    def __init__(self):
        # Initialize ML models
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        
        # Train with dummy data (in production, use real training data)
        self._train_models()
    
    def _train_models(self):
        """Train models with synthetic data for demo purposes"""
        # Generate synthetic training data
        # Features: [document_age, image_quality, text_confidence, metadata_consistency]
        X_train = np.random.rand(1000, 4)
        y_train = np.random.randint(0, 2, 1000)  # 0: genuine, 1: fraud
        
        # Train classifier
        self.classifier.fit(X_train, y_train)
        
        # Train anomaly detector
        self.anomaly_detector.fit(X_train)
    
    def analyze_document(self, image_path, extracted_data, metadata=None):
        """
        Comprehensive fraud analysis of a document
        
        Args:
            image_path: Path to document image
            extracted_data: OCR extracted data
            metadata: Additional metadata (upload time, source, etc.)
        
        Returns:
            Dict with fraud analysis results
        """
        # Extract features
        features = self._extract_features(image_path, extracted_data, metadata)
        
        # Run fraud checks
        results = {
            'is_authentic': True,
            'confidence_score': 0,
            'fraud_indicators': [],
            'anomaly_score': 0,
            'ml_prediction': 'genuine',
            'risk_level': 'low',
            'checks_performed': []
        }
        
        # 1. Image quality analysis
        quality_check = self._check_image_quality(image_path)
        results['checks_performed'].append('image_quality')
        if not quality_check['passed']:
            results['fraud_indicators'].append('Poor image quality')
            results['is_authentic'] = False
        
        # 2. Metadata consistency
        metadata_check = self._check_metadata_consistency(extracted_data)
        results['checks_performed'].append('metadata_consistency')
        if not metadata_check['passed']:
            results['fraud_indicators'].append('Inconsistent metadata')
        
        # 3. Pattern recognition
        pattern_check = self._check_patterns(extracted_data)
        results['checks_performed'].append('pattern_recognition')
        if not pattern_check['passed']:
            results['fraud_indicators'].append('Suspicious patterns detected')
        
        # 4. ML-based anomaly detection
        anomaly_score = self.anomaly_detector.score_samples([features])[0]
        results['anomaly_score'] = float(anomaly_score)
        results['checks_performed'].append('anomaly_detection')
        
        if anomaly_score < -0.5:  # Threshold for anomaly
            results['fraud_indicators'].append('Anomalous document characteristics')
            results['is_authentic'] = False
        
        # 5. Classification prediction
        prediction = self.classifier.predict([features])[0]
        prediction_proba = self.classifier.predict_proba([features])[0]
        results['ml_prediction'] = 'genuine' if prediction == 0 else 'fraud'
        results['confidence_score'] = float(max(prediction_proba) * 100)
        results['checks_performed'].append('ml_classification')
        
        if prediction == 1:
            results['fraud_indicators'].append('ML model flagged as potential fraud')
            results['is_authentic'] = False
        
        # Calculate overall risk level
        results['risk_level'] = self._calculate_risk_level(results)
        
        return results
    
    def _extract_features(self, image_path, extracted_data, metadata):
        """Extract numerical features for ML models"""
        features = []
        
        # Feature 1: Document age (simulated)
        features.append(np.random.rand())
        
        # Feature 2: Image quality score
        img = cv2.imread(image_path)
        if img is not None:
            # Calculate sharpness using Laplacian variance
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
            features.append(min(sharpness / 1000, 1.0))  # Normalize
        else:
            features.append(0.0)
        
        # Feature 3: Text extraction confidence
        text_confidence = extracted_data.get('confidence', 50) / 100
        features.append(text_confidence)
        
        # Feature 4: Metadata consistency score
        consistency_score = self._calculate_consistency_score(extracted_data)
        features.append(consistency_score)
        
        return features
    
    def _check_image_quality(self, image_path):
        """Check if image quality is sufficient"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                return {'passed': False, 'reason': 'Cannot read image'}
            
            # Check resolution
            height, width = img.shape[:2]
            if height < 500 or width < 500:
                return {'passed': False, 'reason': 'Resolution too low'}
            
            # Check sharpness
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            if sharpness < 100:
                return {'passed': False, 'reason': 'Image too blurry'}
            
            return {'passed': True, 'sharpness': sharpness}
        except Exception as e:
            return {'passed': False, 'reason': str(e)}
    
    def _check_metadata_consistency(self, extracted_data):
        """Check if extracted data is internally consistent"""
        # Check if critical fields are present
        required_fields = ['property_id', 'owner_name']
        missing_fields = [f for f in required_fields if not extracted_data.get(f)]
        
        if missing_fields:
            return {
                'passed': False,
                'reason': f'Missing fields: {", ".join(missing_fields)}'
            }
        
        return {'passed': True}
    
    def _check_patterns(self, extracted_data):
        """Check for known fraud patterns"""
        raw_text = extracted_data.get('raw_text', '')
        
        # Check for suspicious patterns
        suspicious_keywords = ['fake', 'duplicate', 'copy', 'specimen']
        
        for keyword in suspicious_keywords:
            if keyword.lower() in raw_text.lower():
                return {
                    'passed': False,
                    'reason': f'Suspicious keyword found: {keyword}'
                }
        
        return {'passed': True}
    
    def _calculate_consistency_score(self, extracted_data):
        """Calculate how consistent the extracted data is"""
        total_fields = len([k for k in extracted_data.keys() if k != 'raw_text'])
        filled_fields = len([v for k, v in extracted_data.items() 
                           if k != 'raw_text' and v])
        
        if total_fields == 0:
            return 0.0
        
        return filled_fields / total_fields
    
    def _calculate_risk_level(self, results):
        """Calculate overall risk level"""
        fraud_count = len(results['fraud_indicators'])
        
        if fraud_count == 0:
            return 'low'
        elif fraud_count <= 2:
            return 'medium'
        else:
            return 'high'
    
    def generate_document_hash(self, image_path):
        """Generate cryptographic hash of document for verification"""
        try:
            with open(image_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            return file_hash
        except Exception as e:
            print(f"Error generating hash: {e}")
            return None


# Singleton instance
fraud_detector = FraudDetector()
