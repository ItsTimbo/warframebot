import json
from code import interact
from sys import intern

from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone, timedelta, tzinfo
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import discord
import requests


class WorldStates(commands.Cog):
    notify_channel = None
    notify_role = None
    guild_id = None
    scheduler = None

    def __init__(self, bot):
        self.bot = bot
        with open('settings.json') as f:
            data = json.load(f)['server']
            self.notify_channel = data['notifyChannel']
            self.notify_role = data['notifyRole']
            self.guild_id = data['guildId']
        f.close()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{__name__} is online')
        self.initiateScheduler()
        await self.initiateNotify()

    @app_commands.command()
    async def debug_notify(self, interaction: discord.Interaction):
        cycle = {
            'name': 'cetusTest',
            'cycle': {
                'state': 'testState'
            }
        }
        print('debugCycle set')

        await self.notify(cycle, 'cetusCycle', seconds_left=310, debug=True)
        await interaction.response.send_message('debug complete', ephemeral=True)

    @app_commands.command()
    async def debug_scheduler(self, interaction: discord.Interaction):
        self.scheduler.print_jobs()
        await interaction.response.send_message('debug complete', ephemeral=True)

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

        await interaction.response.send_message(f'# All Cycles', embed=world_embed, ephemeral=True)  # type: ignore

    def initiateScheduler(self):
        print('Initiating scheduler...')
        self.scheduler = AsyncIOScheduler()
        print('Scheduler initialized')

    async def initiateNotify(self):
        print('Initiating Notify...')
        response = requests.get('https://api.warframestat.us/pc')
        print('response fetched')
        cycles = {
            'cetusCycle': {
                'name': 'Plains of Eidolon',
                'cycle': response.json()['cetusCycle']
            },
            'earthCycle': {
                'name': 'Earth',
                'cycle': response.json()['earthCycle']
            },
            'cambionCycle': {
                'name': 'Cambion Drift',
                'cycle': response.json()['cambionCycle']
            },
            'vallisCycle': {
                'name': 'Orb Vallis',
                'cycle': response.json()['vallisCycle']
            },
            'zarimanCycle': {
                'name': 'Zariman',
                'cycle': response.json()['zarimanCycle']
            },
            'duviriCycle': {
                'name': 'Duviri',
                'cycle': response.json()['duviriCycle']
            }
        }
        print('starting cycles')
        for key, cycle in cycles.items():
            time_left = (
                    datetime.strptime(cycle['cycle']['expiry'], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc)
                    - datetime.now(timezone.utc).replace(tzinfo=timezone.utc))
            print(time_left)
            await self.notify(cycle, key, time_left)
        self.scheduler.start()

    async def notify(self, cycle: dict, world: str, seconds_left: timedelta | None, debug=False):
        print(f'initiating {world} notification')
        if seconds_left is None:
            response = requests.get(f'https://api.warframestat.us/pc/{world}').json()['expiry']
            print('request retrieved')
            seconds_left = (datetime.strptime(response, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc)
                            - datetime.now(timezone.utc).replace(tzinfo=timezone.utc))

        channel = discord.Client.get_channel(self.bot, self.notify_channel)
        guild = discord.Client.get_guild(self.bot, self.guild_id)
        role = guild.get_role(self.notify_role)
        if seconds_left.total_seconds() < 300 or debug:
            minutes_left, seconds_left = divmod(seconds_left.total_seconds(), 60)
            await channel.send(
                f"{role.mention} {cycle['name']} will change from {cycle['cycle']['state']} in " +
                f"{round(minutes_left)}m {round(seconds_left)}s")
            self.scheduler.add_job(
                func=self.notify,
                id=cycle['name'],
                args=[cycle, world],
                next_run_time=datetime.now() + timedelta(seconds=seconds_left + 10)
            )
        elif seconds_left.total_seconds() == 300:
            await channel.send(
                f"{role.mention} {cycle['name']} will change from {cycle['cycle']['state']} in 5m")
            self.scheduler.add_job(
                func=self.notify,
                id=cycle['name'],
                args=[cycle, world],
                next_run_time=datetime.now() + timedelta(seconds=seconds_left.total_seconds() + 10)
            )
        else:
            self.scheduler.add_job(
                func=self.notify,
                id=cycle['name'],
                args=(cycle, world, timedelta(seconds=300)),
                next_run_time=datetime.now() + timedelta(seconds=seconds_left.total_seconds() - 300))
        print(f'{world} notification initiated')


def generateCycleStateString(state: str, expiry: str):
    utc_now = datetime.now(timezone.utc).replace(tzinfo=timezone.utc)
    time_left = datetime.strptime(expiry, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc) - utc_now
    print('time left calculated')
    minutes_left, seconds_left = divmod(time_left.total_seconds(), 60)
    print('minutes and seconds left calculated')
    time_left_string = f'{round(minutes_left)}m {round(seconds_left)}s'
    print('time left string generated')
    if minutes_left >= 60:
        hours_left, minutes_left = divmod(minutes_left, 60)
        time_left_string = f'{round(hours_left)}h {round(minutes_left)}m {round(seconds_left)}s'
    print('sending message...')
    return f'Current State: **{state}**\nTime Left: **{time_left_string}**'


async def setup(bot):
    await bot.add_cog(WorldStates(bot))
