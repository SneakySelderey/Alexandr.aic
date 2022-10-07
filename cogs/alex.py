from discord.ext import commands
from random import choices, randint
import json
from data.user import User
from data import db_session


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
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.discord_id == message.author.id).first()
            # get already existing database entry for current user
            if user is None:
                new_user = User(discord_id=message.author.id, words='', weights='', images='')
                db_sess.add(new_user)
                db_sess.commit()
            user = db_sess.query(User).filter(User.discord_id == message.author.id).first()
            for word in msg_words:
                if word not in user.words.split(';'):
                    user.words += word + ';'
                    user.weights = str(user.weights) + '1;'
                    # if current message author has used a new word, we add this word to
                    # his words list and to his dictionary with weight of 1
                else:
                    ind = user.words.split(';').index(word)
                    new_weights = str(user.weights).split(';')
                    new_weights[ind] = str(int(new_weights[ind]) + 1)
                    user.weights = ';'.join(new_weights)
                    # if we come across a word author has already used someday,
                    # we increase this words weight by one
            db_sess.commit()
            db_sess.close()
            # update current users entry in database

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
