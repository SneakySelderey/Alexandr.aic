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

    @commands.command(name='delete_from_entry')
    async def delete_from_entry(self, ctx, users, words):
        '''deletes words from entries in database'''
        if len(users) == 0:
            await ctx.send(f'{ctx.message.author.mention} no users specified')
            # send a message about error
        if len(words) == 0:
            await ctx.send(f'{ctx.message.author.mention} no words specified')
            # send a message about error
        elif (len(users) == 1 and users[0] == ctx.message.author.id) or (ctx.message.author.guild_permissions.administrator is True):
            db_sess = db_session.create_session()
            users = list(map(lambda x: int(x[2:-1]), users.split(' ')))
            words = words.split(' ')
            for user in users:
                entry = db_sess.query(User).filter(User.discord_id == user).first()
                if entry is not None:
                    words_list = entry.words.split(';')
                    weights_list = entry.weights.split(';')
                    for word in words:
                        index = words_list.index(word)
                        del words_list[index]
                        del weights_list[index]
                    entry.weights = ';'.join(weights_list)
                    entry.words = ';'.join(words_list)
                    db_sess.commit()
            await ctx.send(f'{ctx.message.author.mention} database entries have been redacted successfully')
            db_sess.close()

    @commands.command(name='delete_entries')
    async def delete_entries(self, ctx, *users):
        '''deletes entries from database'''
        db_sess = db_session.create_session()
        users = list(map(lambda x: int(x[2:-1]), users))
        # get clear integers as users ids
        if (len(users) == 1 and users[0] == ctx.message.author.id) or (ctx.message.author.guild_permissions.administrator is True):
            for user in users:
                db_sess.query(User).filter(User.discord_id == ctx.message.author.id).delete()
                # delete message authors entry from database
            db_sess.execute('UPDATE sqlite_sequence SET seq = (SELECT MAX(id) FROM users) WHERE name="users"')
            # update (reset) the autoincrement row (id) so we don't skip numbers
            db_sess.commit()
            db_sess.close()
            await ctx.send(f'{ctx.message.author.mention} database entries have been deleted successfully')
            # send a message about successful deletion
        elif len(users) == 0:
            await ctx.send(f'{ctx.message.author.mention} no users specified')
            # send a message about error

    @commands.command(name='help')
    async def help(self, ctx):
        '''help command'''
        await ctx.send("""```
I return random words from users messages. That's it for now.

$Alexandr.aic - returns random words from your messages
$delete_my_entry word1 word2 ... - deletes the words you specified after the command from your database entry. If words are not specified, deletes your entry completely.```""")


async def setup(bot):
    await bot.add_cog(Alex(bot))
