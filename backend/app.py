"""
BharatPropChain Backend API
Flask REST API for property tokenization platform
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
import os
import sys
from datetime import timedelta
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules
from blockchain.algorand_client import algorand_client
from ai.ocr_processor import ocr_processor
from ai.fraud_detector import fraud_detector
from ai.risk_scorer import risk_scorer
from ai.valuation_model import valuation_model
from compliance.kyc_verifier import kyc_verifier
from compliance.tax_reporter import tax_reporter
from backend.storage import storage_manager
from backend.business.fee_calculator import fee_calculator
from backend.compliance_engine import compliance_engine, VerificationStatus
from backend.kyc_manager import kyc_manager, KYCDocumentType
from backend.rwa_verifier import rwa_verifier, PropertyDocumentType
from backend.kyc_rwa_routes import register_kyc_rwa_routes
from backend.geocoding import geocoding_service, get_city_coordinates

load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Enable CORS
CORS(app)

# Initialize JWT
jwt = JWTManager(app)

# In-memory database (for hackathon - use real DB in production)
users_db = {}
properties_db = {}
transactions_db = []

# Register KYC and RWA routes
register_kyc_rwa_routes(app)


# ============= Authentication Endpoints =============

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.json
    
    user_id = data.get('wallet_address')
    if not user_id:
        return jsonify({'error': 'Wallet address required'}), 400
    
    if user_id in users_db:
        return jsonify({'error': 'User already exists'}), 400
    
    users_db[user_id] = {
        'wallet_address': user_id,
        'name': data.get('name'),
        'email': data.get('email'),
        'kyc_status': 'pending',
        'properties': [],
        'portfolio': {},  # Track owned tokens: {property_id: amount}
        'transactions': []
    }
    
    # Create access token
    access_token = create_access_token(identity=user_id)
    
    return jsonify({
        'success': True,
        'user_id': user_id,
        'access_token': access_token
    }), 201


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login with wallet address"""
    data = request.json
    wallet_address = data.get('wallet_address')
    
    if wallet_address not in users_db:
        return jsonify({'error': 'User not found'}), 404
    
    access_token = create_access_token(identity=wallet_address)
    
    return jsonify({
        'success': True,
        'access_token': access_token,
        'user': users_db[wallet_address]
    })


# ============= KYC Endpoints =============

@app.route('/api/kyc/verify', methods=['POST'])
@jwt_required()
def verify_kyc():
    """Complete KYC verification"""
    user_id = get_jwt_identity()
    data = request.json
    
    # Verify Aadhaar
    aadhaar_result = kyc_verifier.verify_aadhaar(
        data.get('aadhaar_number'),
        data.get('name'),
        data.get('dob')
    )
    
    # Verify PAN
    pan_result = kyc_verifier.verify_pan(
        data.get('pan_number'),
        data.get('name')
    )
    
    # AML screening
    aml_result = kyc_verifier.perform_aml_screening({'user_id': user_id})
    
    # Complete KYC
    kyc_result = kyc_verifier.complete_kyc(
        user_id, aadhaar_result, pan_result, aml_result
    )
    
    if kyc_result['success']:
        users_db[user_id]['kyc_status'] = 'verified'
        
        # Add to compliance engine whitelist
        compliance_engine.add_to_kyc_whitelist(user_id, kyc_result)
    
    return jsonify(kyc_result)


@app.route('/api/kyc/status', methods=['GET'])
@jwt_required()
def get_kyc_status():
    """Get KYC status"""
    user_id = get_jwt_identity()
    status = kyc_verifier.check_kyc_status(user_id)
    return jsonify(status)


# ============= Property Management Endpoints =============

