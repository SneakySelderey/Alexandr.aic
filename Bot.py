import asyncio
import discord
from discord.ext import commands
# import logging
from decouple import config
from random import choices, randint
import json


intents = discord.Intents.default()
intents.members = True
dashes = ['\u2680', '\u2681', '\u2682', '\u2683', '\u2684', '\u2685']


class Alex(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command('help')

    @commands.Cog.listener()
    async def on_message(self, message):
        if '$' not in message.content and message.author != self.bot.user:
            msg = message.content
            msg_words = msg.split(' ')
            for i in [',', '.']:
                msg_words = list(map(lambda x: x.replace(i, ''), msg_words))
            with open("dict.json", "r", encoding='utf8') as f:
                words_dict = json.load(f)
            if str(message.author.id) in words_dict.keys():
                in_dict = [i[0] for i in words_dict[str(message.author.id)]]
            else:
                words_dict[str(message.author.id)] = []
                in_dict = []
            if words_dict == {"key": ["value1", "value2"]}:
                words_dict = {str(message.author.id): []}
                in_dict = []
            for word in msg_words:
                if word not in in_dict:
                    words_dict[str(message.author.id)].append([word, 1])
                    in_dict.append(word)
                else:
                    words_dict[str(message.author.id)][in_dict.index(word)][1] += 1
            with open("dict.json", "w", encoding='utf8') as f:
                json.dump(words_dict, f, ensure_ascii=False)

    @commands.command(name='sudo_Alexandr.aic')
    async def random_words(self, ctx):
        with open("dict.json", "r", encoding='utf8') as f:
            data = json.load(f)[str(ctx.message.author.id)]
        msg = list(choices([i[0] for i in data], weights=[i[1] for i in data], k=randint(5, 15)))
        line = ''
        for i in msg:
            line += i + ' '
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
