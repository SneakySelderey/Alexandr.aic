import asyncio
import discord
from discord.ext import commands
# import logging
from decouple import config
from random import choices, randint


intents = discord.Intents.default()
intents.members = True
dashes = ['\u2680', '\u2681', '\u2682', '\u2683', '\u2684', '\u2685']


class Alex(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command('help')

    @commands.Cog.listener()
    async def on_message(ctx, message):
        if message.author.id == 358539951651946496 and '$' not in message.content:
            msg = message.content
            msg_words = msg.split(' ')
            for i in [',', '.']:
                msg_words = list(map(lambda x: x.replace(i, ''), msg_words))
            with open('words.txt', 'r', encoding='utf8') as f:
                data = f.readlines()
            with open('words.txt', 'a', encoding='utf8') as f:
                for word in msg_words:
                    if word not in data:  # TODO: Эта строка работает не так, как надо. Написать нормальный алгоритм фильтрования уже записанных слов.
                        f.write(f'{word}\n')

    @commands.command(name='sudo_Alexandr.aic')
    async def random_words(self, ctx):
        with open('words.txt', 'r', encoding='utf8') as f:
            data = f.readlines()
        msg = list(choices(data, k=randint(1, 10)))
        line = ''
        for i in msg:
            line += i.replace('\n', ' ')
        await ctx.send(f"""
                        {line}
                        """)

    @commands.command(name='help')
    async def help(self, ctx):
        await ctx.send("""```
I return random words from Sasha's messages. That's it for now.
$sudo Alexandr.aic```""")


async def main():
    bot = commands.Bot(command_prefix='$', intents=intents, activity=discord.Activity(type=discord.ActivityType.listening, name="SCP Foundation databases"))
    TOKEN = config('DISCORD_TOKEN', default='not found')
    bot.add_cog(Alex(bot))
    await bot.start(TOKEN)


if __name__ == '__main__':
    asyncio.run(main())