@app.route('/api/properties/register', methods=['POST'])
@jwt_required()
def register_property():
    """Register a new property"""
    user_id = get_jwt_identity()
    
    # Ensure user exists in database (in case of server restart or session issues)
    if user_id not in users_db:
        users_db[user_id] = {
            'wallet_address': user_id,
            'name': 'User',
            'email': f'{user_id[:8]}@demo.user',
            'kyc_status': 'pending',
            'properties': [],
            'transactions': []
        }
    
    # Check KYC status (Mandatory for Institutional Issuance)
    if users_db.get(user_id, {}).get('kyc_status') != 'verified':
        # Re-check via kyc_manager for robustness
        if not kyc_manager.is_kyc_verified(user_id):
            return jsonify({
                'success': False,
                'error': 'Institutional Access Restricted: Complete the Identity Trust Protocol (KYC) to register assets.'
            }), 403
    
    data = request.json
    
    # Generate property ID
    property_id = f"PROP-{len(properties_db) + 1001}"
    
    # Initialize verification workflow
    workflow = compliance_engine.initialize_verification_workflow(property_id, user_id)
    
    # Get or validate coordinates
    coordinates = None
    lat = data.get('latitude')
    lng = data.get('longitude')
    
    if lat and lng:
        # Use provided coordinates
        coordinates = {'lat': float(lat), 'lng': float(lng)}
    elif data.get('city'):
        # Fallback to city-level coordinates
        city_coords = get_city_coordinates(data.get('city'))
        if city_coords:
            coordinates = city_coords
    
    # Store property data
    property_data = {
        'property_id': property_id,
        'owner': user_id,
        'name': data.get('name'),
        'type': data.get('type'),
        'location': data.get('location'),
        'city': data.get('city'),
        'state': data.get('state'),
        'pincode': data.get('pincode'),
        'full_address': data.get('full_address', ''),
        'coordinates': coordinates,  # Geographic coordinates
        'area_sqft': data.get('area_sqft'),
        'total_value': data.get('total_value'),
        'total_tokens': data.get('total_tokens', 1000),
        'available_tokens': data.get('total_tokens', 1000),  # Track inventory
        'documents': [],
        'status': 'pending_verification',
        'asset_id': None,
        'workflow_status': workflow['status']
    }
    
    properties_db[property_id] = property_data
    users_db[user_id]['properties'].append(property_id)
    
    return jsonify({
        'success': True,
        'property_id': property_id,
        'property': property_data
    }), 201


@app.route('/api/properties/<property_id>/upload-document', methods=['POST'])
@jwt_required()
def upload_document(property_id):
    """Upload property document"""
    user_id = get_jwt_identity()
    
    if property_id not in properties_db:
        return jsonify({'error': 'Property not found'}), 404
    
    if properties_db[property_id]['owner'] != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Handle file upload
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    doc_type = request.form.get('doc_type', 'property_deed')
    
    # Save file
    file_info = storage_manager.save_file(file, property_id, doc_type)
    
    # Perform OCR
    ocr_result = ocr_processor.extract_property_deed_info(file_info['file_path'])
    
    # Fraud detection
    fraud_analysis = fraud_detector.analyze_document(
        file_info['file_path'],
        ocr_result
    )
    
    # Generate document hash
    doc_hash = fraud_detector.generate_document_hash(file_info['file_path'])
    
    # Store document info
    doc_info = {
        'doc_type': doc_type,
        'file_path': file_info['encrypted_path'],
        'file_hash': doc_hash,
        'ocr_data': ocr_result,
        'fraud_analysis': fraud_analysis,
        'uploaded_at': file_info['timestamp']
    }
    
    properties_db[property_id]['documents'].append(doc_info)
    
    return jsonify({
        'success': True,
        'document': doc_info,
        'fraud_analysis': fraud_analysis
    })


