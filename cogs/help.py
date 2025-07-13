import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional, Dict, Any
import logging

from config import COLORS, get_server_config, is_module_enabled
from utils.helpers import create_embed

logger = logging.getLogger(__name__)

class HelpView(discord.ui.View):
    """Interactive help view with category selection."""

    def __init__(self, bot, user: discord.Member):
        super().__init__(timeout=300)
        self.bot = bot
        self.user = user
        self.current_category = "main"

    @discord.ui.select(
        placeholder="Select a command category...",
        options=[
            discord.SelectOption(label="Main Commands", value="main", emoji="🏠"),
            discord.SelectOption(label="RPG Games", value="rpg", emoji="⚔️"),
            discord.SelectOption(label="Moderation", value="moderation", emoji="🛡️"),
            discord.SelectOption(label="AI Chatbot", value="ai", emoji="🤖"),
            discord.SelectOption(label="Admin", value="admin", emoji="⚙️")
        ]
    )
    async def category_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        """Change help category."""
        if interaction.user != self.user:
            await interaction.response.send_message("This help menu is not for you!", ephemeral=True)
            return

        self.current_category = select.values[0]
        embed = self.create_help_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    def create_help_embed(self) -> discord.Embed:
        """Create help embed for current category."""
        embed = discord.Embed(
            title=f"📚 Help - {self.current_category.title()}",
            color=COLORS['primary']
        )

        if self.current_category == "main":
            embed.description = "Basic bot commands and information"
            embed.add_field(
                name="📋 General Commands",
                value="• `/help` - Show this help menu\n"
                      "• `/start` - Start your RPG adventure\n"
                      "• `/profile` - View your character profile\n"
                      "• `/config` - Server configuration (Admin only)",
                inline=False
            )

        elif self.current_category == "rpg":
            embed.description = "RPG gaming commands for adventure and combat"
            embed.add_field(
                name="⚔️ RPG Commands",
                value="• `/start` - Begin your RPG journey\n"
                      "• `/profile` - View character stats\n"
                      "• `/adventure` - Go on adventures\n"
                      "• `/heal` - Heal your character\n"
                      "• `/leaderboard` - View server rankings\n"
                      "• `/battle` - Fight monsters\n"
                      "• `/dungeon` - Enter dungeons\n"
                      "• `/inventory` - View your items\n"
                      "• `/equipment` - Manage equipment\n"
                      "• `/shop` - Buy equipment and items\n"
                      "• `/work` - Work to earn coins\n"
                      "• `/daily` - Claim daily rewards\n"
                      "• `/balance` - Check coin balance\n"
                      "• `/quest` - View and complete quests\n"
                      "• `/craft` - Craft items and equipment",
                inline=False
            )

        elif self.current_category == "moderation":
            embed.description = "Moderation tools for server management"
            embed.add_field(
                name="🛡️ Moderation Commands",
                value="• `/kick` - Kick a member\n"
                      "• `/ban` - Ban a member\n"
                      "• `/warn` - Warn a member\n"
                      "• `/warnings` - View user warnings\n"
                      "• `/purge` - Delete multiple messages\n"
                      "• `/timeout` - Timeout a member\n"
                      "• `/lock` - Lock a channel\n"
                      "• `/unlock` - Unlock a channel\n"
                      "• `/slowmode` - Set channel slowmode\n"
                      "• `/clear_warns` - Clear user warnings",
                inline=False
            )

        elif self.current_category == "ai":
            embed.description = "AI chatbot features for conversation"
            embed.add_field(
                name="🤖 AI Commands",
                value="• `/chat` - Chat with AI\n"
                      "• `/clear_chat` - Clear chat history\n"
                      "• `/ai_status` - Check AI system status\n"
                      "• **Auto-Response** - Just mention me!\n"
                      "• **Context Memory** - I remember our chats\n"
                      "• **Plagg Personality** - Sarcastic and fun responses\n"
                      "• **Natural Language** - Chat like with a friend",
                inline=False
            )

        elif self.current_category == "admin":
            embed.description = "Administrative commands for server owners"
            embed.add_field(
                name="⚙️ Admin Commands",
                value="• `/config` - Interactive server configuration\n"
                      "• `/stats` - View bot statistics\n"
                      "• `/reload` - Reload bot modules\n"
                      "• `/sync` - Sync slash commands\n"
                      "• `/backup` - Backup server data\n"
                      "• `/restore` - Restore server data\n"
                      "• `/reset_user` - Reset user progress\n"
                      "• `/announce` - Send announcements",
                inline=False
            )

        embed.set_footer(text="Use the dropdown menu to browse different categories")
        return embed

class HelpCog(commands.Cog):
    """Help system for the bot."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help', help='Show help information')
    async def help_command(self, ctx, category: Optional[str] = None):
        """Show help information."""
        view = HelpView(self.bot, ctx.author)
        embed = view.create_help_embed()
        await ctx.send(embed=embed, view=view)

    @app_commands.command(name="help", description="Show help information")
    @app_commands.describe(category="Specific category to view (optional)")
    async def help_slash(self, interaction: discord.Interaction, category: Optional[str] = None):
        """Show help information (slash command)."""
        view = HelpView(self.bot, interaction.user)

        if category:
            valid_categories = ["main", "rpg", "moderation", "ai", "admin"]
            if category.lower() in valid_categories:
                view.current_category = category.lower()

        embed = view.create_help_embed()
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="info", description="Show bot information")
    async def info_slash(self, interaction: discord.Interaction):
        """Show bot information."""
        embed = discord.Embed(
            title="🧀 Plagg - AI Chatbot with Game Features",
            description="A comprehensive Discord bot with AI chatbot as the main feature and game features!",
            color=COLORS['primary']
        )

        embed.add_field(
            name="🤖 Main Feature - AI Chat",
            value="• **Smart Conversations** - Just mention me!\n"
                  "• **Plagg's Personality** - Sarcastic and fun\n"
                  "• **Context Memory** - Remembers our chats\n"
                  "• **Google Gemini** - Advanced AI responses\n"
                  "• **Natural Language** - Chat like with a friend",
            inline=True
        )

        embed.add_field(
            name="🎮 Bonus Game Features",
            value="• **RPG System** - Adventures & dungeons\n"
                  "• **Battle System** - Fight monsters\n"
                  "• **Progression** - Level up & get stronger\n"
                  "• **Inventory** - Collect items & gear",
            inline=True
        )

        embed.add_field(
            name="📈 Statistics",
            value=f"• Guilds: {len(self.bot.guilds)}\n"
                  f"• Users: {len(self.bot.users)}\n"
                  f"• Commands: {len(self.bot.commands)}\n"
                  f"• Slash Commands: {len(self.bot.tree.get_commands())}\n"
                  f"• Latency: {round(self.bot.latency * 1000, 2)}ms",
            inline=True
        )

        embed.add_field(
            name="🔗 Links",
            value="• [Support Server](https://discord.gg/your-server)\n"
                  "• [Invite Bot](https://discord.com/api/oauth2/authorize?client_id=YOUR_BOT_ID&permissions=8&scope=bot%20applications.commands)\n"
                  "• [GitHub](https://github.com/your-repo)",
            inline=False
        )

        embed.set_footer(text="Made by NoNameP_P | Use /help to see all available commands")
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(HelpCog(bot))