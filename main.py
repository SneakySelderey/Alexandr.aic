import asyncio
import discord
from discord.ext import commands
# import logging
from decouple import config
from data import db_session


intents = discord.Intents.default()
intents.members = True
dashes = ['\u2680', '\u2681', '\u2682', '\u2683', '\u2684', '\u2685']


async def main():
    bot = commands.Bot(command_prefix='$', intents=intents, activity=discord.Activity(type=discord.ActivityType.listening, name="SCP Foundation databases"))
    TOKEN = config('DISCORD_TOKEN', default='not found')
    bot.load_extension('cogs.alex')
    await bot.start(TOKEN)


if __name__ == '__main__':
    db_session.global_init("dict.db")
    asyncio.run(main())
