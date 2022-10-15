import asyncio
from discord.ext import commands
from discord import File
from random import choices, randint
from data.user import User
from data import db_session
import os


class Alex(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        '''checks every message'''
        if (message.content != '' and '$' not in message.content and message.author != self.bot.user) or (message.content == '' and len(message.attachments) > 0):
            if message.content != '':
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
                    new_user = User(discord_id=message.author.id, words='', weights='', files='')
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
            if len(message.attachments) > 0:
                db_sess = db_session.create_session()
                user = db_sess.query(User).filter(User.discord_id == message.author.id).first()
                if f'{message.author.id}' not in os.listdir('attachments'):
                    os.makedirs(f'attachments/{message.author.id}')
                for att in message.attachments:
                    path = f"attachments/{message.author.id}/{att.url.split('/')[-1]}"
                    await att.save(path)
                    if path not in user.files.split(';'):
                        user.files += path + ';'
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
            msg = list(choices(user.words.split(';')[:-1], weights=map(int, user.weights.split(';')[:-1]), k=randint(5, 15)))
            # choose from 5 to 15 words from authors list of words based on their weight -
            # - the greater the weight is, the higher the pobability to choose that word is
            msg = ' '.join(msg)
            if randint(1, 10) > 7 and user.files != '':
                f = list(choices(user.files.split(';'), k=1))
                f = File(f[0])
                await ctx.send(file=f, content=msg)
            else:
                await ctx.send(msg)
            # compile an output message and send it
        else:
            await ctx.reply('Your database entry is empty')
        db_sess.commit()
        db_sess.close()

    @commands.command(name='delete_from_entry')
    async def delete_from_entry(self, ctx, users, words):
        '''deletes words from entries in database'''
        if len(users) == 0:
            await ctx.reply('No users specified')
            # send a message about error
        if len(words) == 0:
            await ctx.reply('No words specified')
            # send a message about error
        elif (len(users) == 1 and users[0] == ctx.message.author.id and len(words) > 0) or (ctx.message.author.guild_permissions.administrator is True and len(words) > 0):
            # if message author specified only themself in users or if message author is an admin
            db_sess = db_session.create_session()
            users = list(map(lambda x: int(x[2:-1]), users.split(' ')))
            # get clear integers as users ids
            words = words.split(' ')
            for user in users:
                entry = db_sess.query(User).filter(User.discord_id == user).first()
                # find user in database by discord id
                if entry is not None:
                    # if user in database
                    words_list = entry.words.split(';')
                    weights_list = entry.weights.split(';')
                    # get users words and their weights in format of list
                    for word in words:
                        index = words_list.index(word)
                        del words_list[index]
                        del weights_list[index]
                        # delete specified words and their weights from lists
                    entry.weights = ';'.join(weights_list)
                    entry.words = ';'.join(words_list)
                    # change users words and their weights in database
                    db_sess.commit()
                    # save changes
            await ctx.reply('Database entries have been redacted successfully')
            db_sess.close()
        elif len(words) == 0:
            await ctx.reply('Incorrect arguments')
        else:
            await ctx.reply('You need admin permissions to send such requests')

    @commands.command(name='delete_entries')
    async def delete_entries(self, ctx, *users):
        '''deletes entries from database'''
        db_sess = db_session.create_session()
        users = list(map(lambda x: int(x[2:-1]), users))
        # get clear integers as users ids
        if (len(users) == 1 and users[0] == ctx.message.author.id) or (ctx.message.author.guild_permissions.administrator is True):
            # if message author specified only themself in users or if message author is an admin
            for user in users:
                db_sess.query(User).filter(User.discord_id == user).delete()
                # delete users entries from database
            db_sess.execute('UPDATE sqlite_sequence SET seq = (SELECT MAX(id) FROM users) WHERE name="users"')
            # update (reset) the autoincrement row (id) so we don't skip numbers
            db_sess.commit()
            db_sess.close()
            await ctx.reply('Database entries have been deleted successfully')
            # send a message about successful deletion
        elif len(users) == 0:
            await ctx.reply('No users specified')
            # send a message about error
        else:
            await ctx.reply('You need admin permissions to send such requests')

    @commands.command(name='clear_database')
    async def clear_database(self, ctx):
        '''wipes out the database'''
        if ctx.message.author.guild_permissions.administrator is True:
            try:
                await ctx.reply('Are you sure about that? Respond in 30 seconds. $Y/$N')
                respond = await self.bot.wait_for("message", check=lambda x: x.author.id == ctx.author.id and (x.content.lower() == "$y" or x.content.lower() == "$n"), timeout=30.0)
            except asyncio.TimeoutError:
                await ctx.reply("Request timed out")
            if respond.content.lower() == "$y":
                db_sess = db_session.create_session()
                db_sess.query(User).delete()
                db_sess.execute('UPDATE sqlite_sequence SET seq = (SELECT MAX(id) FROM users) WHERE name="users"')
                await ctx.reply(f"Database has been wiped out successfully")
                db_sess.commit()
                db_sess.close()
            else:
                await ctx.reply("Request cancelled")
        else:
            await ctx.reply('You need admin permissions to send such requests')

    @commands.command(name='debug_$Alexandr.aic')
    @commands.is_owner()
    async def debug_random_messages(self, ctx, user):
        '''DEBUG COMMAND | sends a message compiled from random words from specified users entry in database'''
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.discord_id == int(user)).first()
        # get a list of words from database for message author
        if user is not None:
            msg = list(choices(user.words.split(';')[:-1], weights=map(int, user.weights.split(';')[:-1]), k=randint(5, 15)))
            # choose from 5 to 15 words from authors list of words based on their weight -
            # - the greater the weight is, the higher the pobability to choose that word is
            msg = ' '.join(msg)
            if randint(1, 10) > 7 and user.files != '':
                f = list(choices(user.files.split(';'), k=1))
                f = File(f[0])
                await ctx.send(file=f, content=msg)
            else:
                await ctx.send(msg)
            # compile an output message and send it
        else:
            await ctx.reply('Your database entry is empty')
        db_sess.commit()
        db_sess.close()


async def setup(bot):
    await bot.add_cog(Alex(bot))
