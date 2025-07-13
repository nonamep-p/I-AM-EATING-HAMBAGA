"""
Constants for the Epic RPG Bot
"""

# RPG System Constants
RPG_CONSTANTS = {
    # Cooldowns (in seconds)
    'work_cooldown': 3600,      # 1 hour
    'daily_cooldown': 86400,    # 24 hours
    'adventure_cooldown': 1800,  # 30 minutes
    'battle_cooldown': 300,     # 5 minutes
    
    # Costs
    'heal_cost': 50,            # Cost to heal
    'revive_cost': 100,         # Cost to revive
    
    # Level system
    'base_xp': 100,             # XP needed for level 2
    'xp_multiplier': 1.5,       # XP multiplier per level
    
    # Battle system
    'critical_chance': 0.1,     # 10% critical hit chance
    'critical_multiplier': 2.0,  # 2x damage on critical
    
    # Luck system
    'luck_decay': 0.95,         # Luck decay per day
    'max_luck': 1000,           # Maximum luck points
}

# Monsters for battles
MONSTERS = [
    {"name": "Goblin", "hp": 30, "attack": 8, "max_hp": 30},
    {"name": "Orc", "hp": 50, "attack": 12, "max_hp": 50},
    {"name": "Skeleton", "hp": 40, "attack": 10, "max_hp": 40},
    {"name": "Troll", "hp": 80, "attack": 15, "max_hp": 80}
]

# Adventure locations
ADVENTURE_LOCATIONS = ["Forest", "Mountains", "Dungeon", "Desert"]

# Item Rarity System
RARITY_COLORS = {
    "common": 0x9E9E9E,      # Gray
    "uncommon": 0x4CAF50,    # Green
    "rare": 0x2196F3,        # Blue
    "epic": 0x9C27B0,        # Purple
    "legendary": 0xFF9800,   # Orange
    "mythic": 0xF44336,      # Red
    "divine": 0xFFD700,      # Gold
    "omnipotent": 0xFF1493   # Deep Pink
}

RARITY_WEIGHTS = {
    "common": 50,
    "uncommon": 25,
    "rare": 15,
    "epic": 7,
    "legendary": 2,
    "mythic": 0.9,
    "divine": 0.09,
    "omnipotent": 0.01
}

# Shop items with rarity
SHOP_ITEMS = {
    "Iron Sword": {"price": 200, "type": "weapon", "stats": {"attack": 5}, "rarity": "common"},
    "Leather Armor": {"price": 150, "type": "armor", "stats": {"defense": 3}, "rarity": "common"},
    "Health Potion": {"price": 25, "type": "consumable", "stats": {"hp": 50}, "rarity": "common"},
    "Lucky Charm": {"price": 500, "type": "accessory", "stats": {"luck": 10}, "rarity": "uncommon"},
    "Lootbox": {"price": 1000, "type": "consumable", "stats": {}, "rarity": "special"}
}

# Weapon database with rarities
WEAPONS = {
    # Common
    "Rusty Dagger": {"attack": 3, "rarity": "common", "special": None},
    "Iron Sword": {"attack": 8, "rarity": "common", "special": None},
    "Steel Blade": {"attack": 12, "rarity": "common", "special": None},
    
    # Uncommon
    "Silver Sword": {"attack": 18, "rarity": "uncommon", "special": None},
    "Enchanted Blade": {"attack": 22, "rarity": "uncommon", "special": "magic_damage"},
    
    # Rare
    "Flaming Sword": {"attack": 35, "rarity": "rare", "special": "fire_damage"},
    "Ice Shard": {"attack": 32, "rarity": "rare", "special": "freeze_chance"},
    
    # Epic
    "Dragon Slayer": {"attack": 55, "rarity": "epic", "special": "dragon_bane"},
    "Void Blade": {"attack": 50, "rarity": "epic", "special": "void_damage"},
    
    # Legendary
    "Excalibur": {"attack": 85, "rarity": "legendary", "special": "holy_damage"},
    "Mjolnir": {"attack": 90, "rarity": "legendary", "special": "lightning_strike"},
    
    # Mythic
    "Soul Reaper": {"attack": 150, "rarity": "mythic", "special": "soul_steal"},
    "Chaos Blade": {"attack": 140, "rarity": "mythic", "special": "chaos_magic"},
    
    # Divine
    "Godslayer": {"attack": 250, "rarity": "divine", "special": "divine_wrath"},
    
    # Omnipotent (Super Rare)
    "World Ender": {"attack": 999999, "rarity": "omnipotent", "special": "instant_kill"}
}

