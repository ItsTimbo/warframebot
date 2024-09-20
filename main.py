import json

import discord
import os
import asyncio
from discord.ext import commands

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')


@bot.tree.command(name='sync', description='Sync command tree')
async def sync_tree(interaction: discord.Interaction):
    if interaction.user.guild_permissions.administrator:
        try:
            synced = await bot.tree.sync()
            print(f'Synced: {len(synced)} command/s')
        except Exception as e:
            print('error syncing: ', e)
    await interaction.response.send_message(f'Commands were synced.', ephemeral=True)  # type: ignore


async def load():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')


async def main():
    with open('settings.json', 'r') as file:
        data = json.load(file)['discord']
    async with bot:
        await load()
        await bot.start(data['token'])
        await sync_tree()


asyncio.run(main())
