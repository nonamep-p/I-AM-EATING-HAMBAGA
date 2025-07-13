import logging
from typing import Dict, Any, Optional, List
from replit import db
import json
from datetime import datetime

logger = logging.getLogger(__name__)

async def initialize_database():
    """Initialize the database with default settings."""
    try:
        # Initialize global settings if they don't exist
        if "global_settings" not in db:
            db["global_settings"] = {
                "bot_version": "1.0.0",
                "maintenance_mode": False,
                "total_users": 0,
                "total_guilds": 0
            }
        
        logger.info("Database initialization complete")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

def get_user_rpg_data(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user's RPG data from database."""
    try:
        key = f"user_rpg_{user_id}"
        if key in db:
            return dict(db[key])
        return None
    except Exception as e:
        logger.error(f"Error getting user RPG data for {user_id}: {e}")
        return None

def update_user_rpg_data(user_id: str, data: Dict[str, Any]) -> bool:
    """Update user's RPG data in database."""
    try:
        key = f"user_rpg_{user_id}"
        db[key] = data
        return True
    except Exception as e:
        logger.error(f"Error updating user RPG data for {user_id}: {e}")
        return False

def ensure_user_exists(user_id: str) -> bool:
    """Ensure user exists in database, create if not."""
    try:
        key = f"user_rpg_{user_id}"
        if key not in db:
            return create_user_profile(user_id)
        return True
    except Exception as e:
        logger.error(f"Error ensuring user exists {user_id}: {e}")
        return False

def create_user_profile(user_id: str) -> bool:
    """Create a new user profile with default stats."""
    try:
        default_profile = {
            "user_id": user_id,
            "level": 1,
            "xp": 0,
            "max_xp": 100,
            "hp": 100,
            "max_hp": 100,
            "attack": 10,
            "defense": 5,
            "coins": 100,
            "inventory": [],
            "equipped": {
                "weapon": None,
                "armor": None,
                "accessory": None
            },
            "stats": {
                "battles_won": 0,
                "battles_lost": 0,
                "items_found": 0,
                "bosses_defeated": 0
            },
            "adventure_count": 0,
            "work_count": 0,
            "daily_streak": 0,
            "last_daily": None,
            "last_work": None,
            "last_adventure": None,
            "luck_points": 0,
            "created_at": str(db.get("timestamp", ""))
        }
        
        key = f"user_rpg_{user_id}"
        db[key] = default_profile
        
        # Update global user count
        global_settings = db.get("global_settings", {})
        global_settings["total_users"] = global_settings.get("total_users", 0) + 1
        db["global_settings"] = global_settings
        
        logger.info(f"Created new user profile for {user_id}")
        return True
    except Exception as e:
        logger.error(f"Error creating user profile for {user_id}: {e}")
        return False

def get_leaderboard(category: str, guild_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """Get leaderboard data for a specific category."""
    try:
        users = []
        
        # Get all user keys
        user_keys = [key for key in db.keys() if key.startswith("user_rpg_")]
        
        for key in user_keys:
            try:
                user_data = dict(db[key])
                user_id = user_data.get("user_id")
                
                if not user_id:
                    continue
                    
                value = user_data.get(category, 0)
                users.append({
                    "user_id": user_id,
                    "value": value
                })
            except Exception as e:
                logger.warning(f"Error processing user data for leaderboard: {e}")
                continue
        
        # Sort by value (descending)
        users.sort(key=lambda x: x["value"], reverse=True)
        
        return users[:limit]
    except Exception as e:
        logger.error(f"Error getting leaderboard for {category}: {e}")
        return []

def get_guild_data(guild_id: int) -> Dict[str, Any]:
    """Get guild-specific data."""
    try:
        key = f"guild_{guild_id}"
        if key in db:
            return dict(db[key])
        
        # Create default guild data
        default_guild = {
            "guild_id": guild_id,
            "modules": {
                "rpg": True,
                "economy": True,
                "moderation": True,
                "ai": True
            },
            "prefix": "$",
            "ai_channels": [],
            "mod_log_channel": None,
            "auto_mod": False,
            "settings": {}
        }
        
        db[key] = default_guild
        return default_guild
    except Exception as e:
        logger.error(f"Error getting guild data for {guild_id}: {e}")
        return {}

def update_guild_data(guild_id: int, data: Dict[str, Any]) -> bool:
    """Update guild data in database."""
    try:
        key = f"guild_{guild_id}"
        db[key] = data
        return True
    except Exception as e:
        logger.error(f"Error updating guild data for {guild_id}: {e}")
        return False

def get_user_warnings(user_id: int, guild_id: int) -> List[Dict[str, Any]]:
    """Get user warnings for a specific guild."""
    try:
        key = f"warnings_{guild_id}_{user_id}"
        if key in db:
            return list(db[key])
        return []
    except Exception as e:
        logger.error(f"Error getting warnings for {user_id} in {guild_id}: {e}")
        return []

def add_user_warning(user_id: int, guild_id: int, reason: str, moderator_id: int) -> bool:
    """Add a warning to a user."""
    try:
        key = f"warnings_{guild_id}_{user_id}"
        warnings = db.get(key, [])
        
        warning = {
            "reason": reason,
            "moderator_id": moderator_id,
            "timestamp": str(db.get("timestamp", ""))
        }
        
        warnings.append(warning)
        db[key] = warnings
        
        return True
    except Exception as e:
        logger.error(f"Error adding warning for {user_id} in {guild_id}: {e}")
        return False

def clear_user_warnings(user_id: int, guild_id: int) -> bool:
    """Clear all warnings for a user."""
    try:
        key = f"warnings_{guild_id}_{user_id}"
        if key in db:
            del db[key]
        return True
    except Exception as e:
        logger.error(f"Error clearing warnings for {user_id} in {guild_id}: {e}")
        return False

def get_conversation_history(user_id: int, guild_id: int) -> List[Dict[str, Any]]:
    """Get AI conversation history for a user."""
    try:
        key = f"conversation_{guild_id}_{user_id}"
        if key in db:
            return list(db[key])
        return []
    except Exception as e:
        logger.error(f"Error getting conversation history for {user_id}: {e}")
        return []

def update_conversation_history(user_id: int, guild_id: int, history: List[Dict[str, Any]]) -> bool:
    """Update AI conversation history."""
    try:
        key = f"conversation_{guild_id}_{user_id}"
        db[key] = history
        return True
    except Exception as e:
        logger.error(f"Error updating conversation history for {user_id}: {e}")
        return False

def clear_conversation_history(user_id: int, guild_id: int) -> bool:
    """Clear AI conversation history."""
    try:
        key = f"conversation_{guild_id}_{user_id}"
        if key in db:
            del db[key]
        return True
    except Exception as e:
        logger.error(f"Error clearing conversation history for {user_id}: {e}")
        return False

def get_user_data(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user data from database."""
    try:
        user_data = db.get(f"user_{user_id}")
        if user_data is None:
            # Create default user data
            default_data = {
                'id': user_id,
                'created_at': datetime.now().isoformat(),
                'last_active': datetime.now().isoformat(),
                'warnings': [],
                'muted_until': None,
                'timeout_count': 0,
                'reputation': 0,
                'notes': []
            }
            db[f"user_{user_id}"] = default_data
            return default_data
        return user_data
    except Exception as e:
        logger.error(f"Error getting user data for {user_id}: {e}")
        return None

def update_user_data(user_id: int, data: Dict[str, Any]) -> bool:
    """Update user data in database."""
    try:
        data['last_active'] = datetime.now().isoformat()
        db[f"user_{user_id}"] = data
        return True
    except Exception as e:
        logger.error(f"Error updating user data for {user_id}: {e}")
        return False

def create_guild_profile(guild_id: int, name: str = "Unknown Guild") -> bool:
    """Create a guild profile in database."""
    try:
        guild_data = {
            'id': guild_id,
            'name': name,
            'created_at': datetime.now().isoformat(),
            'member_count': 0,
            'settings': {},
            'stats': {
                'commands_used': 0,
                'messages_processed': 0,
                'warnings_issued': 0,
                'timeouts_given': 0
            }
        }
        db[f"guild_{guild_id}"] = guild_data
        return True
    except Exception as e:
        logger.error(f"Error creating guild profile for {guild_id}: {e}")
        return False