@app.route('/api/properties/<property_id>/verify', methods=['POST'])
@jwt_required()
def verify_property(property_id):
    """Run AI verification on property"""
    user_id = get_jwt_identity()
    
    if property_id not in properties_db:
        return jsonify({'error': 'Property not found'}), 404
    
    property_data = properties_db[property_id]
    
    # Mark documents as uploaded (even if none were uploaded, for demo purposes)
    compliance_engine.update_workflow_status(
        property_id,
        VerificationStatus.DOCUMENTS_UPLOADED,
        {'documents_count': len(property_data.get('documents', []))}
    )
    
    # Get fraud analysis from documents
    fraud_analysis = None
    if property_data['documents']:
        fraud_analysis = property_data['documents'][0]['fraud_analysis']
    
    # Calculate risk score
    risk_score = risk_scorer.calculate_risk_score(property_data, fraud_analysis)
    
    # Get valuation
    valuation = valuation_model.predict_valuation(property_data)
    
    # Update property
    properties_db[property_id]['risk_score'] = risk_score
    properties_db[property_id]['valuation'] = valuation
    properties_db[property_id]['status'] = 'verified'
    
    # Update compliance workflow to AI_VERIFIED
    compliance_engine.update_workflow_status(
        property_id,
        VerificationStatus.AI_VERIFIED,
        {'risk_score': risk_score, 'valuation': valuation}
    )
    
    return jsonify({
        'success': True,
        'risk_score': risk_score,
        'valuation': valuation
    })


