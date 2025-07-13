import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import logging

from config import COLORS, EMOJIS, get_server_config, is_module_enabled
from utils.helpers import create_embed, format_number, create_progress_bar
from utils.database import get_user_rpg_data, update_user_rpg_data, ensure_user_exists, create_user_profile, get_leaderboard
from utils.constants import RPG_CONSTANTS, WEAPONS, ARMOR, RARITY_COLORS, RARITY_WEIGHTS, PVP_ARENAS, OMNIPOTENT_ITEM
from utils.rng_system import roll_with_luck, check_rare_event, get_luck_status, generate_loot_with_luck, weighted_random_choice
from replit import db

logger = logging.getLogger(__name__)

def level_up_player(player_data):
    """Check and handle level ups."""
    current_level = player_data.get('level', 1)
    current_xp = player_data.get('xp', 0)

    # Calculate XP needed for next level
    base_xp = 100
    xp_needed = int(base_xp * (1.5 ** (current_level - 1)))

    if current_xp >= xp_needed:
        # Level up!
        new_level = current_level + 1
        remaining_xp = current_xp - xp_needed

        # Update stats
        player_data['level'] = new_level
        player_data['xp'] = remaining_xp
        player_data['max_xp'] = int(base_xp * (1.5 ** (new_level - 1)))

        # Increase stats
        player_data['max_hp'] = player_data.get('max_hp', 100) + 10
        player_data['hp'] = player_data.get('max_hp', 100)  # Full heal on level up
        player_data['attack'] = player_data.get('attack', 10) + 2
        player_data['defense'] = player_data.get('defense', 5) + 1

        return f"🎉 Level {new_level}! HP+10, ATK+2, DEF+1"

    player_data['max_xp'] = xp_needed
    return None

def get_random_adventure_outcome():
    """Get a random adventure outcome."""
    outcomes = [
        {
            'description': 'You discovered a hidden treasure chest!',
            'coins': (50, 150),
            'xp': (20, 50),
            'items': ['Health Potion', 'Iron Sword', 'Leather Armor']
        },
        {
            'description': 'You defeated a group of bandits!',
            'coins': (30, 100),
            'xp': (15, 40),
            'items': ['Health Potion', 'Lucky Charm']
        },
        {
            'description': 'You helped a merchant and received a reward!',
            'coins': (40, 120),
            'xp': (10, 30),
            'items': ['Health Potion', 'Iron Sword']
        },
        {
            'description': 'You found rare materials while exploring!',
            'coins': (20, 80),
            'xp': (25, 60),
            'items': ['Health Potion', 'Lucky Charm', 'Iron Sword']
        }
    ]
    return random.choice(outcomes)

def calculate_battle_damage(attack, defense):
    """Calculate battle damage."""
    base_damage = max(1, attack - defense)
    # Add some randomness
    damage = random.randint(int(base_damage * 0.8), int(base_damage * 1.2))
    return max(1, damage)

