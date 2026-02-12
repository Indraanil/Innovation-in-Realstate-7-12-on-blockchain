"""
Income Distribution Smart Contract
Automated rental income distribution based on token ownership
"""

from pyteal import *


def income_distribution_contract():
    """
    Smart contract for automated rental income distribution
    Distributes income proportionally to token holders
    """
    
    # Global state
    property_asset_id_key = Bytes("asset_id")
    total_income_key = Bytes("total_income")
    last_distribution_key = Bytes("last_dist")
    
    # Operations
    op_setup = Bytes("setup")
    op_distribute = Bytes("distribute")
    op_claim = Bytes("claim")
    
    # Setup the income distribution
    setup_distribution = Seq([
        # Store property asset ID
        App.globalPut(property_asset_id_key, Btoi(Txn.application_args[1])),
        App.globalPut(total_income_key, Int(0)),
        App.globalPut(last_distribution_key, Global.latest_timestamp()),
        Return(Int(1))
    ])
    
    # Distribute income to contract
    distribute_income = Seq([
        # Add to total income pool
        App.globalPut(
            total_income_key,
            App.globalGet(total_income_key) + Txn.amount()
        ),
        App.globalPut(last_distribution_key, Global.latest_timestamp()),
        Return(Int(1))
    ])
    
    # Claim proportional income
    claim_income = Seq([
        # Calculate user's share based on token ownership
        # In production, this would query asset holdings
        # For hackathon, simplified logic
        Return(Int(1))
    ])
    
    # Main program
    program = Cond(
        # Initialize
        [Txn.application_id() == Int(0), Return(Int(1))],
        
        # Operations
        [Txn.application_args[0] == op_setup, setup_distribution],
        [Txn.application_args[0] == op_distribute, distribute_income],
        [Txn.application_args[0] == op_claim, claim_income],
        
        # Default
        [Int(1), Return(Int(0))]
    )
    
    return program


def approval_program():
    return income_distribution_contract()


def clear_program():
    return Return(Int(1))


if __name__ == "__main__":
    with open("income_distribution_approval.teal", "w") as f:
        compiled = compileTeal(approval_program(), mode=Mode.Application, version=8)
        f.write(compiled)
    
    with open("income_distribution_clear.teal", "w") as f:
        compiled = compileTeal(clear_program(), mode=Mode.Application, version=8)
        f.write(compiled)
    
    print("Income distribution contract compiled successfully!")
