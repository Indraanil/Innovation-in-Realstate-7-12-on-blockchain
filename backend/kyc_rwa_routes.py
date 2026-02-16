"""
KYC and RWA API Routes
Enhanced verification endpoints for BharatPropChain
"""

from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.kyc_manager import kyc_manager, KYCDocumentType
from backend.rwa_verifier import rwa_verifier, PropertyDocumentType
from backend.storage import storage_manager


def register_kyc_rwa_routes(app):
    """Register KYC and RWA routes with Flask app"""
    
    # ============= Enhanced KYC Endpoints =============
    
    @app.route('/api/kyc/upload-document', methods=['POST'])
    @jwt_required()
    def upload_kyc_document():
        """Upload KYC document (Aadhaar, PAN, Selfie)"""
        user_id = get_jwt_identity()
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        doc_type = request.form.get('doc_type')
        
        if doc_type not in [KYCDocumentType.AADHAAR.value, KYCDocumentType.PAN.value, KYCDocumentType.SELFIE.value]:
            return jsonify({'error': 'Invalid document type'}), 400
        
        # Save document
        file_info = storage_manager.save_kyc_document(file, user_id, doc_type)
        
        # Upload to KYC manager
        result = kyc_manager.upload_document(user_id, doc_type, file_info['file_path'], file_info)
        
        # Auto-verify if enabled
        if kyc_manager.auto_verify:
            if doc_type == KYCDocumentType.AADHAAR.value:
                # Simulate OCR extraction
                aadhaar_data = {
                    'aadhaar_number': '1234 5678 9012',
                    'name': 'Demo User',
                    'dob': '1990-01-01',
                    'address': 'Demo Address'
                }
                kyc_manager.verify_aadhaar_document(user_id, aadhaar_data)
            elif doc_type == KYCDocumentType.PAN.value:
                pan_data = {
                    'pan_number': 'ABCDE1234F',
                    'name': 'Demo User'
                }
                kyc_manager.verify_pan_document(user_id, pan_data)
            elif doc_type == KYCDocumentType.SELFIE.value:
                kyc_manager.perform_face_matching(user_id)
        
        return jsonify(result)
    
    @app.route('/api/kyc/submit', methods=['POST'])
    @jwt_required()
    def submit_kyc():
        """Submit KYC for review"""
        user_id = get_jwt_identity()
        result = kyc_manager.submit_for_review(user_id)
        return jsonify(result)
    
    @app.route('/api/kyc/status', methods=['GET'])
    @jwt_required()
    def get_kyc_status_api():
        """Get KYC status"""
        user_id = get_jwt_identity()
        status = kyc_manager.get_kyc_status(user_id)
        progress = kyc_manager.get_verification_progress(user_id)
        return jsonify({**status, 'progress': progress})
    
    # ============= RWA Verification Endpoints =============
    
    @app.route('/api/rwa/initialize', methods=['POST'])
    @jwt_required()
    def initialize_rwa():
        """Initialize RWA verification for a property"""
        user_id = get_jwt_identity()
        data = request.json
        property_id = data.get('property_id')
        
        if not property_id:
            return jsonify({'error': 'Property ID required'}), 400
        
        result = rwa_verifier.initialize_rwa(property_id, user_id)
        return jsonify({'success': True, 'rwa_record': result})
    
    @app.route('/api/rwa/upload-document', methods=['POST'])
    @jwt_required()
    def upload_rwa_document():
        """Upload RWA document (Title Deed, EC, Tax Receipt)"""
        user_id = get_jwt_identity()
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        property_id = request.form.get('property_id')
        doc_type = request.form.get('doc_type')
        
        if not property_id:
            return jsonify({'error': 'Property ID required'}), 400
        
        valid_doc_types = [PropertyDocumentType.TITLE_DEED.value, 
                          PropertyDocumentType.ENCUMBRANCE_CERT.value,
                          PropertyDocumentType.TAX_RECEIPT.value]
        
        if doc_type not in valid_doc_types:
            return jsonify({'error': 'Invalid document type'}), 400
        
        # Save document
        file_info = storage_manager.save_rwa_document(file, property_id, doc_type)
        
        # Upload to RWA verifier
        result = rwa_verifier.upload_document(property_id, doc_type, file_info['file_path'], file_info)
        
        # Auto-verify if enabled
        if rwa_verifier.auto_verify:
            if doc_type == PropertyDocumentType.TITLE_DEED.value:
                deed_data = {
                    'deed_number': f'DEED-{property_id}',
                    'owner_name': 'Demo Owner',
                    'property_address': 'Demo Address',
                    'registration_date': '2020-01-15'
                }
                rwa_verifier.verify_title_deed(property_id, deed_data)
            elif doc_type == PropertyDocumentType.ENCUMBRANCE_CERT.value:
                ec_data = {'certificate_number': f'EC-{property_id}'}
                rwa_verifier.verify_encumbrance_certificate(property_id, ec_data)
            elif doc_type == PropertyDocumentType.TAX_RECEIPT.value:
                tax_data = {'receipt_number': f'TAX-{property_id}', 'payment_year': '2025-26'}
                rwa_verifier.verify_tax_receipt(property_id, tax_data)
        
        return jsonify(result)
    
    @app.route('/api/rwa/submit', methods=['POST'])
    @jwt_required()
    def submit_rwa():
        """Submit RWA for verification"""
        user_id = get_jwt_identity()
        data = request.json
        property_id = data.get('property_id')
        
        if not property_id:
            return jsonify({'error': 'Property ID required'}), 400
        
        # Validate ownership and perform checks
        rwa_verifier.validate_ownership(property_id, user_id)
        rwa_verifier.check_legal_compliance(property_id)
        
        result = rwa_verifier.submit_for_verification(property_id)
        return jsonify(result)
    
    @app.route('/api/rwa/status/<property_id>', methods=['GET'])
    def get_rwa_status_api(property_id):
        """Get RWA verification status"""
        status = rwa_verifier.get_rwa_status(property_id)
        return jsonify(status)
