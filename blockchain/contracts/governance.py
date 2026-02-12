"""
Governance Smart Contract
Token-based voting for property decisions
"""

from pyteal import *


def governance_contract():
    """
    Decentralized governance contract for property management
    Token holders can vote on proposals
    """
    
    # Global state
    proposal_count_key = Bytes("prop_count")
    quorum_key = Bytes("quorum")
    
    # Local state (per user)
    vote_weight_key = Bytes("vote_weight")
    
    # Operations
    op_create_proposal = Bytes("create")
    op_vote = Bytes("vote")
    op_execute = Bytes("execute")
    
    # Scratch variables
    proposal_id = ScratchVar(TealType.uint64)
    votes_for = ScratchVar(TealType.uint64)
    votes_against = ScratchVar(TealType.uint64)
    
    # Create a new proposal
    create_proposal = Seq([
        # Increment proposal count
        App.globalPut(
            proposal_count_key,
            App.globalGet(proposal_count_key) + Int(1)
        ),
        
        # Store proposal details (simplified for hackathon)
        # In production: store proposal hash, description, voting period
        Return(Int(1))
    ])
    
    # Cast a vote
    cast_vote = Seq([
        # Get proposal ID
        proposal_id.store(Btoi(Txn.application_args[1])),
        
        # Verify proposal exists
        Assert(proposal_id.load() <= App.globalGet(proposal_count_key)),
        
        # Record vote (simplified)
        # In production: verify token ownership, prevent double voting
        App.localPut(Txn.sender(), vote_weight_key, Btoi(Txn.application_args[2])),
        
        Return(Int(1))
    ])
    
    # Execute proposal if quorum reached
    execute_proposal = Seq([
        # Check quorum and majority
        # Simplified for hackathon
        Return(Int(1))
    ])
    
    # Main program
    program = Cond(
        # Initialize
        [Txn.application_id() == Int(0), Seq([
            App.globalPut(proposal_count_key, Int(0)),
            App.globalPut(quorum_key, Int(51)),  # 51% quorum
            Return(Int(1))
        ])],
        
        # Opt-in (for local state)
        [Txn.on_completion() == OnComplete.OptIn, Return(Int(1))],
        
        # Operations
        [Txn.application_args[0] == op_create_proposal, create_proposal],
        [Txn.application_args[0] == op_vote, cast_vote],
        [Txn.application_args[0] == op_execute, execute_proposal],
        
        # Default
        [Int(1), Return(Int(0))]
    )
    
    return program


def approval_program():
    return governance_contract()


def clear_program():
    return Return(Int(1))


if __name__ == "__main__":
    with open("governance_approval.teal", "w") as f:
        compiled = compileTeal(approval_program(), mode=Mode.Application, version=8)
        f.write(compiled)
    
    with open("governance_clear.teal", "w") as f:
        compiled = compileTeal(clear_program(), mode=Mode.Application, version=8)
        f.write(compiled)
    
    print("Governance contract compiled successfully!")
