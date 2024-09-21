import json

from discord.ext import commands
from discord import app_commands
import discord


class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{__name__} is online')

    @app_commands.command(name='notify', description='toggle notification for cycles')
    @app_commands.describe(cycle='world cycles')
    @app_commands.choices(cycle=[
        app_commands.Choice(name='Plains of Eidolon', value='Cetus'),
        app_commands.Choice(name='Earth', value='Earth')
    ])
    async def setNotification(self, interaction: discord.Interaction, cycle: app_commands.Choice[str]):
        with open('settings.json', 'r') as f:
            data = json.load(f)
            f.close()

        data['cycles'][cycle.value]['notify'] = not data['cycles'][cycle.value]['notify']

        with open('settings.json', 'w') as f:
            f.write(json.dumps(data))
            f.close()

        await interaction.response.send_message(
            f'Notification for {cycle.value} set to {data['cycles'][cycle.value]['notify']}', ephemeral=True)

    @app_commands.command(name='notify_channel', description='change notify channel')
    async def setNotifyChannel(self, interaction: discord.Interaction):
        with open('settings.json', 'r') as f:
            data = json.load(f)

        data['server']['notifyChannel'] = interaction.channel_id

        with open('settings.json', 'w') as f:
            f.write(json.dumps(data))

        await interaction.response.send_message('Notification Channel has been set to this channel', ephemeral=True)

    @app_commands.command(name='notify_role', description='change notify role')
    async def setNotifyRole(self, interaction: discord.Interaction, role: discord.Role):
        with open('settings.json', 'r') as f:
            data = json.load(f)

        data['server']['notifyRole'] = role.id
        data['server']['guildId'] = interaction.guild.id

        with open('settings.json', 'w') as f:
            f.write(json.dumps(data))

        await interaction.response.send_message(f'Notify Role has been set', ephemeral=True)


async def setup(bot):
    await bot.add_cog(Config(bot))
