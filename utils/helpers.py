import discord
import random
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

from config import COLORS, EMOJIS

logger = logging.getLogger(__name__)

def create_embed(title: str, description: str, color: int = COLORS['primary']) -> discord.Embed:
    """Create a standardized embed."""
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.now()
    )
    return embed

def format_number(num: int) -> str:
    """Format large numbers with commas."""
    return f"{num:,}"

def create_progress_bar(percentage: float, length: int = 10) -> str:
    """Create a visual progress bar."""
    filled = int(percentage / 100 * length)
    empty = length - filled
    return f"{'█' * filled}{'░' * empty} {percentage:.1f}%"

def get_random_work_job() -> Dict[str, Any]:
    """Get a random work job with rewards."""
    jobs = [
        {
            "name": "Delivery Driver",
            "min_coins": 50,
            "max_coins": 100,
            "min_xp": 10,
            "max_xp": 25
        },
        {
            "name": "Data Entry",
            "min_coins": 30,
            "max_coins": 80,
            "min_xp": 5,
            "max_xp": 20
        },
        {
            "name": "Freelance Writer",
            "min_coins": 70,
            "max_coins": 150,
            "min_xp": 15,
            "max_xp": 35
        },
        {
            "name": "Pet Sitter",
            "min_coins": 40,
            "max_coins": 90,
            "min_xp": 8,
            "max_xp": 22
        },
        {
            "name": "Tutor",
            "min_coins": 80,
            "max_coins": 160,
            "min_xp": 20,
            "max_xp": 40
        }
    ]
    
    return random.choice(jobs)

def get_random_adventure_outcome() -> Dict[str, Any]:
    """Get a random adventure outcome."""
    outcomes = [
        {
            "description": "You discovered a hidden treasure chest!",
            "coins": (100, 300),
            "xp": (50, 100),
            "items": ["Health Potion", "Mana Potion", "Ancient Coin"]
        },
        {
            "description": "You helped a lost traveler and received a reward!",
            "coins": (80, 200),
            "xp": (30, 70),
            "items": ["Traveler's Map", "Lucky Charm", "Bread"]
        },
        {
            "description": "You found rare materials while exploring!",
            "coins": (60, 150),
            "xp": (40, 80),
            "items": ["Iron Ore", "Mystic Crystal", "Healing Herbs"]
        },
        {
            "description": "You completed a mysterious quest!",
            "coins": (120, 250),
            "xp": (60, 120),
            "items": ["Quest Scroll", "Magic Ring", "Gold Coin"]
        }
    ]
    
    return random.choice(outcomes)

def level_up_player(player_data: Dict[str, Any]) -> Optional[str]:
    """Check if player levels up and apply bonuses."""
    current_level = player_data.get('level', 1)
    current_xp = player_data.get('xp', 0)
    max_xp = player_data.get('max_xp', 100)
    
    if current_xp >= max_xp:
        # Level up!
        new_level = current_level + 1
        
        # Calculate new max XP (exponential growth)
        new_max_xp = int(max_xp * 1.5)
        
        # Apply stat bonuses
        hp_bonus = random.randint(15, 25)
        attack_bonus = random.randint(3, 7)
        defense_bonus = random.randint(2, 5)
        coin_bonus = new_level * 50
        
        player_data['level'] = new_level
        player_data['xp'] = current_xp - max_xp  # Carry over excess XP
        player_data['max_xp'] = new_max_xp
        player_data['max_hp'] = player_data.get('max_hp', 100) + hp_bonus
        player_data['hp'] = player_data['max_hp']  # Full heal on level up
        player_data['attack'] = player_data.get('attack', 10) + attack_bonus
        player_data['defense'] = player_data.get('defense', 5) + defense_bonus
        player_data['coins'] = player_data.get('coins', 0) + coin_bonus
        
        return (f"Level {new_level}! "
                f"HP +{hp_bonus}, ATK +{attack_bonus}, DEF +{defense_bonus}, "
                f"Coins +{coin_bonus}")
    
    return None

def calculate_battle_damage(attacker_stats: Dict[str, Any], defender_stats: Dict[str, Any]) -> int:
    """Calculate damage in battle."""
    attack = attacker_stats.get('attack', 10)
    defense = defender_stats.get('defense', 5)
    
    # Base damage calculation
    base_damage = max(1, attack - defense)
    
    # Add some randomness (80% - 120% of base damage)
    damage_multiplier = random.uniform(0.8, 1.2)
    final_damage = int(base_damage * damage_multiplier)
    
    return max(1, final_damage)

def generate_random_stats() -> Dict[str, int]:
    """Generate random stats for monsters/items."""
    return {
        'hp': random.randint(50, 150),
        'attack': random.randint(8, 20),
        'defense': random.randint(3, 12)
    }

def format_time_remaining(seconds: int) -> str:
    """Format time remaining in human-readable format."""
    if seconds <= 0:
        return "Ready now!"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

def get_time_until_next_use(last_use: Optional[datetime], cooldown_seconds: int) -> int:
    """Get seconds until next use of a cooldown-based command."""
    if not last_use:
        return 0
    
    next_use = last_use + timedelta(seconds=cooldown_seconds)
    now = datetime.now()
    
    if now >= next_use:
        return 0
    
    return int((next_use - now).total_seconds())

def get_rarity_color(rarity: str) -> int:
    """Get color for item rarity."""
    rarity_colors = {
        'common': 0x95A5A6,      # Gray
        'uncommon': 0x2ECC71,    # Green
        'rare': 0x3498DB,        # Blue
        'epic': 0x9B59B6,        # Purple
        'legendary': 0xF39C12,   # Orange
        'mythical': 0xE74C3C     # Red
    }
    return rarity_colors.get(rarity.lower(), 0x95A5A6)

def get_rarity_emoji(rarity: str) -> str:
    """Get emoji for item rarity."""
    rarity_emojis = {
        'common': '⚪',
        'uncommon': '🟢',
        'rare': '🔵',
        'epic': '🟣',
        'legendary': '🟠',
        'mythical': '🔴'
    }
    return rarity_emojis.get(rarity.lower(), '⚪')

def truncate_text(text: str, max_length: int = 1000) -> str:
    """Truncate text to fit within Discord limits."""
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."

def get_user_display_name(user: discord.User) -> str:
    """Get the best display name for a user."""
    return getattr(user, 'display_name', user.name)

def create_success_embed(title: str, description: str) -> discord.Embed:
    """Create a success embed."""
    return create_embed(title, description, COLORS['success'])

def create_error_embed(title: str, description: str) -> discord.Embed:
    """Create an error embed."""
    return create_embed(title, description, COLORS['error'])

def create_warning_embed(title: str, description: str) -> discord.Embed:
    """Create a warning embed."""
    return create_embed(title, description, COLORS['warning'])

def create_info_embed(title: str, description: str) -> discord.Embed:
    """Create an info embed."""
    return create_embed(title, description, COLORS['info'])

def format_duration(seconds: int) -> str:
    """Format duration in seconds to human readable format."""
    if seconds < 60:
        return f"{seconds} seconds"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        if remaining_seconds > 0:
            return f"{minutes} minutes, {remaining_seconds} seconds"
        return f"{minutes} minutes"
    elif seconds < 86400:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        if remaining_minutes > 0:
            return f"{hours} hours, {remaining_minutes} minutes"
        return f"{hours} hours"
    else:
        days = seconds // 86400
        remaining_hours = (seconds % 86400) // 3600
        if remaining_hours > 0:
            return f"{days} days, {remaining_hours} hours"
        return f"{days} days"