class ProfileView(discord.ui.View):
    """Interactive profile view."""

    def __init__(self, user: discord.Member, player_data: Dict[str, Any]):
        super().__init__(timeout=300)
        self.user = user
        self.player_data = player_data
        self.current_page = "stats"

    @discord.ui.button(label="📊 Stats", style=discord.ButtonStyle.primary)
    async def stats_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show player stats."""
        if interaction.user != self.user:
            await interaction.response.send_message("This is not your profile!", ephemeral=True)
            return

        embed = self.create_stats_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="🎒 Inventory", style=discord.ButtonStyle.secondary)
    async def inventory_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show player inventory."""
        if interaction.user != self.user:
            await interaction.response.send_message("This is not your profile!", ephemeral=True)
            return

        embed = self.create_inventory_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="🍀 Luck", style=discord.ButtonStyle.success)
    async def luck_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show player luck status."""
        if interaction.user != self.user:
            await interaction.response.send_message("This is not your profile!", ephemeral=True)
            return

        embed = self.create_luck_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    def create_stats_embed(self) -> discord.Embed:
        """Create stats embed."""
        level = self.player_data.get('level', 1)
        xp = self.player_data.get('xp', 0)
        max_xp = self.player_data.get('max_xp', 100)
        hp = self.player_data.get('hp', 100)
        max_hp = self.player_data.get('max_hp', 100)
        attack = self.player_data.get('attack', 10)
        defense = self.player_data.get('defense', 5)
        coins = self.player_data.get('coins', 0)

        # Calculate XP percentage
        xp_percent = (xp / max_xp) * 100 if max_xp > 0 else 0
        hp_percent = (hp / max_hp) * 100 if max_hp > 0 else 0

        embed = discord.Embed(
            title=f"📊 {self.user.display_name}'s Profile",
            color=COLORS['primary']
        )
        embed.set_thumbnail(url=self.user.display_avatar.url)

        embed.add_field(
            name="📊 Level & Experience",
            value=f"**Level:** {level}\n"
                  f"**XP:** {xp:,}/{max_xp:,}\n"
                  f"{create_progress_bar(xp_percent)}",
            inline=True
        )

        embed.add_field(
            name="❤️ Health",
            value=f"**HP:** {hp}/{max_hp}\n"
                  f"{create_progress_bar(hp_percent)}",
            inline=True
        )

        embed.add_field(
            name="💰 Wealth",
            value=f"**Coins:** {format_number(coins)}",
            inline=True
        )

        embed.add_field(
            name="⚔️ Combat Stats",
            value=f"**Attack:** {attack}\n"
                  f"**Defense:** {defense}",
            inline=True
        )

        # Stats
        stats = self.player_data.get('stats', {})
        embed.add_field(
            name="📈 Statistics",
            value=f"**Battles Won:** {stats.get('battles_won', 0)}\n"
                  f"**Adventures:** {self.player_data.get('adventure_count', 0)}\n"
                  f"**Work Count:** {self.player_data.get('work_count', 0)}",
            inline=True
        )

        return embed

    def create_inventory_embed(self) -> discord.Embed:
        """Create inventory embed."""
        inventory = self.player_data.get('inventory', [])
        equipped = self.player_data.get('equipped', {})

        embed = discord.Embed(
            title=f"🎒 {self.user.display_name}'s Inventory",
            color=COLORS['secondary']
        )

        # Equipped items
        weapon = equipped.get('weapon', 'None')
        armor = equipped.get('armor', 'None')
        accessory = equipped.get('accessory', 'None')

        embed.add_field(
            name="🔧 Equipped",
            value=f"**Weapon:** {weapon}\n"
                  f"**Armor:** {armor}\n"
                  f"**Accessory:** {accessory}",
            inline=False
        )

        # Inventory items
        if inventory:
            items_text = ""
            for item in inventory[:10]:  # Show first 10 items
                items_text += f"• {item}\n"
            if len(inventory) > 10:
                items_text += f"... and {len(inventory) - 10} more items"
        else:
            items_text = "Your inventory is empty!"

        embed.add_field(
            name="📦 Items",
            value=items_text,
            inline=False
        )

        return embed

    def create_luck_embed(self) -> discord.Embed:
        """Create luck embed."""
        luck_status = get_luck_status(str(self.user.id))

        embed = discord.Embed(
            title=f"🍀 {self.user.display_name}'s Luck",
            color=COLORS['success']
        )

        embed.add_field(
            name="🎲 Luck Status",
            value=f"**Level:** {luck_status['emoji']} {luck_status['level']}\n"
                  f"**Points:** {luck_status['points']}\n"
                  f"**Bonus:** +{luck_status['bonus_percent']}%",
            inline=False
        )

        return embed

def generate_random_item():
    """Generate a random item with rarity."""
    # Choose item type
    item_type = random.choice(["weapon", "armor"])
    
    # Choose rarity based on weights
    rarity_list = []
    for rarity, weight in RARITY_WEIGHTS.items():
        rarity_list.extend([rarity] * int(weight * 100))
    
    chosen_rarity = random.choice(rarity_list)
    
    # Get items of chosen rarity
    if item_type == "weapon":
        items = {k: v for k, v in WEAPONS.items() if v["rarity"] == chosen_rarity}
    else:
        items = {k: v for k, v in ARMOR.items() if v["rarity"] == chosen_rarity}
    
    if not items:
        # Fallback to common items
        if item_type == "weapon":
            items = {k: v for k, v in WEAPONS.items() if v["rarity"] == "common"}
        else:
            items = {k: v for k, v in ARMOR.items() if v["rarity"] == "common"}
    
    item_name = random.choice(list(items.keys()))
    return item_name, items[item_name]

def get_rarity_emoji(rarity):
    """Get emoji for rarity."""
    emojis = {
        "common": "⚪",
        "uncommon": "🟢", 
        "rare": "🔵",
        "epic": "🟣",
        "legendary": "🟠",
        "mythic": "🔴",
        "divine": "🟡",
        "omnipotent": "💖"
    }
    return emojis.get(rarity, "⚪")

class AdventureView(discord.ui.View):
    """Interactive adventure view."""

    def __init__(self, user_id: str):
        super().__init__(timeout=300)
        self.user_id = user_id

    @discord.ui.select(
        placeholder="Choose your adventure location...",
        options=[
            discord.SelectOption(
                label="Forest",
                value="Forest",
                description="A peaceful forest with hidden treasures",
                emoji="🌲"
            ),
            discord.SelectOption(
                label="Mountains",
                value="Mountains", 
                description="Treacherous peaks with great rewards",
                emoji="⛰️"
            ),
            discord.SelectOption(
                label="Dungeon",
                value="Dungeon",
                description="Dark underground chambers",
                emoji="🏰"
            ),
            discord.SelectOption(
                label="Desert",
                value="Desert",
                description="Endless sands with ancient secrets",
                emoji="🏜️"
            )
        ]
    )
    async def adventure_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        """Start an adventure."""
        location = select.values[0]

        # Disable the select while processing
        select.disabled = True
        await interaction.response.edit_message(view=self)

        # Process adventure
        await self.process_adventure(interaction, location)

    async def process_adventure(self, interaction: discord.Interaction, location: str):
        """Process the adventure."""
        try:
            player_data = get_user_rpg_data(self.user_id)
            if not player_data:
                await interaction.followup.send("❌ Could not retrieve your data!", ephemeral=True)
                return

            # Get adventure outcome
            outcome = get_random_adventure_outcome()

            # Calculate rewards with luck
            base_coins = random.randint(*outcome['coins'])
            base_xp = random.randint(*outcome['xp'])

            enhanced_rewards = generate_loot_with_luck(self.user_id, {
                'coins': base_coins,
                'xp': base_xp
            })

            coins_earned = enhanced_rewards['coins']
            xp_earned = enhanced_rewards['xp']

            # Random item reward
            items_found = []
            if roll_with_luck(self.user_id, 0.3):  # 30% chance for item
                items_found = [random.choice(outcome['items'])]

            # Update player data
            player_data['coins'] = player_data.get('coins', 0) + coins_earned
            player_data['xp'] = player_data.get('xp', 0) + xp_earned
            player_data['adventure_count'] = player_data.get('adventure_count', 0) + 1

            # Add items to inventory
            if items_found:
                inventory = player_data.get('inventory', [])
                inventory.extend(items_found)
                player_data['inventory'] = inventory

            # Check for level up
            level_up_msg = level_up_player(player_data)

            update_user_rpg_data(self.user_id, player_data)

            # Create result embed
            embed = discord.Embed(
                title=f"🗺️ Adventure Complete - {location}",
                description=outcome['description'],
                color=COLORS['success']
            )

            embed.add_field(
                name="💰 Rewards",
                value=f"**Coins:** {format_number(coins_earned)}\n"
                      f"**XP:** {xp_earned}",
                inline=True
            )

            if items_found:
                embed.add_field(
                    name="📦 Items Found",
                    value="\n".join([f"• {item}" for item in items_found]),
                    inline=True
                )

            if level_up_msg:
                embed.add_field(
                    name="📊 Level Up!",
                    value=level_up_msg,
                    inline=False
                )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Adventure error: {e}")
            await interaction.followup.send("❌ Adventure failed! Please try again.", ephemeral=True)

class ShopView(discord.ui.View):
    """Interactive shop view."""

    def __init__(self, user_id: str):
        super().__init__(timeout=300)
        self.user_id = user_id

    @discord.ui.select(
        placeholder="Choose an item to buy...",
        options=[
            discord.SelectOption(
                label="Iron Sword",
                value="Iron Sword",
                description="Basic weapon (+5 Attack) - 200 coins",
                emoji="⚔️"
            ),
            discord.SelectOption(
                label="Leather Armor",
                value="Leather Armor",
                description="Basic armor (+3 Defense) - 150 coins",
                emoji="🛡️"
            ),
            discord.SelectOption(
                label="Health Potion",
                value="Health Potion",
                description="Restore 50 HP - 25 coins",
                emoji="🧪"
            ),
            discord.SelectOption(
                label="Lucky Charm",
                value="Lucky Charm",
                description="Increases luck (+10 Luck) - 500 coins",
                emoji="🍀"
            )
        ]
    )
    async def shop_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        """Buy an item."""
        item = select.values[0]
        
        # Item prices and stats
        item_data = {
            "Iron Sword": {"price": 200, "type": "weapon", "stats": {"attack": 5}},
            "Leather Armor": {"price": 150, "type": "armor", "stats": {"defense": 3}},
            "Health Potion": {"price": 25, "type": "consumable", "stats": {"hp": 50}},
            "Lucky Charm": {"price": 500, "type": "accessory", "stats": {"luck": 10}}
        }

        await self.process_purchase(interaction, item, item_data[item])

    async def process_purchase(self, interaction: discord.Interaction, item: str, item_data: Dict[str, Any]):
        """Process item purchase."""
        try:
            player_data = get_user_rpg_data(self.user_id)
            if not player_data:
                await interaction.response.send_message("❌ Could not retrieve your data!", ephemeral=True)
                return

            coins = player_data.get('coins', 0)
            price = item_data['price']

            if coins < price:
                await interaction.response.send_message(f"❌ Not enough coins! You need {price} coins but have {coins}.", ephemeral=True)
                return

            # Deduct coins
            player_data['coins'] = coins - price

            # Add item to inventory
            inventory = player_data.get('inventory', [])
            inventory.append(item)
            player_data['inventory'] = inventory

            # Update database
            update_user_rpg_data(self.user_id, player_data)

            embed = discord.Embed(
                title="🛒 Purchase Successful!",
                description=f"You bought **{item}** for {format_number(price)} coins!",
                color=COLORS['success']
            )

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            logger.error(f"Shop error: {e}")
            await interaction.response.send_message("❌ Purchase failed! Please try again.", ephemeral=True)

class LootboxView(discord.ui.View):
    """Lootbox opening view."""

    def __init__(self, user_id: str):
        super().__init__(timeout=300)
        self.user_id = user_id

    @discord.ui.button(label="📦 Open Lootbox", style=discord.ButtonStyle.primary, emoji="🎁")
    async def open_lootbox(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Open a lootbox."""
        player_data = get_user_rpg_data(self.user_id)
        if not player_data:
            await interaction.response.send_message("❌ Could not retrieve your data!", ephemeral=True)
            return

        inventory = player_data.get('inventory', [])
        if "Lootbox" not in inventory:
            await interaction.response.send_message("❌ You don't have any lootboxes!", ephemeral=True)
            return

        # Remove lootbox from inventory
        inventory.remove("Lootbox")
        player_data['inventory'] = inventory

        # Generate loot
        rewards = []
        coins_reward = 0

        # Always get coins
        coins_reward = random.randint(100, 1000)
        
        # Chance for items
        for _ in range(3):  # 3 chances for items
            if roll_with_luck(self.user_id, 0.4):  # 40% chance per roll
                item_name, item_data = generate_random_item()
                rewards.append(item_name)
                inventory.append(item_name)

        # Super rare chance for omnipotent items
        if roll_with_luck(self.user_id, 0.001):  # 0.1% chance
            if random.choice([True, False]):
                rewards.append("World Ender")
                inventory.append("World Ender")
            else:
                rewards.append("Reality Stone")
                inventory.append("Reality Stone")

        player_data['coins'] = player_data.get('coins', 0) + coins_reward
        player_data['inventory'] = inventory
        update_user_rpg_data(self.user_id, player_data)

        # Create result embed
        embed = discord.Embed(
            title="🎁 Lootbox Opened!",
            description=f"**Coins:** {format_number(coins_reward)}",
            color=COLORS['success']
        )

        if rewards:
            items_text = ""
            for item in rewards:
                if item in WEAPONS:
                    rarity = WEAPONS[item]["rarity"]
                elif item in ARMOR:
                    rarity = ARMOR[item]["rarity"]
                elif item == "Reality Stone":
                    rarity = "omnipotent"
                else:
                    rarity = "common"
                
                emoji = get_rarity_emoji(rarity)
                items_text += f"{emoji} **{item}** ({rarity})\n"
            
            embed.add_field(name="🎯 Items Found", value=items_text, inline=False)

        button.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)

