"""
Algorand Client - Core blockchain interaction module
Handles TestNet connections, transactions, and smart contract deployments
"""

from algosdk import account, mnemonic
from algosdk.v2client import algod, indexer
from algosdk.transaction import (
    AssetConfigTxn,
    AssetTransferTxn,
    ApplicationCreateTxn,
    ApplicationCallTxn,
    PaymentTxn,
    OnComplete,
    StateSchema,
    wait_for_confirmation
)
from algosdk.logic import get_application_address
import os
from dotenv import load_dotenv

load_dotenv()


class AlgorandClient:
    """Main Algorand blockchain client for TestNet operations"""
    
    def __init__(self):
        # Initialize Algorand clients
        self.algod_address = os.getenv('ALGOD_ADDRESS', 'https://testnet-api.algonode.cloud')
        self.algod_token = os.getenv('ALGOD_TOKEN', '')
        self.indexer_address = os.getenv('INDEXER_ADDRESS', 'https://testnet-idx.algonode.cloud')
        self.indexer_token = os.getenv('INDEXER_TOKEN', '')
        
        self.algod_client = algod.AlgodClient(self.algod_token, self.algod_address)
        self.indexer_client = indexer.IndexerClient(self.indexer_token, self.indexer_address)
        
        # Load admin account
        admin_mnemonic = os.getenv('ADMIN_MNEMONIC')
        if admin_mnemonic and admin_mnemonic != 'your 25 word mnemonic here':
            self.admin_private_key = mnemonic.to_private_key(admin_mnemonic)
            self.admin_address = account.address_from_private_key(self.admin_private_key)
        else:
            self.admin_private_key = None
            self.admin_address = None
    
    def create_account(self):
        """Generate a new Algorand account"""
        private_key, address = account.generate_account()
        account_mnemonic = mnemonic.from_private_key(private_key)
        return {
            'address': address,
            'private_key': private_key,
            'mnemonic': account_mnemonic
        }
    
    def get_balance(self, address):
        """Get account balance in microAlgos"""
        try:
            account_info = self.algod_client.account_info(address)
            return account_info.get('amount', 0)
        except Exception as e:
            print(f"Error getting balance: {e}")
            return 0
    
    def create_property_asset(self, creator_private_key, property_data):
        """
        Create an Algorand Standard Asset (ASA) for a property
        
        Args:
            creator_private_key: Private key of the property owner
            property_data: Dict with property details (name, total_value, total_tokens, etc.)
        
        Returns:
            Asset ID of the created token
        """
        creator_address = account.address_from_private_key(creator_private_key)
        
        # Get suggested parameters
        params = self.algod_client.suggested_params()
        
        # Create asset configuration transaction
        txn = AssetConfigTxn(
            sender=creator_address,
            sp=params,
            total=int(property_data['total_tokens']),  # Total token supply
            default_frozen=False,
            unit_name=property_data.get('unit_name', 'PROP'),
            asset_name=property_data['name'][:32],  # Max 32 chars
            manager=creator_address,
            reserve=creator_address,
            freeze=creator_address,
            clawback=creator_address,
            url=property_data.get('url', '')[:96],  # Max 96 chars
            decimals=0,  # Whole tokens only
            note=property_data.get('note', '').encode()
        )
        
        # Sign and send transaction
        signed_txn = txn.sign(creator_private_key)
        tx_id = self.algod_client.send_transaction(signed_txn)
        
        # Wait for confirmation
        confirmed_txn = wait_for_confirmation(self.algod_client, tx_id, 4)
        asset_id = confirmed_txn['asset-index']
        
        print(f"Property Asset Created! Asset ID: {asset_id}")
        print(f"View on AlgoExplorer: https://testnet.algoexplorer.io/asset/{asset_id}")
        
        return asset_id
    
    def opt_in_asset(self, account_private_key, asset_id):
        """Opt-in to receive an asset"""
        account_address = account.address_from_private_key(account_private_key)
        params = self.algod_client.suggested_params()
        
        txn = AssetTransferTxn(
            sender=account_address,
            sp=params,
            receiver=account_address,
            amt=0,
            index=asset_id
        )
        
        signed_txn = txn.sign(account_private_key)
        tx_id = self.algod_client.send_transaction(signed_txn)
        wait_for_confirmation(self.algod_client, tx_id, 4)
        
        print(f"Account {account_address} opted in to asset {asset_id}")
        return tx_id
    
    def transfer_asset(self, sender_private_key, receiver_address, asset_id, amount):
        """Transfer property tokens between accounts"""
        sender_address = account.address_from_private_key(sender_private_key)
        params = self.algod_client.suggested_params()
        
        txn = AssetTransferTxn(
            sender=sender_address,
            sp=params,
            receiver=receiver_address,
            amt=int(amount),
            index=asset_id
        )
        
        signed_txn = txn.sign(sender_private_key)
        tx_id = self.algod_client.send_transaction(signed_txn)
        confirmed_txn = wait_for_confirmation(self.algod_client, tx_id, 4)
        
        print(f"Transferred {amount} tokens of asset {asset_id}")
        print(f"View on AlgoExplorer: https://testnet.algoexplorer.io/tx/{tx_id}")
        
        return tx_id
    
    def deploy_smart_contract(self, creator_private_key, approval_program, clear_program, 
                             global_schema, local_schema, app_args=None):
        """
        Deploy a PyTeal smart contract to Algorand
        
        Args:
            creator_private_key: Account deploying the contract
            approval_program: Compiled approval program (bytes)
            clear_program: Compiled clear program (bytes)
            global_schema: Global state schema
            local_schema: Local state schema
            app_args: Optional application arguments
        
        Returns:
            Application ID
        """
        creator_address = account.address_from_private_key(creator_private_key)
        params = self.algod_client.suggested_params()
        
        txn = ApplicationCreateTxn(
            sender=creator_address,
            sp=params,
            on_complete=OnComplete.NoOpOC,
            approval_program=approval_program,
            clear_program=clear_program,
            global_schema=global_schema,
            local_schema=local_schema,
            app_args=app_args or []
        )
        
        signed_txn = txn.sign(creator_private_key)
        tx_id = self.algod_client.send_transaction(signed_txn)
        confirmed_txn = wait_for_confirmation(self.algod_client, tx_id, 4)
        
        app_id = confirmed_txn['application-index']
        app_address = get_application_address(app_id)
        
        print(f"Smart Contract Deployed! App ID: {app_id}")
        print(f"App Address: {app_address}")
        print(f"View on AlgoExplorer: https://testnet.algoexplorer.io/application/{app_id}")
        
        return app_id
    
    def call_smart_contract(self, caller_private_key, app_id, app_args=None, 
                           foreign_assets=None, accounts=None):
        """Call a deployed smart contract"""
        caller_address = account.address_from_private_key(caller_private_key)
        params = self.algod_client.suggested_params()
        
        txn = ApplicationCallTxn(
            sender=caller_address,
            sp=params,
            index=app_id,
            on_complete=OnComplete.NoOpOC,
            app_args=app_args or [],
            foreign_assets=foreign_assets or [],
            accounts=accounts or []
        )
        
        signed_txn = txn.sign(caller_private_key)
        tx_id = self.algod_client.send_transaction(signed_txn)
        confirmed_txn = wait_for_confirmation(self.algod_client, tx_id, 4)
        
        print(f"Smart contract called successfully")
        print(f"View on AlgoExplorer: https://testnet.algoexplorer.io/tx/{tx_id}")
        
        return tx_id
    
    def get_asset_info(self, asset_id):
        """Get information about an asset"""
        try:
            asset_info = self.algod_client.asset_info(asset_id)
            return asset_info
        except Exception as e:
            print(f"Error getting asset info: {e}")
            return None
    
    def get_account_assets(self, address):
        """Get all assets held by an account"""
        try:
            account_info = self.algod_client.account_info(address)
            return account_info.get('assets', [])
        except Exception as e:
            print(f"Error getting account assets: {e}")
            return []


# Singleton instance
algorand_client = AlgorandClient()
