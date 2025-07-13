import discord
from discord.ext import commands
from discord import app_commands
import psutil
import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import traceback

from config import COLORS, EMOJIS, get_server_config, update_server_config, user_has_permission, is_module_enabled
from utils.helpers import create_embed, format_duration
from utils.database import get_user_data, update_user_data, get_guild_data, update_guild_data

logger = logging.getLogger(__name__)

class ConfigView(discord.ui.View):
    """Interactive configuration view for server settings."""
    
    def __init__(self, guild_id: int):
        super().__init__(timeout=300)
        self.guild_id = guild_id
        self.config = get_server_config(guild_id)
        
    @discord.ui.button(label="📝 Change Prefix", style=discord.ButtonStyle.primary)
    async def change_prefix(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Change server prefix."""
        if not user_has_permission(interaction.user, 'admin'):
            await interaction.response.send_message("❌ You need admin permissions!", ephemeral=True)
            return
            
        modal = PrefixModal(self.guild_id, self.config)
        await interaction.response.send_modal(modal)
        
    @discord.ui.button(label="🔧 Module Settings", style=discord.ButtonStyle.secondary)
    async def module_settings(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Configure modules."""
        if not user_has_permission(interaction.user, 'admin'):
            await interaction.response.send_message("❌ You need admin permissions!", ephemeral=True)
            return
            
        view = ModuleConfigView(self.guild_id)
        embed = create_embed(
            "🔧 Module Configuration",
            "Select which modules to enable or disable:",
            COLORS['info']
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        
    @discord.ui.button(label="🤖 AI Settings", style=discord.ButtonStyle.success)
    async def ai_settings(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Configure AI settings."""
        if not user_has_permission(interaction.user, 'admin'):
            await interaction.response.send_message("❌ You need admin permissions!", ephemeral=True)
            return
            
        view = AIConfigView(self.guild_id)
        embed = create_embed(
            "🤖 AI Configuration",
            "Configure AI chatbot settings:",
            COLORS['info']
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        
    @discord.ui.button(label="🛡️ Moderation Settings", style=discord.ButtonStyle.danger)
    async def mod_settings(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Configure moderation settings."""
        if not user_has_permission(interaction.user, 'admin'):
            await interaction.response.send_message("❌ You need admin permissions!", ephemeral=True)
            return
            
        view = ModerationConfigView(self.guild_id)
        embed = create_embed(
            "🛡️ Moderation Configuration",
            "Configure moderation and auto-moderation settings:",
            COLORS['error']
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class PrefixModal(discord.ui.Modal):
    """Modal for changing server prefix."""
    
    def __init__(self, guild_id: int, config: Dict[str, Any]):
        super().__init__(title="Change Server Prefix")
        self.guild_id = guild_id
        self.config = config
        
        self.prefix_input = discord.ui.TextInput(
            label="New Prefix",
            placeholder="Enter new prefix (e.g., !, ?, $)",
            max_length=5,
            default=config.get('prefix', '$')
        )
        self.add_item(self.prefix_input)
        
    async def on_submit(self, interaction: discord.Interaction):
        """Handle prefix change."""
        new_prefix = self.prefix_input.value.strip()
        
        if not new_prefix:
            await interaction.response.send_message("❌ Prefix cannot be empty!", ephemeral=True)
            return
            
        self.config['prefix'] = new_prefix
        update_server_config(self.guild_id, self.config)
        
        embed = create_embed(
            "✅ Prefix Changed",
            f"Server prefix changed to: `{new_prefix}`",
            COLORS['success']
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

class ModuleConfigView(discord.ui.View):
    """View for configuring modules."""
    
    def __init__(self, guild_id: int):
        super().__init__(timeout=300)
        self.guild_id = guild_id
        self.config = get_server_config(guild_id)
        
    @discord.ui.button(label="🎮 RPG Games", style=discord.ButtonStyle.primary)
    async def toggle_rpg(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Toggle RPG module."""
        self.config['enabled_modules']['rpg'] = not self.config['enabled_modules']['rpg']
        update_server_config(self.guild_id, self.config)
        
        status = "enabled" if self.config['enabled_modules']['rpg'] else "disabled"
        await interaction.response.send_message(f"✅ RPG module {status}!", ephemeral=True)
        
    @discord.ui.button(label="💰 Economy", style=discord.ButtonStyle.success)
    async def toggle_economy(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Toggle economy module."""
        self.config['enabled_modules']['economy'] = not self.config['enabled_modules']['economy']
        update_server_config(self.guild_id, self.config)
        
        status = "enabled" if self.config['enabled_modules']['economy'] else "disabled"
        await interaction.response.send_message(f"✅ Economy module {status}!", ephemeral=True)
        
    @discord.ui.button(label="🤖 AI Chatbot", style=discord.ButtonStyle.secondary)
    async def toggle_ai(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Toggle AI chatbot module."""
        self.config['enabled_modules']['ai_chatbot'] = not self.config['enabled_modules']['ai_chatbot']
        update_server_config(self.guild_id, self.config)
        
        status = "enabled" if self.config['enabled_modules']['ai_chatbot'] else "disabled"
        await interaction.response.send_message(f"✅ AI Chatbot module {status}!", ephemeral=True)
        
    @discord.ui.button(label="🔨 Moderation", style=discord.ButtonStyle.danger)
    async def toggle_moderation(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Toggle moderation module."""
        self.config['enabled_modules']['moderation'] = not self.config['enabled_modules']['moderation']
        update_server_config(self.guild_id, self.config)
        
        status = "enabled" if self.config['enabled_modules']['moderation'] else "disabled"
        await interaction.response.send_message(f"✅ Moderation module {status}!", ephemeral=True)

class AIConfigView(discord.ui.View):
    """View for configuring AI settings."""
    
    def __init__(self, guild_id: int):
        super().__init__(timeout=300)
        self.guild_id = guild_id
        self.config = get_server_config(guild_id)
        
    @discord.ui.button(label="📝 Set AI Channels", style=discord.ButtonStyle.primary)
    async def set_ai_channels(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Set AI channels."""
        modal = AIChannelModal(self.guild_id, self.config)
        await interaction.response.send_modal(modal)

class AIChannelModal(discord.ui.Modal):
    """Modal for setting AI channels."""
    
    def __init__(self, guild_id: int, config: Dict[str, Any]):
        super().__init__(title="Set AI Channels")
        self.guild_id = guild_id
        self.config = config
        
        current_channels = ", ".join([f"<#{ch}>" for ch in config.get('ai_channels', [])])
        
        self.channels_input = discord.ui.TextInput(
            label="AI Channels (mention channels)",
            placeholder="Mention channels where AI should respond (e.g., #general #chat)",
            style=discord.TextStyle.paragraph,
            default=current_channels,
            required=False
        )
        self.add_item(self.channels_input)
        
    async def on_submit(self, interaction: discord.Interaction):
        """Handle AI channel setting."""
        channels_text = self.channels_input.value.strip()
        
        # Extract channel IDs from mentions
        import re
        channel_ids = re.findall(r'<#(\d+)>', channels_text)
        
        self.config['ai_channels'] = [int(ch) for ch in channel_ids]
        update_server_config(self.guild_id, self.config)
        
        if channel_ids:
            channel_mentions = [f"<#{ch}>" for ch in channel_ids]
            embed = create_embed(
                "✅ AI Channels Set",
                f"AI will now respond in: {', '.join(channel_mentions)}",
                COLORS['success']
            )
        else:
            embed = create_embed(
                "✅ AI Channels Cleared",
                "AI will now respond in all channels (when mentioned)",
                COLORS['success']
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class ModerationConfigView(discord.ui.View):
    """View for configuring moderation settings."""
    
    def __init__(self, guild_id: int):
        super().__init__(timeout=300)
        self.guild_id = guild_id
        self.config = get_server_config(guild_id)
        
    @discord.ui.button(label="🛡️ Toggle Auto-Mod", style=discord.ButtonStyle.primary)
    async def toggle_automod(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Toggle auto-moderation."""
        self.config['auto_moderation']['enabled'] = not self.config['auto_moderation']['enabled']
        update_server_config(self.guild_id, self.config)
        
        status = "enabled" if self.config['auto_moderation']['enabled'] else "disabled"
        await interaction.response.send_message(f"✅ Auto-moderation {status}!", ephemeral=True)
        
    @discord.ui.button(label="📝 Set Mod Log", style=discord.ButtonStyle.secondary)
    async def set_mod_log(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Set moderation log channel."""
        modal = ModLogModal(self.guild_id, self.config)
        await interaction.response.send_modal(modal)

class ModLogModal(discord.ui.Modal):
    """Modal for setting mod log channel."""
    
    def __init__(self, guild_id: int, config: Dict[str, Any]):
        super().__init__(title="Set Moderation Log Channel")
        self.guild_id = guild_id
        self.config = config
        
        current_channel = f"<#{config.get('mod_log_channel')}>" if config.get('mod_log_channel') else ""
        
        self.channel_input = discord.ui.TextInput(
            label="Moderation Log Channel",
            placeholder="Mention the channel for moderation logs (e.g., #mod-logs)",
            default=current_channel,
            required=False
        )
        self.add_item(self.channel_input)
        
    async def on_submit(self, interaction: discord.Interaction):
        """Handle mod log channel setting."""
        channel_text = self.channel_input.value.strip()
        
        if not channel_text:
            self.config['mod_log_channel'] = None
            update_server_config(self.guild_id, self.config)
            
            embed = create_embed(
                "✅ Mod Log Cleared",
                "Moderation log channel has been cleared",
                COLORS['success']
            )
        else:
            # Extract channel ID from mention
            import re
            channel_match = re.search(r'<#(\d+)>', channel_text)
            
            if channel_match:
                channel_id = int(channel_match.group(1))
                self.config['mod_log_channel'] = channel_id
                update_server_config(self.guild_id, self.config)
                
                embed = create_embed(
                    "✅ Mod Log Set",
                    f"Moderation logs will be sent to <#{channel_id}>",
                    COLORS['success']
                )
            else:
                embed = create_embed(
                    "❌ Invalid Channel",
                    "Please mention a valid channel (e.g., #mod-logs)",
                    COLORS['error']
                )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class AdminCog(commands.Cog):
    """Admin commands and server management."""
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name='config', help='Interactive server configuration')
    @commands.has_permissions(administrator=True)
    async def config_command(self, ctx):
        """Interactive server configuration."""
        if not is_module_enabled("admin", ctx.guild.id):
            return
            
        view = ConfigView(ctx.guild.id)
        config = get_server_config(ctx.guild.id)
        
        embed = create_embed(
            f"{EMOJIS['admin']} Server Configuration",
            f"**Current Settings:**\n"
            f"• Prefix: `{config.get('prefix', '$')}`\n"
            f"• Currency: {config.get('currency_name', 'coins')}\n"
            f"• AI Channels: {len(config.get('ai_channels', []))} configured\n"
            f"• Auto-Moderation: {'✅' if config.get('auto_moderation', {}).get('enabled', True) else '❌'}\n\n"
            f"Use the buttons below to configure your server:",
            COLORS['info']
        )
        
        await ctx.send(embed=embed, view=view)
        
    @app_commands.command(name="config", description="Interactive server configuration")
    @app_commands.describe()
    async def config_slash(self, interaction: discord.Interaction):
        """Interactive server configuration (slash command)."""
        if not user_has_permission(interaction.user, 'admin'):
            await interaction.response.send_message("❌ You need admin permissions!", ephemeral=True)
            return
            
        if not is_module_enabled("admin", interaction.guild.id):
            await interaction.response.send_message("❌ Admin module is disabled!", ephemeral=True)
            return
            
        view = ConfigView(interaction.guild.id)
        config = get_server_config(interaction.guild.id)
        
        embed = create_embed(
            f"{EMOJIS['admin']} Server Configuration",
            f"**Current Settings:**\n"
            f"• Prefix: `{config.get('prefix', '$')}`\n"
            f"• Currency: {config.get('currency_name', 'coins')}\n"
            f"• AI Channels: {len(config.get('ai_channels', []))} configured\n"
            f"• Auto-Moderation: {'✅' if config.get('auto_moderation', {}).get('enabled', True) else '❌'}\n\n"
            f"Use the buttons below to configure your server:",
            COLORS['info']
        )
        
        await interaction.response.send_message(embed=embed, view=view)
        
    @commands.command(name='stats', help='View bot statistics')
    async def stats_command(self, ctx):
        """View bot statistics."""
        if not is_module_enabled("admin", ctx.guild.id):
            return
            
        embed = await self.create_stats_embed()
        await ctx.send(embed=embed)
        
    @app_commands.command(name="stats", description="View bot statistics")
    async def stats_slash(self, interaction: discord.Interaction):
        """View bot statistics (slash command)."""
        if not is_module_enabled("admin", interaction.guild.id):
            await interaction.response.send_message("❌ Admin module is disabled!", ephemeral=True)
            return
            
        embed = await self.create_stats_embed()
        await interaction.response.send_message(embed=embed)
        
    async def create_stats_embed(self) -> discord.Embed:
        """Create bot statistics embed."""
        try:
            # Get system stats
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Calculate uptime
            uptime = datetime.now() - self.bot.start_time
            uptime_str = format_duration(uptime.total_seconds())
            
            embed = discord.Embed(
                title=f"{EMOJIS['admin']} Bot Statistics",
                color=COLORS['info']
            )
            
            # Bot Stats
            embed.add_field(
                name="🤖 Bot Info",
                value=f"**Servers:** {len(self.bot.guilds)}\n"
                      f"**Users:** {len(self.bot.users)}\n"
                      f"**Uptime:** {uptime_str}\n"
                      f"**Commands:** {len(self.bot.commands)}",
                inline=True
            )
            
            # System Stats
            embed.add_field(
                name="🖥️ System Info",
                value=f"**CPU:** {cpu_percent}%\n"
                      f"**Memory:** {memory.percent}%\n"
                      f"**Disk:** {disk.percent}%\n"
                      f"**Python:** {os.sys.version.split()[0]}",
                inline=True
            )
            
            # Discord Stats
            embed.add_field(
                name="📊 Discord Stats",
                value=f"**Latency:** {round(self.bot.latency * 1000)}ms\n"
                      f"**Shards:** {self.bot.shard_count or 1}\n"
                      f"**Cached Messages:** {len(self.bot.cached_messages)}\n"
                      f"**Voice Clients:** {len(self.bot.voice_clients)}",
                inline=True
            )
            
            embed.set_footer(text=f"Bot ID: {self.bot.user.id}")
            embed.timestamp = datetime.now()
            
            return embed
        except Exception as e:
            logger.error(f"Error creating stats embed: {e}")
            return create_embed("❌ Error", "Failed to generate statistics.", COLORS['error'])
            
    @commands.command(name='reload', help='Reload a cog (Owner only)')
    @commands.is_owner()
    async def reload_command(self, ctx, cog: str = None):
        """Reload a cog."""
        if not cog:
            await ctx.send("❌ Please specify a cog to reload.")
            return
            
        try:
            await self.bot.reload_extension(cog)
            await ctx.send(f"✅ Reloaded cog: `{cog}`")
        except Exception as e:
            await ctx.send(f"❌ Failed to reload cog `{cog}`: {e}")
            
    @app_commands.command(name="reload", description="Reload a cog (Owner only)")
    @app_commands.describe(cog="The cog to reload")
    async def reload_slash(self, interaction: discord.Interaction, cog: str):
        """Reload a cog (slash command)."""
        if interaction.user.id != self.bot.owner_id:
            await interaction.response.send_message("❌ Owner only command!", ephemeral=True)
            return
            
        try:
            await self.bot.reload_extension(cog)
            await interaction.response.send_message(f"✅ Reloaded cog: `{cog}`", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to reload cog `{cog}`: {e}", ephemeral=True)
            
    @commands.command(name='sync', help='Sync slash commands (Owner only)')
    @commands.is_owner()
    async def sync_command(self, ctx):
        """Sync slash commands."""
        try:
            synced = await self.bot.tree.sync()
            await ctx.send(f"✅ Synced {len(synced)} slash commands.")
        except Exception as e:
            await ctx.send(f"❌ Failed to sync commands: {e}")
            
    @app_commands.command(name="sync", description="Sync slash commands (Owner only)")
    async def sync_slash(self, interaction: discord.Interaction):
        """Sync slash commands (slash command)."""
        if interaction.user.id != self.bot.owner_id:
            await interaction.response.send_message("❌ Owner only command!", ephemeral=True)
            return
            
        try:
            synced = await self.bot.tree.sync()
            await interaction.response.send_message(f"✅ Synced {len(synced)} slash commands.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to sync commands: {e}", ephemeral=True)

async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(AdminCog(bot))