# Armor database with rarities
ARMOR = {
    # Common
    "Cloth Robe": {"defense": 2, "rarity": "common", "special": None},
    "Leather Armor": {"defense": 5, "rarity": "common", "special": None},
    "Chain Mail": {"defense": 8, "rarity": "common", "special": None},
    
    # Uncommon
    "Iron Armor": {"defense": 12, "rarity": "uncommon", "special": None},
    "Blessed Robes": {"defense": 15, "rarity": "uncommon", "special": "magic_resist"},
    
    # Rare
    "Dragon Scale": {"defense": 25, "rarity": "rare", "special": "fire_resist"},
    "Mithril Armor": {"defense": 30, "rarity": "rare", "special": "lightweight"},
    
    # Epic
    "Paladin Plate": {"defense": 45, "rarity": "epic", "special": "holy_blessing"},
    "Shadow Cloak": {"defense": 40, "rarity": "epic", "special": "stealth"},
    
    # Legendary
    "Aegis Shield": {"defense": 70, "rarity": "legendary", "special": "reflect_damage"},
    "Phoenix Mail": {"defense": 65, "rarity": "legendary", "special": "resurrection"},
    
    # Mythic
    "Void Armor": {"defense": 100, "rarity": "mythic", "special": "void_protection"},
    
    # Divine
    "Divine Vestments": {"defense": 150, "rarity": "divine", "special": "divine_protection"}
}

# Super Rare Omnipotent Item
OMNIPOTENT_ITEM = {
    "Reality Stone": {
        "type": "accessory",
        "rarity": "omnipotent", 
        "special": "reality_control",
        "description": "Grants the power to have anything in the game (except World Ender)"
    }
}

# PvP Arenas
PVP_ARENAS = {
    "Colosseum": {"entry_fee": 100, "winner_multiplier": 2},
    "Shadow Realm": {"entry_fee": 500, "winner_multiplier": 3},
    "Divine Arena": {"entry_fee": 1000, "winner_multiplier": 5}
}

# Lootbox contents
LOOTBOX_CONTENTS = {
    "common": {"coins": (100, 500), "items": ["Health Potion", "Mana Potion"]},
    "rare": {"coins": (500, 2000), "items": ["Magic Scroll", "Enchanted Ring"]},
    "legendary": {"coins": (2000, 10000), "items": ["Legendary Weapon", "Legendary Armor"]}
}

# Shop Items
SHOP_ITEMS = {
    'weapons': {
        'Iron Sword': {
            'price': 500,
            'attack': 15,
            'rarity': 'common',
            'description': 'A sturdy iron blade'
        },
        'Steel Sword': {
            'price': 1200,
            'attack': 25,
            'rarity': 'uncommon',
            'description': 'A sharp steel weapon'
        },
        'Enchanted Blade': {
            'price': 3000,
            'attack': 40,
            'rarity': 'rare',
            'description': 'A magically enhanced sword'
        },
        'Dragon Slayer': {
            'price': 7500,
            'attack': 65,
            'rarity': 'epic',
            'description': 'Forged from dragon scales'
        },
        'Legendary Katana': {
            'price': 15000,
            'attack': 100,
            'rarity': 'legendary',
            'description': 'A blade of legend'
        }
    },
    'armor': {
        'Leather Armor': {
            'price': 400,
            'defense': 8,
            'rarity': 'common',
            'description': 'Basic leather protection'
        },
        'Chain Mail': {
            'price': 1000,
            'defense': 15,
            'rarity': 'uncommon',
            'description': 'Interlocked metal rings'
        },
        'Plate Armor': {
            'price': 2500,
            'defense': 25,
            'rarity': 'rare',
            'description': 'Heavy metal plating'
        },
        'Enchanted Robes': {
            'price': 6000,
            'defense': 35,
            'rarity': 'epic',
            'description': 'Magically warded cloth'
        },
        'Dragon Scale Armor': {
            'price': 12000,
            'defense': 55,
            'rarity': 'legendary',
            'description': 'Scales of an ancient dragon'
        }
    },
    'consumables': {
        'Health Potion': {
            'price': 50,
            'heal': 50,
            'rarity': 'common',
            'description': 'Restores 50 HP'
        },
        'Mana Potion': {
            'price': 75,
            'mana': 50,
            'rarity': 'common',
            'description': 'Restores 50 MP'
        },
        'Super Health Potion': {
            'price': 150,
            'heal': 150,
            'rarity': 'uncommon',
            'description': 'Restores 150 HP'
        },
        'Elixir of Life': {
            'price': 500,
            'heal': 999,
            'rarity': 'rare',
            'description': 'Fully restores HP'
        },
        'Lucky Charm': {
            'price': 1000,
            'luck': 100,
            'rarity': 'epic',
            'description': 'Increases luck for 24 hours'
        }
    }
}

