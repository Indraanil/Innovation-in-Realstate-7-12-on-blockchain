"""
Deploy Smart Contracts to Algorand TestNet
Run this script to deploy all PyTeal contracts
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from blockchain.algorand_client import algorand_client
from algosdk.transaction import StateSchema
from pyteal import compileTeal, Mode
import importlib


def compile_contract(contract_module, contract_name):
    """Compile a PyTeal contract to TEAL"""
    print(f"\n📝 Compiling {contract_name}...")
    
    # Import contract module
    module = importlib.import_module(f'blockchain.contracts.{contract_module}')
    
    # Get approval and clear programs
    approval = module.approval_program()
    clear = module.clear_program()
    
    # Compile to TEAL
    approval_teal = compileTeal(approval, mode=Mode.Application, version=8)
    clear_teal = compileTeal(clear, mode=Mode.Application, version=8)
    
    # Compile TEAL to bytecode
    approval_result = algorand_client.algod_client.compile(approval_teal)
    clear_result = algorand_client.algod_client.compile(clear_teal)
    
    return (
        approval_result['result'].encode(),
        clear_result['result'].encode()
    )


def deploy_contracts():
    """Deploy all smart contracts"""
    print("🚀 BharatPropChain Contract Deployment")
    print("=" * 50)
    
    # Check if admin account is configured
    if not algorand_client.admin_private_key:
        print("\n❌ ERROR: Admin account not configured")
        print("Please set ADMIN_MNEMONIC in .env file")
        print("Get test ALGO from: https://bank.testnet.algorand.network/")
        return
    
    print(f"\n✅ Admin Address: {algorand_client.admin_address}")
    
    # Check balance
    balance = algorand_client.get_balance(algorand_client.admin_address)
    print(f"💰 Balance: {balance / 1000000} ALGO")
    
    if balance < 1000000:  # Less than 1 ALGO
        print("\n⚠️  WARNING: Low balance. Get test ALGO from:")
        print("https://bank.testnet.algorand.network/")
        return
    
    # Define contracts to deploy
    contracts = [
        ('property_token', 'Property Token Contract'),
        ('income_distribution', 'Income Distribution Contract'),
        ('governance', 'Governance Contract')
    ]
    
    deployed_contracts = {}
    
    # Define state schemas
    global_schema = StateSchema(num_uints=10, num_byte_slices=10)
    local_schema = StateSchema(num_uints=5, num_byte_slices=5)
    
    for module_name, display_name in contracts:
        try:
            print(f"\n📦 Deploying {display_name}...")
            
            # Compile contract
            approval_program, clear_program = compile_contract(module_name, display_name)
            
            # Deploy to Algorand
            app_id = algorand_client.deploy_smart_contract(
                algorand_client.admin_private_key,
                approval_program,
                clear_program,
                global_schema,
                local_schema
            )
            
            deployed_contracts[module_name] = app_id
            print(f"✅ {display_name} deployed successfully!")
            print(f"   App ID: {app_id}")
            
        except Exception as e:
            print(f"❌ Error deploying {display_name}: {e}")
    
    # Save deployment info
    print("\n" + "=" * 50)
    print("📋 Deployment Summary")
    print("=" * 50)
    
    for name, app_id in deployed_contracts.items():
        print(f"{name}: {app_id}")
    
    # Save to file
    with open('deployment/deployed_contracts.txt', 'w') as f:
        f.write("BharatPropChain Deployed Contracts\n")
        f.write("=" * 50 + "\n\n")
        for name, app_id in deployed_contracts.items():
            f.write(f"{name}: {app_id}\n")
            f.write(f"https://testnet.algoexplorer.io/application/{app_id}\n\n")
    
    print("\n✅ Deployment complete!")
    print("📄 Details saved to: deployment/deployed_contracts.txt")


if __name__ == '__main__':
    try:
        deploy_contracts()
    except KeyboardInterrupt:
        print("\n\n⚠️  Deployment cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
