"""
Property Token Smart Contract
PyTeal contract for minting property tokens as Algorand Standard Assets
"""

from pyteal import *


def property_token_contract():
    """
    Smart contract for property tokenization
    Handles token minting with property metadata verification
    """
    
    # Global state keys
    property_id_key = Bytes("property_id")
    property_hash_key = Bytes("property_hash")
    owner_key = Bytes("owner")
    total_value_key = Bytes("total_value")
    token_supply_key = Bytes("token_supply")
    
    # Operations
    op_mint = Bytes("mint")
    op_verify = Bytes("verify")
    
    # Mint new property token
    mint_token = Seq([
        # Verify caller is the owner
        Assert(Txn.sender() == App.globalGet(owner_key)),
        
        # Store property metadata
        App.globalPut(property_id_key, Txn.application_args[1]),
        App.globalPut(property_hash_key, Txn.application_args[2]),
        App.globalPut(total_value_key, Btoi(Txn.application_args[3])),
        App.globalPut(token_supply_key, Btoi(Txn.application_args[4])),
        
        Return(Int(1))
    ])
    
    # Verify property data
    verify_property = Seq([
        # Check if property hash matches
        Assert(App.globalGet(property_hash_key) == Txn.application_args[1]),
        Return(Int(1))
    ])
    
    # Main program logic
    program = Cond(
        # Initialize contract
        [Txn.application_id() == Int(0), Seq([
            App.globalPut(owner_key, Txn.sender()),
            Return(Int(1))
        ])],
        
        # Handle operations
        [Txn.application_args[0] == op_mint, mint_token],
        [Txn.application_args[0] == op_verify, verify_property],
        
        # Default: reject
        [Int(1), Return(Int(0))]
    )
    
    return program


def approval_program():
    """Main approval program"""
    return property_token_contract()


def clear_program():
    """Clear state program"""
    return Return(Int(1))


if __name__ == "__main__":
    # Compile the contract
    with open("property_token_approval.teal", "w") as f:
        compiled = compileTeal(approval_program(), mode=Mode.Application, version=8)
        f.write(compiled)
    
    with open("property_token_clear.teal", "w") as f:
        compiled = compileTeal(clear_program(), mode=Mode.Application, version=8)
        f.write(compiled)
    
    print("Property token contract compiled successfully!")
