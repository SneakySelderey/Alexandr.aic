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
        '''checks every message'''
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
                    # his words list and to his database entry with weight of 1
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

    @commands.command(name='Alexandr.aic')
    async def random_words(self, ctx):
        '''sends a message compiled from random words from users entry in database'''
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.discord_id == ctx.message.author.id).first()
        # get a list of words from database for message author
        if user is not None:
            msg = list(choices([i for i in user.words.split(';')[:-1]], weights=map(int, [i for i in user.weights.split(';')[:-1]]), k=randint(5, 15)))
            # choose from 5 to 15 words from authors list of words based on their weight -
            # - the greater the weight is, the higher the pobability to choose that word is
            msg = ' '.join(msg)
            await ctx.send(msg)
            # compile an output message and send it
        else:
            await ctx.send('Your database entry is empty')

    @commands.command(name='delete_my_entry')
    async def delete_my_entry(self, ctx):
        '''deletes users entry from database'''
        db_sess = db_session.create_session()
        db_sess.query(User).filter(User.discord_id == ctx.message.author.id).delete()
        # delete message authors entry from database
        db_sess.execute('UPDATE sqlite_sequence SET seq = (SELECT MAX(id) FROM users) WHERE name="users"')
        # update (reset) the autoincrement row (id) so we don't skip numbers
        db_sess.commit()
        db_sess.close()
        await ctx.send(f'{ctx.message.author.mention} your database entry has been deleted succesfully')
        # send a message about succesful deletion

    @commands.command(name='help')
    async def help(self, ctx):
        await ctx.send("""```
I return random words from users messages. That's it for now.
$Alexandr.aic```""")
    # help command


async def setup(bot):
    await bot.add_cog(Alex(bot))
