from discord.ext import commands
from discord import app_commands
from datetime import datetime
import discord
import requests


class WorldStates(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{__name__} is online')

    @app_commands.command(name='worldstates', description='display current world states')
    async def current_world_state(self, interaction: discord.Interaction):
        response = requests.get('https://api.warframestat.us/pc')

        embeds = []
        print('Building embeds...')
        world_embed = discord.Embed()
        world_embed.add_field(
            name='Plains of Eidolon',
            value=generateCycleStateString(
                response.json()['cetusCycle']['state'],
                response.json()['cetusCycle']['expiry']
            )
        )
        world_embed.add_field(
            name='Earth',
            value=generateCycleStateString(
                response.json()['earthCycle']['state'],
                response.json()['earthCycle']['expiry']
            )
        )
        world_embed.add_field(
            name='Cambion Drift',
            value=generateCycleStateString(
                response.json()['cambionCycle']['state'],
                response.json()['cambionCycle']['expiry']
            )
        )
        world_embed.add_field(
            name='Orb Vallis',
            value=generateCycleStateString(
                response.json()['vallisCycle']['state'],
                response.json()['vallisCycle']['expiry']
            )
        )
        world_embed.add_field(
            name='Zariman',
            value=generateCycleStateString(
                response.json()['zarimanCycle']['state'],
                response.json()['zarimanCycle']['expiry']
            )
        )
        world_embed.add_field(
            name='Duviri',
            value=generateCycleStateString(
                response.json()['duviriCycle']['state'],
                response.json()['duviriCycle']['expiry']
            )
        )
        embeds.append(world_embed)
        print('Embeds built')

        await interaction.response.send_message(f'# All Cycles', embed=world_embed, ephemeral=True)

def generateCycleStateString(state: str, expiry: str):
    time_left = datetime.now() - datetime.strptime(expiry, "%Y-%m-%dT%H:%M:%S.%fZ")
    minutes_left, seconds_left = divmod(time_left.total_seconds(), 60)
    time_left_string = f'{round(minutes_left)}m {round(seconds_left)}s'
    if minutes_left >= 60:
        hours_left, minutes_left = divmod(minutes_left, 60)
        time_left_string = f'{round(hours_left)}h {round(minutes_left)}m {round(seconds_left)}s'
    return f'Current State: **{state}**\nTime Left: **{time_left_string}**'

async def setup(bot):
    await bot.add_cog(WorldStates(bot))