# Monster data
MONSTERS = {
    'Forest': [
        {
            'name': 'Goblin',
            'hp': 50,
            'attack': 12,
            'defense': 3,
            'coins': (20, 50),
            'xp': (15, 30),
            'rarity': 'common'
        },
        {
            'name': 'Wolf',
            'hp': 70,
            'attack': 18,
            'defense': 5,
            'coins': (30, 70),
            'xp': (20, 40),
            'rarity': 'common'
        },
        {
            'name': 'Forest Troll',
            'hp': 120,
            'attack': 25,
            'defense': 8,
            'coins': (80, 150),
            'xp': (50, 100),
            'rarity': 'uncommon'
        }
    ],
    'Mountains': [
        {
            'name': 'Rock Golem',
            'hp': 150,
            'attack': 30,
            'defense': 15,
            'coins': (100, 200),
            'xp': (75, 150),
            'rarity': 'uncommon'
        },
        {
            'name': 'Mountain Lion',
            'hp': 90,
            'attack': 35,
            'defense': 8,
            'coins': (60, 120),
            'xp': (40, 80),
            'rarity': 'common'
        },
        {
            'name': 'Dragon Whelp',
            'hp': 200,
            'attack': 45,
            'defense': 20,
            'coins': (200, 400),
            'xp': (150, 300),
            'rarity': 'rare'
        }
    ],
    'Dungeon': [
        {
            'name': 'Skeleton Warrior',
            'hp': 80,
            'attack': 20,
            'defense': 10,
            'coins': (50, 100),
            'xp': (30, 60),
            'rarity': 'common'
        },
        {
            'name': 'Shadow Wraith',
            'hp': 60,
            'attack': 40,
            'defense': 5,
            'coins': (70, 140),
            'xp': (50, 100),
            'rarity': 'uncommon'
        },
        {
            'name': 'Dungeon Lord',
            'hp': 300,
            'attack': 60,
            'defense': 25,
            'coins': (500, 1000),
            'xp': (300, 600),
            'rarity': 'epic'
        }
    ],
    'Desert': [
        {
            'name': 'Sand Viper',
            'hp': 40,
            'attack': 25,
            'defense': 2,
            'coins': (25, 60),
            'xp': (20, 40),
            'rarity': 'common'
        },
        {
            'name': 'Mummy',
            'hp': 100,
            'attack': 22,
            'defense': 12,
            'coins': (80, 160),
            'xp': (60, 120),
            'rarity': 'uncommon'
        },
        {
            'name': 'Pharaoh\'s Guardian',
            'hp': 250,
            'attack': 50,
            'defense': 30,
            'coins': (400, 800),
            'xp': (250, 500),
            'rarity': 'rare'
        }
    ]
}

# Adventure locations
ADVENTURE_LOCATIONS = {
    'Forest': {
        'description': 'A peaceful forest with hidden dangers',
        'difficulty': 'Easy',
        'rewards_multiplier': 1.0
    },
    'Mountains': {
        'description': 'Treacherous peaks with valuable resources',
        'difficulty': 'Medium',
        'rewards_multiplier': 1.3
    },
    'Dungeon': {
        'description': 'Dark underground chambers filled with treasure',
        'difficulty': 'Hard',
        'rewards_multiplier': 1.7
    },
    'Desert': {
        'description': 'Harsh wasteland with ancient secrets',
        'difficulty': 'Very Hard',
        'rewards_multiplier': 2.0
    }
}

# Daily reward system
DAILY_REWARDS = {
    'base': 200,               # Base daily coins
    'level_multiplier': 10,    # Coins per level
    'streak_bonus': 25,        # Bonus coins per streak day
    'max_streak': 30,          # Maximum streak bonus
}

# Luck system
LUCK_LEVELS = {
    'cursed': {'min': -1000, 'max': -500, 'emoji': '💀', 'bonus_percent': -50},
    'unlucky': {'min': -499, 'max': -100, 'emoji': '😰', 'bonus_percent': -25},
    'normal': {'min': -99, 'max': 99, 'emoji': '😐', 'bonus_percent': 0},
    'lucky': {'min': 100, 'max': 499, 'emoji': '🍀', 'bonus_percent': 25},
    'blessed': {'min': 500, 'max': 999, 'emoji': '✨', 'bonus_percent': 50},
    'divine': {'min': 1000, 'max': 9999, 'emoji': '🌟', 'bonus_percent': 100},
}

# Moderation constants
MODERATION_CONSTANTS = {
    'max_warnings': 3,
    'auto_ban_warnings': 5,
    'spam_threshold': 5,       # Messages per 10 seconds
    'spam_time_window': 10,    # Seconds
    'caps_threshold': 0.7,     # 70% caps = spam
    'repeated_chars': 5,       # 5+ same chars = spam
}

# AI Chat constants
AI_CONSTANTS = {
    'max_history': 20,         # Maximum conversation history
    'response_timeout': 30,    # Seconds to wait for AI response
    'max_tokens': 1000,        # Maximum response tokens
    'temperature': 0.7,        # AI response randomness
}

# Embed limits
EMBED_LIMITS = {
    'title': 256,
    'description': 4096,
    'field_name': 256,
    'field_value': 1024,
    'footer': 2048,
    'author': 256,
    'fields': 25,
    'total': 6000
}