from discord.ext import commands
from discord import app_commands
import discord
import requests
import json

class WorldStates(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{__name__} is online')

    @app_commands.command(name='worldstates', description='display current world states')
    async def current_world_states(self, interaction: discord.Interaction):
        response = requests.get('https://api.warframestat.us/pc')
        with open('test.json', 'w') as f:
            f.write(json.dumps(response.json()))
        f.close()

async def setup(bot):
    await bot.add_cog(WorldStates(bot))