class PvPView(discord.ui.View):
    """PvP battle view."""

    def __init__(self, challenger_id: str, target_id: str, arena: str):
        super().__init__(timeout=300)
        self.challenger_id = challenger_id
        self.target_id = target_id
        self.arena = arena
        self.accepted = False

    @discord.ui.button(label="⚔️ Accept Challenge", style=discord.ButtonStyle.success)
    async def accept_challenge(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Accept the PvP challenge."""
        if str(interaction.user.id) != self.target_id:
            await interaction.response.send_message("❌ This challenge is not for you!", ephemeral=True)
            return

        self.accepted = True
        await self.start_pvp_battle(interaction)

    @discord.ui.button(label="❌ Decline", style=discord.ButtonStyle.danger)
    async def decline_challenge(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Decline the PvP challenge."""
        if str(interaction.user.id) != self.target_id:
            await interaction.response.send_message("❌ This challenge is not for you!", ephemeral=True)
            return

        embed = discord.Embed(
            title="❌ Challenge Declined",
            description=f"<@{self.target_id}> declined the challenge.",
            color=COLORS['error']
        )
        
        for item in self.children:
            item.disabled = True
            
        await interaction.response.edit_message(embed=embed, view=self)

    async def start_pvp_battle(self, interaction):
        """Start the actual PvP battle."""
        challenger_data = get_user_rpg_data(self.challenger_id)
        target_data = get_user_rpg_data(self.target_id)

        if not challenger_data or not target_data:
            await interaction.response.send_message("❌ Could not retrieve player data!", ephemeral=True)
            return

        # Calculate battle stats
        challenger_attack = challenger_data.get('attack', 10)
        challenger_hp = challenger_data.get('hp', 100)
        challenger_defense = challenger_data.get('defense', 5)

        target_attack = target_data.get('attack', 10)
        target_hp = target_data.get('hp', 100)
        target_defense = target_data.get('defense', 5)

        # Check for super rare weapons
        challenger_inventory = challenger_data.get('inventory', [])
        target_inventory = target_data.get('inventory', [])

        if "World Ender" in challenger_inventory:
            challenger_attack = 999999
        if "World Ender" in target_inventory:
            target_attack = 999999

        # Battle simulation
        battle_log = []
        turn = 1
        
        while challenger_hp > 0 and target_hp > 0 and turn <= 10:
            # Challenger attacks
            damage = calculate_battle_damage(challenger_attack, target_defense)
            target_hp -= damage
            battle_log.append(f"Round {turn}: Challenger deals {damage} damage!")
            
            if target_hp <= 0:
                break
                
            # Target attacks
            damage = calculate_battle_damage(target_attack, challenger_defense)
            challenger_hp -= damage
            battle_log.append(f"Round {turn}: Target deals {damage} damage!")
            
            turn += 1

        # Determine winner
        arena_data = PVP_ARENAS[self.arena]
        entry_fee = arena_data["entry_fee"]
        winner_reward = entry_fee * arena_data["winner_multiplier"]

        if challenger_hp > target_hp:
            winner = self.challenger_id
            loser = self.target_id
            winner_data = challenger_data
            loser_data = target_data
        else:
            winner = self.target_id
            loser = self.challenger_id
            winner_data = target_data
            loser_data = challenger_data

        # Update winner's data
        winner_data['coins'] = winner_data.get('coins', 0) + winner_reward
        winner_stats = winner_data.get('stats', {})
        winner_stats['pvp_wins'] = winner_stats.get('pvp_wins', 0) + 1
        winner_data['stats'] = winner_stats

        # Update loser's data
        loser_data['coins'] = max(0, loser_data.get('coins', 0) - entry_fee)
        loser_stats = loser_data.get('stats', {})
        loser_stats['pvp_losses'] = loser_stats.get('pvp_losses', 0) + 1
        loser_data['stats'] = loser_stats

        update_user_rpg_data(winner, winner_data)
        update_user_rpg_data(loser, loser_data)

        # Create result embed
        embed = discord.Embed(
            title=f"⚔️ PvP Battle Complete - {self.arena}",
            description=f"**Winner:** <@{winner}>\n**Reward:** {format_number(winner_reward)} coins",
            color=COLORS['success']
        )

        battle_text = "\n".join(battle_log[:6])  # Show first 6 rounds
        embed.add_field(name="🥊 Battle Log", value=battle_text, inline=False)

        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)

