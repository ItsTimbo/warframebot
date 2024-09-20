from discord.ext import commands
from discord import app_commands
import discord

class Debug(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{__name__} is online')

    @app_commands.command()
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message('Pong! {0}s'.format(round(self.bot.latency, 1)), ephemeral=True)

async def setup(bot):
    await bot.add_cog(Debug(bot))