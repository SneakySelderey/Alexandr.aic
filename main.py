import asyncio
import discord
from discord.ext import commands
import logging
from decouple import config
from data import db_session
from help_command import SupremeHelpCommand


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
dashes = ['\u2680', '\u2681', '\u2682', '\u2683', '\u2684', '\u2685']

bot = commands.Bot(command_prefix='$', intents=intents, activity=discord.Activity(type=discord.ActivityType.listening, name="SCP Foundation databases"), log_level=logging.DEBUG)
bot.help_command = SupremeHelpCommand()
TOKEN = config('DISCORD_TOKEN', default='not found')


async def main():
    async with bot:
        await bot.load_extension('cogs.alex')
        await bot.start(TOKEN)


if __name__ == '__main__':
    db_session.global_init("dict.db")
    asyncio.run(main())