class TradeView(discord.ui.View):
    """Trading system view."""

    def __init__(self, trader1_id: str, trader2_id: str):
        super().__init__(timeout=600)
        self.trader1_id = trader1_id
        self.trader2_id = trader2_id
        self.trader1_items = []
        self.trader2_items = []
        self.trader1_coins = 0
        self.trader2_coins = 0
        self.trader1_ready = False
        self.trader2_ready = False

    @discord.ui.button(label="💎 Add Items", style=discord.ButtonStyle.primary)
    async def add_items(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Add items to trade."""
        user_id = str(interaction.user.id)
        if user_id not in [self.trader1_id, self.trader2_id]:
            await interaction.response.send_message("❌ You're not part of this trade!", ephemeral=True)
            return

        await interaction.response.send_message("📝 Please type the item name you want to add to the trade:", ephemeral=True)

    @discord.ui.button(label="💰 Add Coins", style=discord.ButtonStyle.secondary)
    async def add_coins(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Add coins to trade."""
        user_id = str(interaction.user.id)
        if user_id not in [self.trader1_id, self.trader2_id]:
            await interaction.response.send_message("❌ You're not part of this trade!", ephemeral=True)
            return

        await interaction.response.send_message("💰 Please type the amount of coins you want to add:", ephemeral=True)

    @discord.ui.button(label="✅ Ready", style=discord.ButtonStyle.success)
    async def ready_trade(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Mark as ready for trade."""
        user_id = str(interaction.user.id)
        
        if user_id == self.trader1_id:
            self.trader1_ready = True
        elif user_id == self.trader2_id:
            self.trader2_ready = True
        else:
            await interaction.response.send_message("❌ You're not part of this trade!", ephemeral=True)
            return

        if self.trader1_ready and self.trader2_ready:
            await self.execute_trade(interaction)
        else:
            await interaction.response.send_message("✅ You are ready! Waiting for the other trader...", ephemeral=True)

    @discord.ui.button(label="❌ Cancel Trade", style=discord.ButtonStyle.danger)
    async def cancel_trade(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Cancel the trade."""
        embed = discord.Embed(
            title="❌ Trade Cancelled",
            description="The trade has been cancelled.",
            color=COLORS['error']
        )
        
        for item in self.children:
            item.disabled = True
            
        await interaction.response.edit_message(embed=embed, view=self)

    async def execute_trade(self, interaction):
        """Execute the trade between players."""
        trader1_data = get_user_rpg_data(self.trader1_id)
        trader2_data = get_user_rpg_data(self.trader2_id)

        if not trader1_data or not trader2_data:
            await interaction.response.send_message("❌ Could not retrieve trader data!", ephemeral=True)
            return

        # Execute the trade
        # This is a simplified version - in practice you'd want more validation
        
        embed = discord.Embed(
            title="✅ Trade Completed!",
            description="The trade has been successfully completed!",
            color=COLORS['success']
        )

        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)

class BattleView(discord.ui.View):
    """Interactive battle view."""

    def __init__(self, user_id: str, enemy_data: Dict[str, Any]):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.enemy_data = enemy_data

    @discord.ui.button(label="⚔️ Attack", style=discord.ButtonStyle.danger)
    async def attack_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Attack the enemy."""
        await self.process_battle_action(interaction, "attack")

    @discord.ui.button(label="🛡️ Defend", style=discord.ButtonStyle.secondary)
    async def defend_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Defend against enemy attack."""
        await self.process_battle_action(interaction, "defend")

    @discord.ui.button(label="🧪 Use Item", style=discord.ButtonStyle.success)
    async def item_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Use an item."""
        await self.process_battle_action(interaction, "item")

    async def process_battle_action(self, interaction: discord.Interaction, action: str):
        """Process battle action."""
        try:
            player_data = get_user_rpg_data(self.user_id)
            if not player_data:
                await interaction.response.send_message("❌ Could not retrieve your data!", ephemeral=True)
                return

            player_hp = player_data.get('hp', 100)
            player_attack = player_data.get('attack', 10)
            player_defense = player_data.get('defense', 5)

            enemy_hp = self.enemy_data.get('hp', 50)
            enemy_attack = self.enemy_data.get('attack', 8)

            battle_result = ""

            if action == "attack":
                # Player attacks
                damage = calculate_battle_damage(player_attack, 0)
                enemy_hp -= damage
                battle_result += f"You dealt {damage} damage to {self.enemy_data['name']}!\n"

                # Enemy attacks back if still alive
                if enemy_hp > 0:
                    enemy_damage = calculate_battle_damage(enemy_attack, player_defense)
                    player_hp -= enemy_damage
                    battle_result += f"{self.enemy_data['name']} dealt {enemy_damage} damage to you!\n"

            elif action == "defend":
                # Reduced damage when defending
                enemy_damage = calculate_battle_damage(enemy_attack, player_defense * 2)
                player_hp -= enemy_damage
                battle_result += f"You defended! {self.enemy_data['name']} dealt {enemy_damage} damage!\n"

            # Check battle outcome
            if enemy_hp <= 0:
                # Victory
                coins_reward = random.randint(50, 150)
                xp_reward = random.randint(20, 50)
                
                player_data['coins'] = player_data.get('coins', 0) + coins_reward
                player_data['xp'] = player_data.get('xp', 0) + xp_reward
                
                stats = player_data.get('stats', {})
                stats['battles_won'] = stats.get('battles_won', 0) + 1
                player_data['stats'] = stats

                embed = discord.Embed(
                    title="🎉 Victory!",
                    description=f"{battle_result}\n**You defeated {self.enemy_data['name']}!**\n\n"
                               f"**Rewards:**\n"
                               f"Coins: {format_number(coins_reward)}\n"
                               f"XP: {xp_reward}",
                    color=COLORS['success']
                )

                # Disable all buttons
                for item in self.children:
                    item.disabled = True

            elif player_hp <= 0:
                # Defeat
                player_data['hp'] = 0
                stats = player_data.get('stats', {})
                stats['battles_lost'] = stats.get('battles_lost', 0) + 1
                player_data['stats'] = stats

                embed = discord.Embed(
                    title="💀 Defeat!",
                    description=f"{battle_result}\n**You were defeated by {self.enemy_data['name']}!**\n\n"
                               f"You need to heal before your next battle.",
                    color=COLORS['error']
                )

                # Disable all buttons
                for item in self.children:
                    item.disabled = True

            else:
                # Battle continues
                self.enemy_data['hp'] = enemy_hp
                player_data['hp'] = player_hp

                embed = discord.Embed(
                    title=f"⚔️ Battle vs {self.enemy_data['name']}",
                    description=f"{battle_result}\n\n"
                               f"**Your HP:** {player_hp}/{player_data.get('max_hp', 100)}\n"
                               f"**{self.enemy_data['name']} HP:** {enemy_hp}/{self.enemy_data.get('max_hp', enemy_hp)}",
                    color=COLORS['warning']
                )

            # Update player data
            update_user_rpg_data(self.user_id, player_data)

            await interaction.response.edit_message(embed=embed, view=self)

        except Exception as e:
            logger.error(f"Battle error: {e}")
            await interaction.response.send_message("❌ Battle error! Please try again.", ephemeral=True)

class RPGGamesCog(commands.Cog):
    """RPG Games system for the bot."""

    def __init__(self, bot):
        self.bot = bot

    # Slash command versions
    @app_commands.command(name="profile", description="View your character profile")
    @app_commands.describe(member="The member to view (optional)")
    async def profile_slash(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        """View character profile (slash command)."""
        if not is_module_enabled("rpg", interaction.guild_id):
            await interaction.response.send_message("❌ RPG module is disabled!", ephemeral=True)
            return

        target = member or interaction.user
        user_id = str(target.id)

        if not ensure_user_exists(user_id):
            await interaction.response.send_message(f"❌ {target.display_name} hasn't started their adventure yet!", ephemeral=True)
            return

        player_data = get_user_rpg_data(user_id)
        if not player_data:
            await interaction.response.send_message("❌ Could not retrieve profile data.", ephemeral=True)
            return

        view = ProfileView(target, player_data)
        embed = view.create_stats_embed()

        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="start", description="Start your RPG adventure")
    async def start_slash(self, interaction: discord.Interaction):
        """Start RPG adventure (slash command)."""
        if not is_module_enabled("rpg", interaction.guild_id):
            await interaction.response.send_message("❌ RPG module is disabled!", ephemeral=True)
            return

        user_id = str(interaction.user.id)

        # Check if user already exists
        if get_user_rpg_data(user_id):
            await interaction.response.send_message("❌ You've already started your adventure! Use `/profile` to see your stats.", ephemeral=True)
            return

        # Create new user profile
        if create_user_profile(user_id):
            embed = create_embed(
                "🎉 Adventure Started!",
                f"Welcome to your RPG adventure, {interaction.user.mention}!\n\n"
                f"**Starting Stats:**\n"
                f"• Level: 1\n"
                f"• HP: 100/100\n"
                f"• Attack: 10\n"
                f"• Defense: 5\n"
                f"• Coins: 100\n\n"
                f"Use `/profile` to view your character\n"
                f"Use `$adventure` to start exploring\n"
                f"Use `$work` to earn coins\n"
                f"Use `$shop` to buy equipment",
                COLORS['success']
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ Failed to start your adventure. Please try again.", ephemeral=True)

    @commands.command(name='start', help='Start your RPG adventure')
    async def start_command(self, ctx):
        """Start RPG adventure."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)

        # Check if user already exists
        if get_user_rpg_data(user_id):
            await ctx.send("❌ You've already started your adventure! Use `$profile` to see your stats.")
            return

        # Create new user profile
        if create_user_profile(user_id):
            embed = create_embed(
                "🎉 Adventure Started!",
                f"Welcome to your RPG adventure, {ctx.author.mention}!\n\n"
                f"**Starting Stats:**\n"
                f"• Level: 1\n"
                f"• HP: 100/100\n"
                f"• Attack: 10\n"
                f"• Defense: 5\n"
                f"• Coins: 100\n\n"
                f"Use `$profile` to view your character\n"
                f"Use `$adventure` to start exploring\n"
                f"Use `$work` to earn coins\n"
                f"Use `$shop` to buy equipment",
                COLORS['success']
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Failed to start your adventure. Please try again.")

    @commands.command(name='profile', help='View your character profile')
    async def profile_command(self, ctx, member: Optional[discord.Member] = None):
        """View character profile."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        target = member or ctx.author
        user_id = str(target.id)

        if not ensure_user_exists(user_id):
            await ctx.send(f"❌ {target.display_name} hasn't started their adventure yet!")
            return

        player_data = get_user_rpg_data(user_id)
        if not player_data:
            await ctx.send("❌ Could not retrieve profile data.")
            return

        view = ProfileView(target, player_data)
        embed = view.create_stats_embed()

        await ctx.send(embed=embed, view=view)

    @commands.command(name='adventure', help='Go on an adventure')
    @commands.cooldown(1, RPG_CONSTANTS['adventure_cooldown'], commands.BucketType.user)
    async def adventure_command(self, ctx):
        """Go on an adventure."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)

        if not ensure_user_exists(user_id):
            await ctx.send("❌ You need to start your adventure first! Use `$start` command.")
            return

        view = AdventureView(user_id)
        embed = create_embed(
            "🗺️ Choose Your Adventure",
            "Select a location to explore!\n\n"
            "Each location offers different rewards and challenges.",
            COLORS['primary']
        )

        await ctx.send(embed=embed, view=view)

    @commands.command(name='work', help='Work to earn coins')
    @commands.cooldown(1, RPG_CONSTANTS['work_cooldown'], commands.BucketType.user)
    async def work_command(self, ctx):
        """Work to earn coins."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)

        if not ensure_user_exists(user_id):
            await ctx.send("❌ You need to start your adventure first! Use `$start` command.")
            return

        player_data = get_user_rpg_data(user_id)
        if not player_data:
            await ctx.send("❌ Could not retrieve your data.")
            return

        # Work jobs
        jobs = [
            {"name": "Mining", "coins": (50, 100), "xp": (5, 15)},
            {"name": "Farming", "coins": (30, 80), "xp": (3, 10)},
            {"name": "Trading", "coins": (70, 120), "xp": (8, 20)},
            {"name": "Blacksmithing", "coins": (60, 110), "xp": (6, 18)}
        ]

        job = random.choice(jobs)
        coins_earned = random.randint(*job['coins'])
        xp_earned = random.randint(*job['xp'])

        # Apply luck bonus
        enhanced_rewards = generate_loot_with_luck(user_id, {
            'coins': coins_earned,
            'xp': xp_earned
        })

        player_data['coins'] = player_data.get('coins', 0) + enhanced_rewards['coins']
        player_data['xp'] = player_data.get('xp', 0) + enhanced_rewards['xp']
        player_data['work_count'] = player_data.get('work_count', 0) + 1

        # Check for level up
        level_up_msg = level_up_player(player_data)

        update_user_rpg_data(user_id, player_data)

        embed = create_embed(
            f"💼 Work Complete - {job['name']}",
            f"You worked hard and earned rewards!\n\n"
            f"**Rewards:**\n"
            f"Coins: {format_number(enhanced_rewards['coins'])}\n"
            f"XP: {enhanced_rewards['xp']}",
            COLORS['success']
        )

        if level_up_msg:
            embed.add_field(name="📊 Level Up!", value=level_up_msg, inline=False)

        await ctx.send(embed=embed)

    

    @commands.command(name='shop', help='Browse the item shop')
    async def shop_command(self, ctx):
        """Browse the shop."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)

        if not ensure_user_exists(user_id):
            await ctx.send("❌ You need to start your adventure first! Use `$start` command.")
            return

        player_data = get_user_rpg_data(user_id)
        coins = player_data.get('coins', 0) if player_data else 0

        view = ShopView(user_id)
        embed = discord.Embed(
            title="🏪 Item Shop",
            description=f"**Your Coins:** {format_number(coins)}\n\n"
                       "Choose an item to purchase:",
            color=COLORS['warning']
        )

        await ctx.send(embed=embed, view=view)

    @commands.command(name='battle', help='Battle a monster')
    @commands.cooldown(1, RPG_CONSTANTS['battle_cooldown'], commands.BucketType.user)
    async def battle_command(self, ctx):
        """Start a battle with a monster."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)

        if not ensure_user_exists(user_id):
            await ctx.send("❌ You need to start your adventure first! Use `$start` command.")
            return

        player_data = get_user_rpg_data(user_id)
        if not player_data:
            await ctx.send("❌ Could not retrieve your data.")
            return

        if player_data.get('hp', 0) <= 0:
            await ctx.send("❌ You need to heal before you can battle!")
            return

        # Generate random monster
        monsters = [
            {"name": "Goblin", "hp": 30, "attack": 8, "max_hp": 30},
            {"name": "Orc", "hp": 50, "attack": 12, "max_hp": 50},
            {"name": "Skeleton", "hp": 40, "attack": 10, "max_hp": 40},
            {"name": "Troll", "hp": 80, "attack": 15, "max_hp": 80}
        ]

        enemy = random.choice(monsters)

        view = BattleView(user_id, enemy)
        embed = discord.Embed(
            title=f"⚔️ Battle vs {enemy['name']}",
            description=f"A wild {enemy['name']} appears!\n\n"
                       f"**Your HP:** {player_data.get('hp', 100)}/{player_data.get('max_hp', 100)}\n"
                       f"**{enemy['name']} HP:** {enemy['hp']}/{enemy['max_hp']}\n\n"
                       f"Choose your action:",
            color=COLORS['warning']
        )

        await ctx.send(embed=embed, view=view)

    @commands.command(name='equip', help='Equip an item')
    async def equip_command(self, ctx, *, item_name: str):
        """Equip an item."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)

        if not ensure_user_exists(user_id):
            await ctx.send("❌ You need to start your adventure first! Use `$start` command.")
            return

        player_data = get_user_rpg_data(user_id)
        if not player_data:
            await ctx.send("❌ Could not retrieve your data.")
            return

        inventory = player_data.get('inventory', [])
        
        if item_name not in inventory:
            await ctx.send(f"❌ You don't have **{item_name}** in your inventory!")
            return

        # Simple equipment logic
        equipped = player_data.get('equipped', {})
        
        if 'Sword' in item_name:
            equipped['weapon'] = item_name
        elif 'Armor' in item_name:
            equipped['armor'] = item_name
        elif 'Charm' in item_name:
            equipped['accessory'] = item_name

        player_data['equipped'] = equipped
        update_user_rpg_data(user_id, player_data)

        embed = create_embed(
            "🔧 Item Equipped!",
            f"You equipped **{item_name}**!",
            COLORS['success']
        )

        await ctx.send(embed=embed)

    @commands.command(name='inventory', help='View your inventory')
    async def inventory_command(self, ctx):
        """View inventory."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)

        if not ensure_user_exists(user_id):
            await ctx.send("❌ You need to start your adventure first! Use `$start` command.")
            return

        player_data = get_user_rpg_data(user_id)
        if not player_data:
            await ctx.send("❌ Could not retrieve your data.")
            return

        inventory = player_data.get('inventory', [])
        
        if not inventory:
            await ctx.send("❌ Your inventory is empty!")
            return

        embed = discord.Embed(
            title=f"🎒 {ctx.author.display_name}'s Inventory",
            color=COLORS['secondary']
        )

        # Show items
        items_text = ""
        for i, item in enumerate(inventory[:20], 1):  # Show first 20 items
            items_text += f"{i}. {item}\n"

        if len(inventory) > 20:
            items_text += f"... and {len(inventory) - 20} more items"

        embed.add_field(
            name="📦 Items",
            value=items_text or "No items",
            inline=False
        )

        await ctx.send(embed=embed)

    @commands.command(name='heal', help='Heal your character')
    async def heal_command(self, ctx):
        """Heal character."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)

        if not ensure_user_exists(user_id):
            await ctx.send("❌ You need to start your adventure first!")
            return

        player_data = get_user_rpg_data(user_id)
        if not player_data:
            await ctx.send("❌ Could not retrieve your data.")
            return

        hp = player_data.get('hp', 100)
        max_hp = player_data.get('max_hp', 100)
        coins = player_data.get('coins', 0)

        if hp >= max_hp:
            await ctx.send("❌ You're already at full health!")
            return

        heal_cost = RPG_CONSTANTS['heal_cost']
        if coins < heal_cost:
            await ctx.send(f"❌ You need {heal_cost} coins to heal! You have {coins} coins.")
            return

        # Heal player
        player_data['hp'] = max_hp
        player_data['coins'] = coins - heal_cost

        update_user_rpg_data(user_id, player_data)

        embed = create_embed(
            "❤️ Healed!",
            f"You've been fully healed for {heal_cost} coins!\n"
            f"HP: {max_hp}/{max_hp}",
            COLORS['success']
        )

        await ctx.send(embed=embed)

    @commands.command(name='daily', help='Claim your daily reward')
    @commands.cooldown(1, 86400, commands.BucketType.user)  # 24 hour cooldown
    async def daily_command(self, ctx):
        """Claim daily reward."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)

        if not ensure_user_exists(user_id):
            await ctx.send("❌ You need to start your adventure first! Use `$start` command.")
            return

        player_data = get_user_rpg_data(user_id)
        if not player_data:
            await ctx.send("❌ Could not retrieve your data.")
            return

        # Calculate daily reward
        level = player_data.get('level', 1)
        base_reward = 100
        level_bonus = level * 10
        streak = player_data.get('daily_streak', 0) + 1
        streak_bonus = min(streak * 25, 175)  # Max 7 day streak

        coins_reward = base_reward + level_bonus + streak_bonus
        xp_reward = 50 + (level * 5)

        # Update player data
        player_data['coins'] = player_data.get('coins', 0) + coins_reward
        player_data['xp'] = player_data.get('xp', 0) + xp_reward
        player_data['daily_streak'] = streak
        player_data['last_daily'] = datetime.now().isoformat()

        # Check for level up
        level_up_msg = level_up_player(player_data)

        update_user_rpg_data(user_id, player_data)

        embed = create_embed(
            "🎁 Daily Reward Claimed!",
            f"**Coins:** {format_number(coins_reward)}\n"
            f"**XP:** {xp_reward}\n"
            f"**Streak:** {streak} days\n\n"
            f"Come back tomorrow for more rewards!",
            COLORS['success']
        )

        if level_up_msg:
            embed.add_field(name="📊 Level Up!", value=level_up_msg, inline=False)

        await ctx.send(embed=embed)

    @commands.command(name='balance', help='Check your coin balance')
    async def balance_command(self, ctx, member: Optional[discord.Member] = None):
        """Check coin balance."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        target = member or ctx.author
        user_id = str(target.id)

        if not ensure_user_exists(user_id):
            await ctx.send(f"❌ {target.display_name} hasn't started their adventure yet!")
            return

        player_data = get_user_rpg_data(user_id)
        if not player_data:
            await ctx.send("❌ Could not retrieve balance data.")
            return

        coins = player_data.get('coins', 0)

        embed = create_embed(
            f"💰 {target.display_name}'s Balance",
            f"**Coins:** {format_number(coins)}",
            COLORS['warning']
        )

        await ctx.send(embed=embed)

    @commands.command(name='leaderboard', help='View leaderboards')
    async def leaderboard_command(self, ctx, category: str = "level"):
        """View leaderboards."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        valid_categories = ["level", "coins", "adventure_count", "work_count"]
        if category not in valid_categories:
            await ctx.send(f"❌ Invalid category! Valid options: {', '.join(valid_categories)}")
            return

        leaderboard = get_leaderboard(category, ctx.guild.id, 10)

        if not leaderboard:
            await ctx.send("❌ No leaderboard data available yet!")
            return

        embed = discord.Embed(
            title=f"🏆 Leaderboard - {category.title()}",
            color=COLORS['warning']
        )

        description = ""
        for i, entry in enumerate(leaderboard, 1):
            try:
                user = self.bot.get_user(int(entry['user_id']))
                name = user.display_name if user else "Unknown User"
                value = entry['value']

                if category == "coins":
                    value = format_number(value)

                description += f"**{i}.** {name} - {value}\n"
            except:
                continue

        embed.description = description or "No data available"

        await ctx.send(embed=embed)

    @commands.command(name='use', help='Use an item')
    async def use_command(self, ctx, *, item_name: str):
        """Use an item."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)

        if not ensure_user_exists(user_id):
            await ctx.send("❌ You need to start your adventure first! Use `$start` command.")
            return

        player_data = get_user_rpg_data(user_id)
        if not player_data:
            await ctx.send("❌ Could not retrieve your data.")
            return

        inventory = player_data.get('inventory', [])
        
        if item_name not in inventory:
            await ctx.send(f"❌ You don't have **{item_name}** in your inventory!")
            return

        # Use item effects
        if item_name == "Health Potion":
            hp = player_data.get('hp', 100)
            max_hp = player_data.get('max_hp', 100)
            
            if hp >= max_hp:
                await ctx.send("❌ You're already at full health!")
                return
            
            heal_amount = min(50, max_hp - hp)
            player_data['hp'] = hp + heal_amount
            
            # Remove item from inventory
            inventory.remove(item_name)
            player_data['inventory'] = inventory
            
            update_user_rpg_data(user_id, player_data)
            
            await ctx.send(f"❤️ You used **{item_name}** and restored {heal_amount} HP!")
        else:
            await ctx.send(f"❌ **{item_name}** is not a usable item!")

    @app_commands.command(name="pay", description="Pay coins to another user")
    @app_commands.describe(user="The user to pay", amount="Amount of coins to pay")
    async def pay_slash(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        """Pay coins to another user (slash command)."""
        if not is_module_enabled("rpg", interaction.guild_id):
            await interaction.response.send_message("❌ RPG module is disabled!", ephemeral=True)
            return

        if amount <= 0:
            await interaction.response.send_message("❌ Amount must be positive!", ephemeral=True)
            return

        if user.id == interaction.user.id:
            await interaction.response.send_message("❌ You can't pay yourself!", ephemeral=True)
            return

        sender_id = str(interaction.user.id)
        receiver_id = str(user.id)

        if not ensure_user_exists(sender_id):
            await interaction.response.send_message("❌ You need to start your adventure first!", ephemeral=True)
            return

        if not ensure_user_exists(receiver_id):
            await interaction.response.send_message("❌ The target user needs to start their adventure first!", ephemeral=True)
            return

        sender_data = get_user_rpg_data(sender_id)
        receiver_data = get_user_rpg_data(receiver_id)

        if not sender_data or not receiver_data:
            await interaction.response.send_message("❌ Could not retrieve user data!", ephemeral=True)
            return

        sender_coins = sender_data.get('coins', 0)
        if sender_coins < amount:
            await interaction.response.send_message(f"❌ You don't have enough coins! You have {format_number(sender_coins)} coins.", ephemeral=True)
            return

        # Transfer coins
        sender_data['coins'] = sender_coins - amount
        receiver_data['coins'] = receiver_data.get('coins', 0) + amount

        update_user_rpg_data(sender_id, sender_data)
        update_user_rpg_data(receiver_id, receiver_data)

        embed = create_embed(
            "💸 Payment Successful!",
            f"{interaction.user.mention} paid {format_number(amount)} coins to {user.mention}!",
            COLORS['success']
        )

        await interaction.response.send_message(embed=embed)

    @commands.command(name='pay', help='Pay coins to another user')
    async def pay_command(self, ctx, user: discord.Member, amount: int):
        """Pay coins to another user."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        if amount <= 0:
            await ctx.send("❌ Amount must be positive!")
            return

        if user.id == ctx.author.id:
            await ctx.send("❌ You can't pay yourself!")
            return

        sender_id = str(ctx.author.id)
        receiver_id = str(user.id)

        if not ensure_user_exists(sender_id):
            await ctx.send("❌ You need to start your adventure first!")
            return

        if not ensure_user_exists(receiver_id):
            await ctx.send("❌ The target user needs to start their adventure first!")
            return

        sender_data = get_user_rpg_data(sender_id)
        receiver_data = get_user_rpg_data(receiver_id)

        if not sender_data or not receiver_data:
            await ctx.send("❌ Could not retrieve user data!")
            return

        sender_coins = sender_data.get('coins', 0)
        if sender_coins < amount:
            await ctx.send(f"❌ You don't have enough coins! You have {format_number(sender_coins)} coins.")
            return

        # Transfer coins
        sender_data['coins'] = sender_coins - amount
        receiver_data['coins'] = receiver_data.get('coins', 0) + amount

        update_user_rpg_data(sender_id, sender_data)
        update_user_rpg_data(receiver_id, receiver_data)

        embed = create_embed(
            "💸 Payment Successful!",
            f"{ctx.author.mention} paid {format_number(amount)} coins to {user.mention}!",
            COLORS['success']
        )

        await ctx.send(embed=embed)
            
    @commands.command(name='pay', help='Pay coins to another user')
    async def pay_command(self, ctx, member: discord.Member, amount: int):
        """Pay coins to another user."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)
        target_id = str(member.id)

        if not ensure_user_exists(user_id) or not ensure_user_exists(target_id):
            await ctx.send("❌ Both users need to start their adventure first!")
            return

        player_data = get_user_rpg_data(user_id)
        target_data = get_user_rpg_data(target_id)

        if not player_data or not target_data:
            await ctx.send("❌ Could not retrieve user data.")
            return

        coins = player_data.get('coins', 0)

        if amount <= 0:
            await ctx.send("❌ Amount must be positive!")
            return

        if coins < amount:
            await ctx.send(f"❌ You don't have enough coins! You have {coins} coins.")
            return

        # Perform the transaction
        player_data['coins'] = coins - amount
        target_data['coins'] = target_data.get('coins', 0) + amount

        update_user_rpg_data(user_id, player_data)
        update_user_rpg_data(target_id, target_data)

        embed = create_embed(
            "💰 Payment Sent!",
            f"You paid {member.mention} {amount} coins!",
            COLORS['success']
        )

        await ctx.send(embed=embed)

    @commands.command(name='lootbox', help='Open a lootbox for random rewards')
    async def lootbox_command(self, ctx):
        """Open a lootbox."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)

        if not ensure_user_exists(user_id):
            await ctx.send("❌ You need to start your adventure first!")
            return

        view = LootboxView(user_id)
        embed = discord.Embed(
            title="🎁 Lootbox System",
            description="Open lootboxes to get random rewards!\n\n"
                       "**Possible Rewards:**\n"
                       "• Coins (100-1000)\n"
                       "• Random weapons and armor\n"
                       "• Super rare items (0.1% chance)\n\n"
                       "Buy lootboxes from the shop for 1000 coins!",
            color=COLORS['warning']
        )

        await ctx.send(embed=embed, view=view)

    @commands.command(name='pvp', help='Challenge another player to PvP')
    async def pvp_command(self, ctx, member: discord.Member, arena: str = "Colosseum"):
        """Challenge another player to PvP."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)
        target_id = str(member.id)

        if user_id == target_id:
            await ctx.send("❌ You can't fight yourself!")
            return

        if arena not in PVP_ARENAS:
            await ctx.send(f"❌ Invalid arena! Choose from: {', '.join(PVP_ARENAS.keys())}")
            return

        if not ensure_user_exists(user_id) or not ensure_user_exists(target_id):
            await ctx.send("❌ Both players need to start their adventure first!")
            return

        challenger_data = get_user_rpg_data(user_id)
        target_data = get_user_rpg_data(target_id)

        if not challenger_data or not target_data:
            await ctx.send("❌ Could not retrieve player data.")
            return

        entry_fee = PVP_ARENAS[arena]["entry_fee"]
        
        if challenger_data.get('coins', 0) < entry_fee:
            await ctx.send(f"❌ You need {entry_fee} coins to enter {arena}!")
            return

        if target_data.get('coins', 0) < entry_fee:
            await ctx.send(f"❌ {member.mention} needs {entry_fee} coins to enter {arena}!")
            return

        view = PvPView(user_id, target_id, arena)
        embed = discord.Embed(
            title=f"⚔️ PvP Challenge - {arena}",
            description=f"{ctx.author.mention} challenges {member.mention} to battle!\n\n"
                       f"**Arena:** {arena}\n"
                       f"**Entry Fee:** {format_number(entry_fee)} coins\n"
                       f"**Winner Gets:** {format_number(entry_fee * PVP_ARENAS[arena]['winner_multiplier'])} coins",
            color=COLORS['warning']
        )

        await ctx.send(embed=embed, view=view)

    @commands.command(name='trade', help='Trade items with another player')
    async def trade_command(self, ctx, member: discord.Member):
        """Start a trade with another player."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)
        target_id = str(member.id)

        if user_id == target_id:
            await ctx.send("❌ You can't trade with yourself!")
            return

        if not ensure_user_exists(user_id) or not ensure_user_exists(target_id):
            await ctx.send("❌ Both players need to start their adventure first!")
            return

        view = TradeView(user_id, target_id)
        embed = discord.Embed(
            title="🤝 Trade System",
            description=f"Trade between {ctx.author.mention} and {member.mention}\n\n"
                       f"**Instructions:**\n"
                       f"1. Add items and coins you want to trade\n"
                       f"2. Both players click Ready when satisfied\n"
                       f"3. Trade will be executed automatically\n\n"
                       f"**Current Trade:**\nEmpty",
            color=COLORS['primary']
        )

        await ctx.send(embed=embed, view=view)

    @commands.command(name='rarity', help='Check item rarity information')
    async def rarity_command(self, ctx, *, item_name: str = None):
        """Check item rarity information."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        if not item_name:
            embed = discord.Embed(
                title="🌟 Rarity System",
                description="Items have different rarities that affect their power:",
                color=COLORS['primary']
            )

            rarity_info = ""
            for rarity, color in RARITY_COLORS.items():
                emoji = get_rarity_emoji(rarity)
                weight = RARITY_WEIGHTS.get(rarity, 0)
                rarity_info += f"{emoji} **{rarity.title()}** - {weight}% chance\n"

            embed.add_field(name="🎲 Rarity Levels", value=rarity_info, inline=False)
            embed.add_field(
                name="✨ Special Items",
                value="🔥 **World Ender** - Omnipotent weapon that can one-shot anything\n"
                     "💎 **Reality Stone** - Grants power to have any item (except World Ender)",
                inline=False
            )

            await ctx.send(embed=embed)
            return

        # Check specific item
        item_found = False
        item_data = None
        item_type = None

        if item_name in WEAPONS:
            item_data = WEAPONS[item_name]
            item_type = "weapon"
            item_found = True
        elif item_name in ARMOR:
            item_data = ARMOR[item_name]
            item_type = "armor"
            item_found = True
        elif item_name == "Reality Stone":
            item_data = OMNIPOTENT_ITEM["Reality Stone"]
            item_type = "accessory"
            item_found = True

        if not item_found:
            await ctx.send(f"❌ Item '{item_name}' not found!")
            return

        rarity = item_data["rarity"]
        emoji = get_rarity_emoji(rarity)
        color = RARITY_COLORS.get(rarity, COLORS['primary'])

        embed = discord.Embed(
            title=f"{emoji} {item_name}",
            description=f"**Type:** {item_type.title()}\n**Rarity:** {rarity.title()}",
            color=color
        )

        if item_type == "weapon":
            embed.add_field(name="⚔️ Attack", value=str(item_data["attack"]), inline=True)
        elif item_type == "armor":
            embed.add_field(name="🛡️ Defense", value=str(item_data["defense"]), inline=True)

        if item_data.get("special"):
            embed.add_field(name="✨ Special", value=item_data["special"], inline=True)

        await ctx.send(embed=embed)

async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(RPGGamesCog(bot))