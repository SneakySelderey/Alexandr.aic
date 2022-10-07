from discord.ext import commands
from random import choices, randint
import json


class Alex(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command('help')

    @commands.Cog.listener()
    async def on_message(self, message):
        if '$' != message.content[0] and message.author != self.bot.user:
            msg = message.content
            msg_words = msg.split(' ')
            # get message content if message is not a command for bot and is not a bots output
            for i in [',', '.']:
                msg_words = list(map(lambda x: x.replace(i, ''), msg_words))
            # delete unwanted chars like commas and dots
            with open("dict.json", "r", encoding='utf8') as f:
                words_dict = json.load(f)
            # get already existing json dictionary file
            if str(message.author.id) in words_dict.keys():
                in_dict = [i[0] for i in words_dict[str(message.author.id)]]
                # if message authors id is already among dictionary keys, we get a list of his words
            else:
                words_dict[str(message.author.id)] = []
                in_dict = []
                # if message authors id is not in dictionary, we create a new key
                # in dictionary for him and consider his list of words empty
            if words_dict == {"key": ["value1", "value2"]}:
                words_dict = {str(message.author.id): []}
                in_dict = []
                # we can't load an empty json file, so, if bot has never read any
                # messages yet, there will be a placeholder {"key": ["value1", "value2"]}
                # in json file to avoid any errors
            for word in msg_words:
                if word not in in_dict:
                    words_dict[str(message.author.id)].append([word, 1])
                    in_dict.append(word)
                    # if current message author has used a new word, we add this word to
                    # his words list and to his dictionary with weight of 1
                else:
                    words_dict[str(message.author.id)][in_dict.index(word)][1] += 1
                    # if we come across a word author has already used someday,
                    # we increase this words weight by one
            with open("dict.json", "w", encoding='utf8') as f:
                json.dump(words_dict, f, ensure_ascii=False)
            # write an update json dictionary file

    @commands.command(name='sudo_Alexandr.aic')
    async def random_words(self, ctx):
        with open("dict.json", "r", encoding='utf8') as f:
            data = json.load(f)[str(ctx.message.author.id)]
        # get a list of words from dictionary for message author
        msg = list(choices([i[0] for i in data], weights=[i[1] for i in data], k=randint(5, 15)))
        # choose from 5 to 15 words from authors list of words based on their weight - the greater the weight is, the higher the pobability to choose that word is
        line = ''
        for i in msg:
            line += i + ' '
        await ctx.send(f"""
                        {line}
                        """)
        # compile an output message and send it

    @commands.command(name='help')
    async def help(self, ctx):
        await ctx.send("""```
I return random words from users messages. That's it for now.
$sudo Alexandr.aic```""")
    # help command


def setup(bot):
    bot.add_cog(Alex(bot))