@app.route('/api/properties/<property_id>/tokenize', methods=['POST'])
@jwt_required()
def tokenize_property(property_id):
    """Mint property tokens on Algorand"""
    user_id = get_jwt_identity()
    
    if property_id not in properties_db:
        return jsonify({'error': 'Property not found'}), 404
    
    property_data = properties_db[property_id]
    
    if property_data['owner'] != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if property_data['status'] != 'verified':
        return jsonify({'error': 'Property must be verified first'}), 400
    
    # Check tokenization eligibility (KYC + RWA verification)
    eligibility = compliance_engine.check_tokenization_eligibility(property_id)
    if not eligibility['eligible']:
        return jsonify({
            'error': 'Property not eligible for tokenization',
            'missing_requirements': eligibility['missing_requirements'],
            'details': eligibility
        }), 400
    
    # Calculate tokenization fee
    fee = fee_calculator.calculate_tokenization_fee(property_data['total_value'])
    
    try:
        # Create property asset on Algorand
        # Note: In production, use actual user's private key
        # For demo, using admin account
        asset_data = {
            'name': property_data['name'][:32],
            'total_tokens': property_data['total_tokens'],
            'unit_name': 'PROP',
            'url': f'https://bharatpropchain.com/property/{property_id}',
            'note': f'Property: {property_id}'
        }
        
        # This would use the user's wallet in production
        # For demo, we'll simulate
        asset_id = f"ASA-{property_id}"  # Simulated
        
        properties_db[property_id]['asset_id'] = asset_id
        properties_db[property_id]['status'] = 'tokenized'
        properties_db[property_id]['tokenization_fee'] = fee
        
        # Update compliance workflow
        compliance_engine.update_workflow_status(
            property_id,
            VerificationStatus.TOKENIZED,
            {'asset_id': asset_id, 'fee': fee}
        )
        
        return jsonify({
            'success': True,
            'asset_id': asset_id,
            'explorer_url': f'https://testnet.algoexplorer.io/asset/{asset_id}',
            'fee': fee
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/properties', methods=['GET'])
def get_properties():
    """Get all properties (marketplace)"""
    # For demo/testing: return all properties
    # In production: return only tokenized: [p for p in properties_db.values() if p.get('status') == 'tokenized']
    all_properties = list(properties_db.values())
    return jsonify({'properties': all_properties})


@app.route('/api/properties/<property_id>', methods=['GET'])
def get_property(property_id):
    """Get property details"""
    if property_id not in properties_db:
        return jsonify({'error': 'Property not found'}), 404
    
    property_data = properties_db[property_id]
    
    # Add success flag for consistency
    return jsonify({
        'success': True,
        'property': property_data
    })


@app.route('/api/properties/nearby/<lat>/<lng>', methods=['GET'])
def get_nearby_properties(lat, lng):
    """Get properties near a location"""
    try:
        center_lat = float(lat)
        center_lng = float(lng)
        radius_km = float(request.args.get('radius', 50))  # Default 50km
        
        nearby_properties = []
        
        for prop in properties_db.values():
            if prop.get('coordinates') and prop.get('status') == 'tokenized':
                distance = geocoding_service.calculate_distance(
                    center_lat, center_lng,
                    prop['coordinates']['lat'],
                    prop['coordinates']['lng']
                )
                
                if distance <= radius_km:
                    prop_with_distance = prop.copy()
                    prop_with_distance['distance_km'] = distance
                    nearby_properties.append(prop_with_distance)
        
        # Sort by distance
        nearby_properties.sort(key=lambda x: x['distance_km'])
        
        return jsonify({
            'success': True,
            'properties': nearby_properties,
            'count': len(nearby_properties)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ============= Trading Endpoints =============

@app.route('/api/trade/buy', methods=['POST'])
@jwt_required()
def buy_tokens():
    """Buy property tokens (KYC-gated)"""
    user_id = get_jwt_identity()
    data = request.json
    
    # Ensure user exists in database
    if user_id not in users_db:
        users_db[user_id] = {
            'wallet_address': user_id,
            'name': 'User',
            'email': f'{user_id[:8]}@demo.user',
            'kyc_status': 'pending',
            'properties': [],
            'portfolio': {},
            'transactions': []
        }
        
    # Auto-verify/Ensure verified for demo/testing purposes
    if not compliance_engine.is_kyc_verified(user_id):
        compliance_engine.add_to_kyc_whitelist(user_id, {'type': 'auto_demo_verify'})
        if user_id in users_db:
            users_db[user_id]['kyc_status'] = 'verified'
    
    property_id = data.get('property_id')
    token_amount = data.get('token_amount')
    
    if property_id not in properties_db:
        return jsonify({'error': 'Property not found'}), 404
    
    property_data = properties_db[property_id]
    
    # Calculate price first
    token_value = property_data['total_value'] / property_data['total_tokens']
    total_price = token_value * token_amount
    
    # Check trading eligibility (KYC + AML limits)
    eligibility = compliance_engine.check_trading_eligibility(
        user_id, property_id, total_price
    )
    
    if not eligibility['eligible']:
        return jsonify({
            'error': 'Trading not allowed',
            'issues': eligibility['issues'],
            'kyc_status': eligibility['kyc_status']
        }), 403
    
    # Calculate transaction fee (price already calculated above)
    fee = fee_calculator.calculate_transaction_fee(total_price)
    
    # Inventory Check
    current_available = property_data.get('available_tokens', property_data['total_tokens'])
    if current_available < token_amount:
         return jsonify({'error': f'Not enough tokens available. Only {current_available} left.'}), 400

    # EXECUTE TRANSACTION (Atomic-ish)
    # 1. Deduct from inventory
    properties_db[property_id]['available_tokens'] = current_available - token_amount
    
    # 2. Add to user portfolio
    if 'portfolio' not in users_db[user_id]:
        users_db[user_id]['portfolio'] = {}
        
    current_holdings = users_db[user_id]['portfolio'].get(property_id, 0)
    users_db[user_id]['portfolio'][property_id] = current_holdings + token_amount

    # Record transaction
    transaction = {
        'txn_id': f"TXN-{len(transactions_db) + 1}",
        'type': 'buy',
        'buyer': user_id,
        'seller': 'ISSUER', # Buying from platform/issuer
        'property_id': property_id,
        'token_amount': token_amount,
        'price': total_price,
        'fee': fee,
        'payment_ref': data.get('payment_ref'),
        'order_id': data.get('order_id'),
        'timestamp': storage_manager.get_timestamp()
    }
    
    transactions_db.append(transaction)
    users_db[user_id]['transactions'].append(transaction['txn_id'])
    
    # Record in compliance engine for AML tracking
    compliance_engine.record_transaction(user_id, total_price, transaction)
    
    return jsonify({
        'success': True,
        'transaction': transaction,
        'new_balance': users_db[user_id]['portfolio'][property_id],
        'tokens_remaining': properties_db[property_id]['available_tokens']
    })


@app.route('/api/trade/sell', methods=['POST'])
@jwt_required()
def sell_tokens():
    """Sell property tokens (Liquidity/Buyback mode)"""
    user_id = get_jwt_identity()
    data = request.json
    
    property_id = data.get('property_id')
    token_amount = data.get('token_amount')
    
    if not property_id or not token_amount or token_amount <= 0:
        return jsonify({'error': 'Invalid request parameters'}), 400
        
    if property_id not in properties_db:
        return jsonify({'error': 'Property not found'}), 404
        
    # Check ownership
    user_portfolio = users_db.get(user_id, {}).get('portfolio', {})
    current_holdings = user_portfolio.get(property_id, 0)
    
    if current_holdings < token_amount:
        return jsonify({'error': f'Insufficient tokens. You own {current_holdings}.'}), 400
        
    property_data = properties_db[property_id]
    
    # Calculate price (simple linear price for MVP)
    token_value = property_data['total_value'] / property_data['total_tokens']
    total_price = token_value * token_amount
    
    # Calculate fee
    fee = fee_calculator.calculate_transaction_fee(total_price)
    
    # EXECUTE TRANSACTION
    # 1. Deduct from user portfolio
    users_db[user_id]['portfolio'][property_id] = current_holdings - token_amount
    
    # 2. Add back to inventory (Buyback model)
    current_available = property_data.get('available_tokens', property_data['total_tokens'])
    properties_db[property_id]['available_tokens'] = current_available + token_amount
    
    # Record transaction
    transaction = {
        'txn_id': f"TXN-{len(transactions_db) + 1}",
        'type': 'sell',
        'buyer': 'ISSUER', # Selling back to platform
        'seller': user_id,
        'property_id': property_id,
        'token_amount': token_amount,
        'price': total_price,
        'fee': fee,
        'payment_ref': data.get('payment_ref'),
        'order_id': data.get('order_id'),
        'timestamp': storage_manager.get_timestamp()
    }
    
    transactions_db.append(transaction)
    users_db[user_id]['transactions'].append(transaction['txn_id'])
    
    return jsonify({
        'success': True,
        'transaction': transaction,
        'new_balance': users_db[user_id]['portfolio'][property_id]
    })


# ============= Analytics Endpoints =============

@app.route('/api/analytics/platform', methods=['GET'])
def get_platform_analytics():
    """Get platform analytics"""
    total_properties = len(properties_db)
    total_users = len(users_db)
    total_transactions = len(transactions_db)
    
    total_value = sum(p.get('total_value', 0) for p in properties_db.values())
    
    return jsonify({
        'total_properties': total_properties,
        'total_users': total_users,
        'total_transactions': total_transactions,
        'total_value_locked': total_value,
        'properties_by_type': _get_properties_by_type(),
        'recent_transactions': transactions_db[-10:]
    })


def _get_properties_by_type():
    """Helper to get property distribution"""
    types = {}
    for prop in properties_db.values():
        prop_type = prop.get('type', 'unknown')
        types[prop_type] = types.get(prop_type, 0) + 1
    return types


# ============= User Dashboard Endpoints =============

@app.route('/api/user/dashboard', methods=['GET'])
@jwt_required()
def get_user_dashboard():
    """Get user dashboard data"""
    user_id = get_jwt_identity()
    user = users_db.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get user's properties
    user_properties = [properties_db[pid] for pid in user['properties'] 
                      if pid in properties_db]
    
    # Get user's transactions
    user_transactions = [txn for txn in transactions_db 
                        if txn.get('buyer') == user_id or txn.get('seller') == user_id]
    
    return jsonify({
        'user': user,
        'properties': user_properties,
        'transactions': user_transactions
    })


# ============= Health Check =============

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'blockchain': 'Algorand TestNet',
        'version': '1.0.0'
    })


if __name__ == '__main__':
    # Create storage directories
    os.makedirs('storage/uploads', exist_ok=True)
    os.makedirs('storage/encrypted', exist_ok=True)
    
    print("==> BharatPropChain Backend Starting...")
    print("==> API: http://localhost:5000")
    print("==> Blockchain: Algorand TestNet")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
