"""
Storage Manager - Handle file uploads and encryption
"""

import os
import hashlib
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from werkzeug.utils import secure_filename


class StorageManager:
    """Manage file storage with encryption"""
    
    def __init__(self):
        self.upload_folder = os.getenv('UPLOAD_FOLDER', './storage/uploads')
        self.encrypted_folder = os.getenv('ENCRYPTED_FOLDER', './storage/encrypted')
        self.kyc_folder = os.path.join(self.upload_folder, 'kyc')
        self.rwa_folder = os.path.join(self.upload_folder, 'rwa')
        
        # Create directories
        os.makedirs(self.upload_folder, exist_ok=True)
        os.makedirs(self.encrypted_folder, exist_ok=True)
        os.makedirs(self.kyc_folder, exist_ok=True)
        os.makedirs(self.rwa_folder, exist_ok=True)
        
        # Encryption key (in production: use proper key management)
        self.key = get_random_bytes(32)
    
    def save_file(self, file, property_id, doc_type):
        """Save and encrypt uploaded file"""
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save original file
        file_path = os.path.join(self.upload_folder, f"{property_id}_{doc_type}_{timestamp}_{filename}")
        file.save(file_path)
        
        # Encrypt file
        encrypted_path = self._encrypt_file(file_path, property_id, doc_type)
        
        return {
            'file_path': file_path,
            'encrypted_path': encrypted_path,
            'filename': filename,
            'timestamp': self.get_timestamp()
        }
    
    def save_kyc_document(self, file, user_id, doc_type):
        """Save KYC document"""
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save to KYC folder
        file_path = os.path.join(self.kyc_folder, f"{user_id}_{doc_type}_{timestamp}_{filename}")
        file.save(file_path)
        
        return {
            'file_path': file_path,
            'filename': filename,
            'timestamp': self.get_timestamp()
        }
    
    def save_rwa_document(self, file, property_id, doc_type):
        """Save RWA document"""
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save to RWA folder
        file_path = os.path.join(self.rwa_folder, f"{property_id}_{doc_type}_{timestamp}_{filename}")
        file.save(file_path)
        
        return {
            'file_path': file_path,
            'filename': filename,
            'timestamp': self.get_timestamp()
        }
    
    def _encrypt_file(self, file_path, property_id, doc_type):
        """Encrypt file using AES"""
        try:
            # Read file
            with open(file_path, 'rb') as f:
                data = f.read()
            
            # Create cipher
            cipher = AES.new(self.key, AES.MODE_EAX)
            ciphertext, tag = cipher.encrypt_and_digest(data)
            
            # Save encrypted file
            encrypted_filename = f"{property_id}_{doc_type}_encrypted.bin"
            encrypted_path = os.path.join(self.encrypted_folder, encrypted_filename)
            
            with open(encrypted_path, 'wb') as f:
                f.write(cipher.nonce)
                f.write(tag)
                f.write(ciphertext)
            
            return encrypted_path
        except Exception as e:
            print(f"Encryption error: {e}")
            return None
    
    def decrypt_file(self, encrypted_path):
        """Decrypt file"""
        try:
            with open(encrypted_path, 'rb') as f:
                nonce = f.read(16)
                tag = f.read(16)
                ciphertext = f.read()
            
            cipher = AES.new(self.key, AES.MODE_EAX, nonce=nonce)
            data = cipher.decrypt_and_verify(ciphertext, tag)
            
            return data
        except Exception as e:
            print(f"Decryption error: {e}")
            return None
    
    def get_timestamp(self):
        """Get current timestamp"""
        return datetime.now().isoformat()


storage_manager = StorageManager()
