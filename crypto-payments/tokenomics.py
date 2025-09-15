"""
Mycelium Token (MYC) Tokenomics Implementation
Smart contract and economic model for the native token
"""

import json
from typing import Dict, List, Optional
from decimal import Decimal, getcontext
from enum import Enum
from datetime import datetime, timedelta
from dataclasses import dataclass

# Set precision for financial calculations
getcontext().prec = 28

class TokenType(Enum):
    UTILITY = "utility"
    GOVERNANCE = "governance"
    REWARD = "reward"
    STAKING = "staking"

class StakingTier(Enum):
    BRONZE = "bronze"    # 1,000 MYC minimum
    SILVER = "silver"    # 10,000 MYC minimum
    GOLD = "gold"        # 100,000 MYC minimum
    PLATINUM = "platinum"  # 1,000,000 MYC minimum

@dataclass
class TokenAllocation:
    category: str
    amount: int
    percentage: float
    vesting_months: int
    cliff_months: int
    description: str

@dataclass
class StakingReward:
    tier: StakingTier
    min_stake: int
    apy_rate: float
    bonus_multiplier: float
    compute_discount: float
    governance_weight: float

class MyceliumTokenomics:
    """MYC Token Economic Model and Smart Contract Interface"""
    
    # Total supply: 1 billion MYC tokens
    TOTAL_SUPPLY = 1_000_000_000
    
    # Token allocation breakdown
    TOKEN_ALLOCATIONS = [
        TokenAllocation(
            category="Public Sale",
            amount=200_000_000,  # 20%
            percentage=20.0,
            vesting_months=0,
            cliff_months=0,
            description="Initial token distribution to early adopters"
        ),
        TokenAllocation(
            category="Team & Advisors", 
            amount=150_000_000,  # 15%
            percentage=15.0,
            vesting_months=48,
            cliff_months=12,
            description="Core team and advisory board allocation"
        ),
        TokenAllocation(
            category="Development Fund",
            amount=200_000_000,  # 20%
            percentage=20.0,
            vesting_months=60,
            cliff_months=6,
            description="Ongoing platform development and improvements"
        ),
        TokenAllocation(
            category="Ecosystem Rewards",
            amount=250_000_000,  # 25%
            percentage=25.0,
            vesting_months=120,
            cliff_months=0,
            description="Community rewards, staking, and governance incentives"
        ),
        TokenAllocation(
            category="Strategic Partners",
            amount=100_000_000,  # 10%
            percentage=10.0,
            vesting_months=24,
            cliff_months=6,
            description="Integration partners and institutional investors"
        ),
        TokenAllocation(
            category="Reserve Fund",
            amount=100_000_000,  # 10%
            percentage=10.0,
            vesting_months=0,
            cliff_months=0,
            description="Treasury for market operations and emergency funds"
        )
    ]
    
    # Staking tiers and rewards
    STAKING_TIERS = {
        StakingTier.BRONZE: StakingReward(
            tier=StakingTier.BRONZE,
            min_stake=1_000,
            apy_rate=0.08,  # 8% APY
            bonus_multiplier=1.0,
            compute_discount=0.05,  # 5% discount on compute
            governance_weight=1.0
        ),
        StakingTier.SILVER: StakingReward(
            tier=StakingTier.SILVER,
            min_stake=10_000,
            apy_rate=0.12,  # 12% APY
            bonus_multiplier=1.25,
            compute_discount=0.10,  # 10% discount
            governance_weight=2.0
        ),
        StakingTier.GOLD: StakingReward(
            tier=StakingTier.GOLD,
            min_stake=100_000,
            apy_rate=0.18,  # 18% APY
            bonus_multiplier=1.5,
            compute_discount=0.15,  # 15% discount
            governance_weight=4.0
        ),
        StakingTier.PLATINUM: StakingReward(
            tier=StakingTier.PLATINUM,
            min_stake=1_000_000,
            apy_rate=0.25,  # 25% APY
            bonus_multiplier=2.0,
            compute_discount=0.25,  # 25% discount
            governance_weight=10.0
        )
    }
    
    # Token utility functions
    UTILITY_FUNCTIONS = {
        "compute_payment": "Pay for bio-algorithm computation",
        "premium_features": "Access advanced language features",
        "marketplace_transactions": "Buy/sell algorithms in marketplace",
        "governance_voting": "Vote on platform development decisions",
        "staking_rewards": "Earn rewards by staking tokens",
        "api_access": "Pay for API calls and services",
        "training_courses": "Purchase educational content",
        "research_grants": "Fund community research projects"
    }
    
    def __init__(self, contract_address: Optional[str] = None):
        self.contract_address = contract_address
        self.launch_date = datetime(2025, 3, 1)  # Planned launch date
        
    def get_token_allocation_summary(self) -> Dict:
        """Get complete token allocation breakdown"""
        total_allocated = sum(allocation.amount for allocation in self.TOKEN_ALLOCATIONS)
        
        return {
            "total_supply": self.TOTAL_SUPPLY,
            "total_allocated": total_allocated,
            "remaining": self.TOTAL_SUPPLY - total_allocated,
            "allocations": [
                {
                    "category": allocation.category,
                    "amount": f"{allocation.amount:,}",
                    "percentage": allocation.percentage,
                    "vesting_months": allocation.vesting_months,
                    "cliff_months": allocation.cliff_months,
                    "description": allocation.description
                }
                for allocation in self.TOKEN_ALLOCATIONS
            ]
        }
    
    def calculate_staking_rewards(self, stake_amount: int, days_staked: int) -> Dict:
        """Calculate staking rewards based on amount and duration"""
        tier = self._get_staking_tier(stake_amount)
        if not tier:
            return {"error": "Minimum staking amount not met"}
        
        reward_config = self.STAKING_TIERS[tier]
        
        # Calculate base rewards
        annual_reward = stake_amount * reward_config.apy_rate
        daily_reward = annual_reward / 365
        total_reward = daily_reward * days_staked
        
        # Apply bonus multiplier for longer staking periods
        if days_staked >= 365:  # 1 year bonus
            total_reward *= reward_config.bonus_multiplier
        elif days_staked >= 180:  # 6 month bonus
            total_reward *= (reward_config.bonus_multiplier * 0.75)
        elif days_staked >= 90:   # 3 month bonus
            total_reward *= (reward_config.bonus_multiplier * 0.5)
        
        return {
            "stake_amount": stake_amount,
            "tier": tier.value,
            "days_staked": days_staked,
            "apy_rate": reward_config.apy_rate * 100,
            "daily_reward": round(daily_reward, 6),
            "total_reward": round(total_reward, 6),
            "bonus_multiplier": reward_config.bonus_multiplier,
            "compute_discount": reward_config.compute_discount * 100,
            "governance_weight": reward_config.governance_weight
        }
    
    def _get_staking_tier(self, stake_amount: int) -> Optional[StakingTier]:
        """Determine staking tier based on amount"""
        if stake_amount >= self.STAKING_TIERS[StakingTier.PLATINUM].min_stake:
            return StakingTier.PLATINUM
        elif stake_amount >= self.STAKING_TIERS[StakingTier.GOLD].min_stake:
            return StakingTier.GOLD
        elif stake_amount >= self.STAKING_TIERS[StakingTier.SILVER].min_stake:
            return StakingTier.SILVER
        elif stake_amount >= self.STAKING_TIERS[StakingTier.BRONZE].min_stake:
            return StakingTier.BRONZE
        else:
            return None
    
    def calculate_governance_power(self, stake_amount: int) -> Dict:
        """Calculate voting power in governance based on stake"""
        tier = self._get_staking_tier(stake_amount)
        if not tier:
            return {"error": "No governance power - minimum stake not met"}
        
        reward_config = self.STAKING_TIERS[tier]
        base_power = stake_amount
        weighted_power = base_power * reward_config.governance_weight
        
        return {
            "stake_amount": stake_amount,
            "tier": tier.value,
            "base_voting_power": base_power,
            "weighted_voting_power": int(weighted_power),
            "governance_weight_multiplier": reward_config.governance_weight
        }
    
    def get_token_price_projection(self, months_ahead: int = 36) -> Dict:
        """Project token price based on utility growth and market adoption"""
        base_price = 0.10  # Initial price $0.10
        monthly_growth_rates = {
            "months_0_6": 0.15,    # 15% monthly growth in first 6 months
            "months_6_12": 0.10,   # 10% monthly growth months 6-12
            "months_12_24": 0.05,  # 5% monthly growth months 12-24
            "months_24_plus": 0.02 # 2% monthly growth beyond 24 months
        }
        
        price = base_price
        projections = [{"month": 0, "price": price, "market_cap": price * self.TOTAL_SUPPLY}]
        
        for month in range(1, months_ahead + 1):
            if month <= 6:
                growth_rate = monthly_growth_rates["months_0_6"]
            elif month <= 12:
                growth_rate = monthly_growth_rates["months_6_12"]
            elif month <= 24:
                growth_rate = monthly_growth_rates["months_12_24"]
            else:
                growth_rate = monthly_growth_rates["months_24_plus"]
            
            price *= (1 + growth_rate)
            market_cap = price * self.TOTAL_SUPPLY
            
            projections.append({
                "month": month,
                "price": round(price, 4),
                "market_cap": round(market_cap, 0),
                "growth_rate": growth_rate * 100
            })
        
        return {
            "base_price": base_price,
            "total_supply": self.TOTAL_SUPPLY,
            "projections": projections
        }
    
    def get_utility_economics(self) -> Dict:
        """Get token utility and economic incentives"""
        return {
            "utility_functions": self.UTILITY_FUNCTIONS,
            "payment_discounts": {
                "crypto_payment_discount": "10-20% off subscription prices",
                "bulk_credit_discount": "Up to 20% off compute credits",
                "staking_compute_discount": "5-25% off based on staking tier",
                "long_term_lock_bonus": "Additional 25% rewards for 1+ year stakes"
            },
            "deflationary_mechanics": {
                "transaction_burn": "0.5% of tokens burned on each transaction",
                "compute_burn": "1% of compute payment tokens burned",
                "governance_burn": "Unused governance tokens burned quarterly",
                "buyback_program": "10% of revenue used for token buybacks"
            },
            "ecosystem_incentives": {
                "developer_rewards": "Earn MYC for contributing algorithms",
                "bug_bounties": "Security researchers rewarded in MYC",
                "community_grants": "Fund research projects with MYC",
                "referral_bonuses": "Earn MYC for bringing new users",
                "education_rewards": "Complete courses to earn MYC"
            }
        }
    
    def generate_smart_contract_spec(self) -> str:
        """Generate Solidity smart contract specification"""
        return '''
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";

contract MyceliumToken is ERC20, ERC20Burnable, Pausable, Ownable {
    uint256 public constant TOTAL_SUPPLY = 1_000_000_000 * 10**18;
    
    // Staking variables
    mapping(address => uint256) public stakedBalances;
    mapping(address => uint256) public stakingTimestamps;
    mapping(address => StakingTier) public userTiers;
    
    enum StakingTier { None, Bronze, Silver, Gold, Platinum }
    
    struct TierConfig {
        uint256 minStake;
        uint256 apyRate;      // Basis points (e.g., 800 = 8%)
        uint256 bonusMultiplier;
        uint256 computeDiscount;
        uint256 governanceWeight;
    }
    
    mapping(StakingTier => TierConfig) public tierConfigs;
    
    // Events
    event Staked(address indexed user, uint256 amount, StakingTier tier);
    event Unstaked(address indexed user, uint256 amount, uint256 reward);
    event RewardClaimed(address indexed user, uint256 reward);
    event TokensBurned(uint256 amount, string reason);
    
    constructor() ERC20("Mycelium Token", "MYC") {
        _mint(msg.sender, TOTAL_SUPPLY);
        
        // Initialize staking tiers
        tierConfigs[StakingTier.Bronze] = TierConfig(1000 * 10**18, 800, 100, 500, 100);
        tierConfigs[StakingTier.Silver] = TierConfig(10000 * 10**18, 1200, 125, 1000, 200);
        tierConfigs[StakingTier.Gold] = TierConfig(100000 * 10**18, 1800, 150, 1500, 400);
        tierConfigs[StakingTier.Platinum] = TierConfig(1000000 * 10**18, 2500, 200, 2500, 1000);
    }
    
    // Staking functions
    function stake(uint256 amount) external whenNotPaused {
        require(amount > 0, "Amount must be greater than 0");
        require(balanceOf(msg.sender) >= amount, "Insufficient balance");
        
        _transfer(msg.sender, address(this), amount);
        
        stakedBalances[msg.sender] += amount;
        stakingTimestamps[msg.sender] = block.timestamp;
        
        // Determine tier
        StakingTier tier = _getStakingTier(stakedBalances[msg.sender]);
        userTiers[msg.sender] = tier;
        
        emit Staked(msg.sender, amount, tier);
    }
    
    function unstake(uint256 amount) external {
        require(stakedBalances[msg.sender] >= amount, "Insufficient staked balance");
        
        uint256 reward = calculateReward(msg.sender);
        
        stakedBalances[msg.sender] -= amount;
        
        // Update tier
        StakingTier tier = _getStakingTier(stakedBalances[msg.sender]);
        userTiers[msg.sender] = tier;
        
        _transfer(address(this), msg.sender, amount + reward);
        
        emit Unstaked(msg.sender, amount, reward);
    }
    
    function calculateReward(address user) public view returns (uint256) {
        if (stakedBalances[user] == 0) return 0;
        
        uint256 stakingDuration = block.timestamp - stakingTimestamps[user];
        StakingTier tier = userTiers[user];
        TierConfig memory config = tierConfigs[tier];
        
        uint256 annualReward = (stakedBalances[user] * config.apyRate) / 10000;
        uint256 reward = (annualReward * stakingDuration) / 365 days;
        
        // Apply bonus multiplier for long-term staking
        if (stakingDuration >= 365 days) {
            reward = (reward * config.bonusMultiplier) / 100;
        }
        
        return reward;
    }
    
    function _getStakingTier(uint256 amount) internal view returns (StakingTier) {
        if (amount >= tierConfigs[StakingTier.Platinum].minStake) return StakingTier.Platinum;
        if (amount >= tierConfigs[StakingTier.Gold].minStake) return StakingTier.Gold;
        if (amount >= tierConfigs[StakingTier.Silver].minStake) return StakingTier.Silver;
        if (amount >= tierConfigs[StakingTier.Bronze].minStake) return StakingTier.Bronze;
        return StakingTier.None;
    }
    
    // Burn function for deflationary mechanics
    function burnForUtility(uint256 amount, string memory reason) external onlyOwner {
        _burn(address(this), amount);
        emit TokensBurned(amount, reason);
    }
    
    // Governance functions
    function getVotingPower(address user) external view returns (uint256) {
        uint256 baseVotes = stakedBalances[user];
        TierConfig memory config = tierConfigs[userTiers[user]];
        return (baseVotes * config.governanceWeight) / 100;
    }
    
    function pause() public onlyOwner {
        _pause();
    }
    
    function unpause() public onlyOwner {
        _unpause();
    }
}
'''


# Usage example and testing
if __name__ == "__main__":
    tokenomics = MyceliumTokenomics()
    
    print("=== MYC TOKEN ALLOCATION ===")
    allocation = tokenomics.get_token_allocation_summary()
    print(json.dumps(allocation, indent=2))
    
    print("\n=== STAKING REWARDS EXAMPLE ===")
    # Example: 50,000 MYC staked for 365 days
    rewards = tokenomics.calculate_staking_rewards(50000, 365)
    print(json.dumps(rewards, indent=2))
    
    print("\n=== GOVERNANCE POWER EXAMPLE ===")
    governance = tokenomics.calculate_governance_power(50000)
    print(json.dumps(governance, indent=2))
    
    print("\n=== PRICE PROJECTIONS (3 YEARS) ===")
    projections = tokenomics.get_token_price_projection(36)
    print(f"Initial Price: ${projections['base_price']}")
    print(f"Year 1 Price: ${projections['projections'][12]['price']}")
    print(f"Year 2 Price: ${projections['projections'][24]['price']}")
    print(f"Year 3 Price: ${projections['projections'][36]['price']}")
    
    print("\n=== TOKEN UTILITY ===")
    utility = tokenomics.get_utility_economics()
    print(json.dumps(utility, indent=2))