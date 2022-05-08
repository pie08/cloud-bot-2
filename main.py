from logging import debug, exception
from operator import mod
from webbrowser import get
from discord import message
from itsdangerous import exc
import nextcord
from nextcord.ext import commands, tasks, menus
from nextcord.ui import view
from nextcord.utils import find
import os
import random
import datetime
from datetime import timedelta
import asyncio
import json
import string
import motor
from motor import motor_asyncio


try:
    cluster = motor_asyncio.AsyncIOMotorClient(
        "mongodb+srv://tyrus:Tyrus113@cluster0.qifea.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")  # here will be the link for your cluster
    db = cluster["cloud_bot"]  # write your db name here
    # write the name of the collection present in the db where data will be stored
    collection = db["data"]
    print('Database Connected Successfully')
except exception as e:
    print('Database Connection Failed')
    print(e)

try:
    cluster = motor_asyncio.AsyncIOMotorClient(
        "mongodb+srv://tyrus:Tyrus113@cluster0.qifea.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")  # here will be the link for your cluster
    db = cluster["cloud_bot"]  # write your db name here
    # write the name of the collection present in the db where data will be stored
    bank = db["bank"]
    print('Database Bank Connected Successfully')
except Exception as e:
    print('Database Bank Connection Failed')
    print(e)


async def get_prefix(client, message):
    result = await collection.find_one({'_id': message.guild.id})
    if result:
        return result['prefix']
    else:
        return '%'

intents = nextcord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix=get_prefix, intents=intents)
client.remove_command("help")

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

@client.event
async def on_ready():
    guilds = 0
    for guild in client.guilds:
        guilds += 1
    all_users = 0
    for user in client.get_all_members():
        all_users += 1
    await client.change_presence(status=nextcord.Status.idle, activity=nextcord.Activity(type=nextcord.ActivityType.watching, name=f'{all_users} users in {guilds} servers!'))
    print(f'Logged In As {client.user}')
    giveaway_check.start()
    warn_reset.start()
    status_update.start()
    while True:
        await asyncio.sleep(5)
        with open('spam_detection.txt', 'r+') as f:
            f.truncate(0)


@client.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        em = nextcord.Embed(title='👍 THANKS FOR INVITING ME',
                            description='**Lets get you started**\n*To see all my commands use `%help`*\n*To setup Welcomes and Leaves use `%welc`*\n*To change config settings use `%bot`*\n*IMPORTANT!! Please make sure to bring my role to the top of the \nhierarchy under settings. \nThis is to make sure all of my commands are functionable for your server*', color=nextcord.Color.green())
        await channel.send(embed=em)
        break

    result = await collection.find_one({'_id': guild.id})
    if not result:
        post = {
            '_id': guild.id,
            'default_channel': guild.text_channels[0].id,
            'welcome_channel': 0,
            'leave_channel': 0,
            'welc': 1,
            "welc_msg": 0,
            'prefix': '%'
        }
        await collection.insert_one(post)


@client.event
async def on_guild_remove(guild):
    result = await collection.find_one({'_id': guild.id})
    if result:
        await collection.delete_one({'_id': guild.id})


def member_count(id):
    count = 0
    guild = client.get_guild(id)
    members = guild.members

    for member in members:
        count = count + 1
    return count


@client.command(name='giveaway', description='%Start a giveaway!')
async def giveaway(ctx):
    if not ctx.author.guild_permissions.manage_messages:
        await ctx.send('This command requires `manage_messages` permissions')
        return
    channel_ask = await ctx.send('Lets setup your giveaway. First, what `channel` do you want your giveaway to be in?\nAlso you may type `cancel` at any time to stop the creation of this giveaway\n\n`Please mention a channel in this server`')
    try:
        giv_channel = await client.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=60)
    except asyncio.TimeoutError:
        await channel_ask.edit(content='`Timed Out! ⌛`')
        return
    if str(giv_channel.content) == 'cancel':
        await ctx.send('`Canceled!`')
        return

    time_ask = await ctx.send(f'Cool! The giveaway will be in {str(giv_channel.content)}! Now how long should the giveaway last for?\n\n`Please enter the duration of the giveaway in seconds. Alternatively, enter a duration in minutes and include an M at the end, a duration for hours enter a H at the end or days and include a D.`')
    try:
        giv_time = await client.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=60)
    except asyncio.TimeoutError:
        await time_ask.edit(content='`Timed Out! ⌛`')
        return
    if str(giv_time.content) == 'cancel':
        await ctx.send('`Canceled!`')
        return

    x = ''
    f = ''
    if str(giv_time.content[-1]).lower() == 'd':
        x = 'days'
        f = str(giv_time.content[:-1])
    elif str(giv_time.content[-1]).lower() == 'h':
        x = 'hours'
        f = str(giv_time.content[:-1])
    elif str(giv_time.content[-1]).lower() == 'm':
        x = 'minutes'
        f = str(giv_time.content[:-1])
    else:
        x = 'seconds'
        f = str(giv_time.content)
    prize_ask = await ctx.send(f'Awesome, The giveaway will last {f} {x}! Finally, what do you want to give away? \n\n`Please enter the giveaway prize. This will also begin the giveaway.`')
    try:
        prize = await client.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=60)
    except asyncio.TimeoutError:
        await prize_ask.edit(content='`Timed out! ⌛`')
    if str(prize.content) == 'cancel':
        await ctx.send('`Canceled!`')
        return

    try:
        f = int(giv_time.content[:-1])
        if str(giv_time.content[-1]).lower() == 'd':
            end_delta = datetime.datetime.now() + timedelta(days=f, hours=0, minutes=0)
        elif str(giv_time.content[-1]).lower() == 'h':
            end_delta = datetime.datetime.now() + timedelta(days=0, hours=f, minutes=0)
        elif str(giv_time.content[-1]).lower() == 'm':
            end_delta = datetime.datetime.now() + timedelta(days=0, hours=0, minutes=f)
        else:
            end_delta = datetime.datetime.now() + timedelta(days=0, hours=0,
                                                            minutes=0, seconds=int(giv_time.content))
    except:
        await ctx.send('Seems like there was a problem, you should make sure you didnt make any mistakes when creating your giveaway.')
        return
    try:
        end_time = end_delta.strftime("%B %d, %Y %I:%M %p")
        em = nextcord.Embed(title=f'{str(prize.content)}',
                            description=f'\nReact with 🎉 to enter \nEnds at : {end_time} \nHost : {ctx.author.mention}', color=nextcord.Color.blue())
        channel = await client.fetch_channel(giv_channel.content[2:-1])
        msg = await channel.send('🎉 **GIVEAWAY** 🎉', embed=em)
        await msg.add_reaction('🎉')
    except:
        await ctx.send('Seems like there was a problem, you should make sure you didnt make any mistakes when creating your giveaway.')

    try:
        post = {
                'guild_id': ctx.guild.id,
                '_id': msg.id,
                'channel_id': channel.id,
                'prize': str(prize.content),
                'host': ctx.author.id,
                'end_time': str(end_delta),
                'emoji': '🎉',
                'giv_list': [],
                'giv': '1'
            }
        await collection.insert_one(post)
    except Exception as e:
        await ctx.send('Error writing giveaway data.')
        print(e)
        return

    await ctx.send(f'Done! The giveaway for the `{str(prize.content)}` is starting in {str(giv_channel.content)}')


@client.event
async def on_raw_reaction_add(payload):
    if payload.member.bot:
        pass
    else:
        result = await collection.find_one({'_id': payload.message_id})
        if result['_id'] == payload.message_id and result['emoji'] == payload.emoji.name:
            await collection.update_one({'_id': payload.message_id}, {'$addToSet': {'giv_list': payload.user_id}})


@client.event
async def on_raw_reaction_remove(payload):
    result = await collection.find_one({'_id': payload.message_id})
    if result['_id'] == payload.message_id and result['emoji'] == payload.emoji.name:
        await collection.update_one({'_id': payload.message_id}, {'$pull': {'giv_list': payload.user_id}})


@client.event
async def on_message(message):
    result = await collection.find_one({'_id': message.guild.id})
    msg_content = message.content.lower()
    user = message.author
    guild = message.guild
    counter = 0

    if message.author.id == client.user.id:
        return
    if result:
        try:
            if message.channel.id in result['blocked_invites']:
                if not message.author.guild_permissions.administrator:
                    if any(word in msg_content for word in ['https://discord.gg']):
                        await message.delete()
                        await message.channel.send(f'{message.author.name}, Please refrain from posting discord invites in this channel')
            elif message.channel.id in result['blocked_links']:
                if not message.author.guild_permissions.administrator:
                    if any(word in msg_content for word in ['https://discord.gg']):
                        await client.process_commands(message)
                        return
                    if any(word in msg_content for word in ['https://', 'http://']):
                        await message.delete()
                        await message.channel.send(f'{message.author.name}, Please refrain from posting links in this channel')
        except:
            pass
    if not result:
        post = {
            '_id': message.guild.id,
            'default_channel': message.guild.text_channels[0].id,
            'welcome_channel': 0,
            'leave_channel': 0,
            'welc': 1,
            "welc_msg": 0,
            'prefix': '%'
        }
        await collection.insert_one(post)

    if str(message.content) == client.user.mention:
        result = await collection.find_one({'_id': message.guild.id})
        prefix = result['prefix']
        await message.channel.send(f'`My prefix is : {prefix}`')

    if user.display_name[:5] == '[AFK]':
        try:
            msg = await message.channel.send("Seems like you're back, removing AFK status")
            await user.edit(nick=user.display_name.replace('[AFK]', ''))
            await asyncio.sleep(10)
            await msg.delete()
        except Exception as e:
            print(e)
    await client.process_commands(message)

    if str(message.content) == '📮':
        await message.reply('i cant take it anymore')
    if str(message.content) == 'sus':
        await message.reply('just stop')

    if result:
        try:
            for x in result['spam_channel']:
                if message.channel.id == x:
                    await client.process_commands(message)
                    return
        except:
            pass
    with open('spam_detection.txt', 'r+') as f:
        for line in f:
            if line.strip('\n') == str(user.id):
                counter += 1
        f.writelines(f'{str(user.id)}\n')
        if counter == 5:
            f.truncate(0)
            muted_role = nextcord.utils.get(guild.roles, name="Muted")
            if not muted_role:
                muted_role = await guild.create_role(name='Muted')
                for channel in guild.text_channels:
                    await channel.set_permissions(muted_role, send_messages=False)
            await user.add_roles(muted_role)
            try:
                await user.send(f'You have been muted in {guild.name} for 10m | Reason, *Spam*')
            except:
                pass
            em = nextcord.Embed(
                title=f'<:check_90:880570776879775835> | *{user} has been muted for 10m due to spam*', color=nextcord.Color.blue())
            await message.channel.send(embed=em)
            await asyncio.sleep(600)
            await user.remove_roles(muted_role)


@client.event
async def on_member_join(member):
    guild = member.guild
    result = await collection.find_one({'_id': guild.id})
    channel = result['default_channel']
    try:
        for x in result['roles']:
            role = nextcord.utils.get(guild.roles, id=x)
            try:
                await member.add_roles(role)
            except:
                pass
    except:
        pass
    if result['welc'] == 0:
        return
    if result['welc_msg'] != 0:
        welc_msg = result['welc_msg'].replace(
            '{members}', str(member_count(guild.id)))
        welc_msg = welc_msg.replace('{member}', member.mention)
        welc_msg = welc_msg.replace('{guild}', guild.name)
    else:
        welc_msg = f'Welcome to {guild.name} {member.mention} ! \n\nMake sure to read our rules \nWe now have {member_count(guild.id)} members! :partying_face:\n'
    if result['welcome_channel'] != 0:
        channel = result['welcome_channel']
    else:
        channel = result['default_channel']
    try:
        if not result['welc_dm'] == 0:
            welc_dm = result['welc_dm']
        else:
            welc_dm = f'Thanks for joining {guild.name}! I hope you enjoy it here!'
    except:
        welc_dm = f'Thanks for joining {guild.name}! I hope you enjoy it here!'

    join_channel = client.get_channel(channel)

    # welcome message
    embed = nextcord.Embed(description=welc_msg, color=nextcord.Color.blue())
    embed.set_author(name='Member Joined')
    embed.set_footer(text='ID :  ' + str(member.id))
    embed.timestamp = datetime.datetime.utcnow()
    await join_channel.send(embed=embed)
    await member.send(welc_dm)


@client.event
async def on_member_remove(member):
    guild = member.guild
    result = await collection.find_one({'_id': guild.id})
    channel = result['default_channel']
    if result['welc'] == 0:
        return
    if result['leave_channel'] != 0:
        channel = result['leave_channel']

    leave_channel = client.get_channel(channel)
    join_date = member.joined_at
    roles = ''

    for role in member.roles[1:]:
        roles = roles + f'{role.mention}' + '  '
    if roles == '':
        roles = 'No roles to display'
    # leave msg
    embed = nextcord.Embed(
        description=f"{member.mention} {member.name}", color=nextcord.Color.red())
    embed.set_author(name='Member Left')
    embed.add_field(name='Roles', value=f'{roles}')
    embed.add_field(name='Join Date', value=join_date.strftime("%m/%d/%Y"))
    embed.set_footer(text='ID :  ' + str(member.id))
    embed.timestamp = datetime.datetime.utcnow()
    await leave_channel.send(embed=embed)


# MOD COMMANDS
@client.command(name='slowmode', description='&Set a slowmode in a channel')
async def slowmode(ctx, seconds: int, channel: nextcord.TextChannel = None):
    if not ctx.author.guild_permissions.manage_messages:
        await ctx.send('This command requires `manage_messages` permission')
        return
    channel = channel or ctx.channel
    await channel.edit(slowmode_delay=seconds)
    await ctx.send(f"<:check_90:881380678938296410> | Set the slowmode delay in {channel.mention} to {seconds} seconds!")


@slowmode.error
async def _(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        em = nextcord.Embed(title='Command: slowmode',
                            description=f'**Usage:** slowmode <seconds> <channel>\n**Example:** slowmode 5 {ctx.channel.mention}')
        await ctx.send(embed=em)


@client.command(name='modnick', description='&Change a users nickname to a moderated one')
async def modnick(ctx, member: nextcord.Member):
    try:
        gen = ''.join(random.choice(string.ascii_uppercase + string.digits)
                      for _ in range(10))
        await member.edit(nick='Moderated Name / ' + gen)
        await ctx.send('<:check_90:881380678938296410> Name successfully changed')
    except:
        await ctx.send('')


@client.command(name='kick', description='&Kick a member from the server')
async def kick(ctx, member: nextcord.Member, *, reason="No reason provided"):
    if not ctx.author.guild_permissions.kick_members:
        await ctx.send('This command requires `kick_members` permission')
        return
    guild = ctx.guild
    try:
        await member.send(f"You have been kicked from {guild.name} for, *{reason}*")
    except:
        pass

    em = nextcord.Embed(
        title=f'<:check_90:880570776879775835> | {member} has been kicked.', color=nextcord.Color.blue())
    await ctx.send(embed=em)
    await member.kick(reason=reason)


@client.command(name='ban', description='&Ban a user from the server')
async def ban(ctx, member: nextcord.Member, *, reason="No reason provided"):
    if not ctx.author.guild_permissions.ban_members:
        await ctx.send('This command requires `ban_members` permission')
        return
    guild = ctx.guild
    try:
        await member.send(f"You have been banned from {guild.name} for, *{reason}*")
    except:
        pass

    em = nextcord.Embed(
        title=f'<:check_90:880570776879775835> | {member} has been banned.', color=nextcord.Color.blue())
    await ctx.send(embed=em)
    await member.ban(reason=reason)


@client.command(name='softban', description='&Ban a member for a period of time')
async def softban(ctx, member: nextcord.Member, time_input='1',  *, reason='No reason provided'):
    if not ctx.author.guild_permissions.ban_members:
        await ctx.send('This command requires `ban_members` permission')
        return
    x = ''
    if time_input[-1].lower() == 'd':
        time = int(time_input[:-1]) * 86400
        x = 'd'
    elif time_input[-1].lower() == 'h':
        time = int(time_input[:-1]) * 3600
        x = 'h'
    elif time_input[-1].lower() == 'm':
        time = int(time_input[:-1]) * 60
        x = 'm'
    else:
        try:
            time = int(time_input)
            x = 's'
        except:
            await ctx.send('`Invalid time format`')
            return
    try:
        await member.send(f'`You have been softbanned from {ctx.guild.name} for {time}{x}` | `Reason - {reason}`')
    except:
        pass
    em = nextcord.Embed(
        title=f'<:check_90:880570776879775835> | *{member} has been softbanned for {time_input}{x}*', color=nextcord.Color.blue())
    await ctx.send(embed=em)
    await member.ban(reason=reason)
    await asyncio.sleep(time)
    await member.unban(reason='Softban ended')


@client.command(name='warn', description='&Warn a member')
async def warn(ctx, member: nextcord.Member, *, reason='No reason provided'):
    if not ctx.author.guild_permissions.manage_messages:
        await ctx.send('This command requires `manage_messages` permission')
        return
    warns = 1
    x = datetime.datetime.now()
    y = x.replace(day=x.day) + timedelta(days=1)
    with open('warns.json') as f:
        data = json.load(f)
        ids = []
        for d in data:
            ids.append(d['user_id'])
        if member.id in ids:
            for d in data:
                if d['user_id'] == member.id:
                    d['warns'] = d['warns'] + 1
        else:
            warn_data = {
                'mod_id': ctx.author.id,
                'user_id': member.id,
                'warns': 1,
                'warn_date': str(x),
                'warn_date_remove': str(y)
            }
            data.append(warn_data)
        for d in data:
            if d['user_id'] == member.id:
                warns = d['warns']

    with open('warns.json', 'w') as f:
        json.dump(data, f, indent=4)
    if warns <= 2:
        em = nextcord.Embed(
            title=f'<:check_90:880570776879775835>  {member} has been warned. {warns}/2 until mute', color=nextcord.Color.blue())
        await ctx.send(embed=em)
    elif warns > 2 and warns <= 4:
        em = nextcord.Embed(
            title=f'<:check_90:880570776879775835>  {member} has been warned. {warns}/4 until kick', color=nextcord.Color.blue())
        await ctx.send(embed=em)
    em = nextcord.Embed(
        title='Warn Result', description=f'You have been warned in {ctx.guild.name} for, *{reason}* \nYou now have {warns} warning(s) in this server', color=nextcord.Color.blue())
    await member.send(embed=em)
    if warns == 2:
        role = nextcord.utils.get(ctx.guild.roles, name="Muted")
        try:
            await member.add_roles(role)
        except:
            em = nextcord.Embed()
        em = nextcord.Embed(
            title=f'<:check_90:880570776879775835>  {member} has been muted for 15 minutes.', color=nextcord.Color.blue())
        await ctx.send(embed=em)
        await asyncio.sleep(900)
        await member.remove_roles(role)
        em = nextcord.Embed(
            title=f'<:check_90:880570776879775835>  {member} has been unmuted.', color=nextcord.Color.blue())
        await ctx.send(embed=em)
    elif warns == 3:
        role = nextcord.utils.get(ctx.guild.roles, name="Muted")
        await member.add_roles(role)
        em = nextcord.Embed(
            title=f'<:check_90:880570776879775835>  {member} has been muted for 30 minutes.', color=nextcord.Color.blue())
        await ctx.send(embed=em)
        await asyncio.sleep(1800)
        await member.remove_roles(role)
        em = nextcord.Embed(
            title=f'<:check_90:880570776879775835>  {member} has been unmuted.', color=nextcord.Color.blue())
        await ctx.send(embed=em)
    elif warns == 4:
        guild = ctx.guild
        try:
            await member.send(f"You have been kicked from {guild.name} for, *Exceding 4 warnings*")
        except:
            pass
        await member.kick(reason='Exceding 4 warnings')
        em = nextcord.Embed(
            title=f'<:check_90:880570776879775835>  {member} has been kicked for *Exceding 4 warnings.*', color=nextcord.Color.blue())
        await ctx.send(embed=em)


@client.command(name='removewarn', description='&Remove a warning from a member')
async def removewarn(ctx, member: nextcord.Member, ammount='1'):
    if not ctx.author.guild_permissions.manage_messages:
        await ctx.send('This command requires `manage_messages` permission')
        return
    try:
        int(ammount)
    except:
        await ctx.send('Ammount can only be a number.')
        return
    count = 0
    with open('warns.json') as f:
        data = json.load(f)
        for d in data:
            if d['user_id'] == member.id:
                if int(ammount) == 0:
                    del data[count]
                    await ctx.send('<:check_90:881380678938296410> | All warning(s) removed')
                elif d['warns'] <= int(ammount):
                    del data[count]
                    await ctx.send(f'<:check_90:881380678938296410> | {ammount} warning(s) removed')
                elif d['warns'] > int(ammount):
                    d['warns'] = d['warns'] - int(ammount)
                    await ctx.send(f'<:check_90:881380678938296410> | {ammount} warning(s) removed')
                else:
                    await ctx.send('Cant remove warning(s).')
                    return
            count += 1
    with open('warns.json', 'w') as f:
        json.dump(data, f, indent=4)


@client.command(name='clear', description='&Clears an ammount of messages from a channel')
async def clear(ctx, amount=2):
    if not ctx.author.guild_permissions.manage_messages:
        await ctx.send('This command requires `manage_messages` permission')
        return
    await ctx.channel.purge(limit=amount+1)
    msg = await ctx.send(f'<:check_90:881380678938296410> | Cleared {amount} messages')
    await asyncio.sleep(2)
    await msg.delete


@client.command(name='mute', description='&Mute a member')
async def mute(ctx, member: nextcord.Member, mute_time='900', *, reason='No reason provided'):
    if not ctx.author.guild_permissions.manage_messages:
        await ctx.send('This command requires `manage_messages` permission')
        return

    muted_role = nextcord.utils.get(ctx.guild.roles, name="Muted")
    guild = ctx.guild
    if muted_role in member.roles:
        await ctx.send(f'User {member} is already muted.')
        return
    if not muted_role:
        await ctx.send('No muted role was found, creating muted role...')
        muted_role = await guild.create_role(name='Muted')
        for channel in guild.text_channels:
            await channel.set_permissions(muted_role, send_messages=False)

    if mute_time[-1].lower() == 'h':
        mute_time = int(mute_time[:-1]) * 3600
    elif mute_time[-1].lower() == 'm':
        mute_time = int(mute_time[:-1]) * 60
    else:
        try:
            mute_time = int(mute_time)
        except:
            await ctx.send('Invalid time format')
            return

    await member.add_roles(muted_role)
    await member.send(f'You have been muted in {ctx.guild.name} for {mute_time}s | Reason, *{reason}*')
    em = nextcord.Embed(
        title=f'<:check_90:880570776879775835>  {member} has been muted by {ctx.author} for {mute_time}s.', color=nextcord.Color.blue())
    await ctx.send(embed=em)
    await asyncio.sleep(mute_time)
    for role in member.roles:
        if role.id == muted_role.id:
            await member.remove_roles(muted_role)
            em = nextcord.Embed(
                title=f'<:check_90:880570776879775835>  {member} has been unmuted.', color=nextcord.Color.blue())
            await ctx.send(embed=em)


@client.command(name='unmute', description='&Unmute a member')
async def unmute(ctx, member: nextcord.Member):
    if not ctx.author.guild_permissions.manage_messages:
        await ctx.send('This command requires `manage_messages` permission')
        return
    muted_role = nextcord.utils.get(ctx.guild.roles, name="Muted")
    for role in member.roles:
        if role.id == muted_role.id:
            await member.remove_roles(muted_role)
            em = nextcord.Embed(
                title=f'<:check_90:880570776879775835> | {member} has been unmuted.', color=nextcord.Color.blue())
            await ctx.send(embed=em)
            return
    await ctx.send(f'User `{member}` is already unmuted.')


@client.command(name='lock', description='&Lock a channel')
async def lock(ctx, channel: nextcord.TextChannel = None):
    if not ctx.author.guild_permissions.manage_channels:
        await ctx.send('This command requires `manage_channels` permission')
        return
    role = ctx.guild.default_role
    channel = channel or ctx.channel
    overwrite = channel.overwrites_for(role)
    if overwrite.send_messages == False:
        await ctx.send(f'{channel.mention} is already locked.')
        return
    overwrite.send_messages = False
    await channel.set_permissions(role, overwrite=overwrite)
    await ctx.send('<:check_90:881380678938296410> | Channel locked.')
    await channel.send(f'Channel locked by {ctx.author.mention} 🔒')


@client.command(name='unlock', description='&Unlock a channel')
async def unlock(ctx, channel: nextcord.TextChannel = None):
    if not ctx.author.guild_permissions.manage_channels:
        await ctx.send('This command requires `manage_channels` permission')
        return
    channel = channel or ctx.channel
    role = ctx.guild.default_role
    overwrite = channel.overwrites_for(role)
    if overwrite.send_messages == None:
        await ctx.send(f'{channel.mention} is already unlocked.')
        return
    overwrite.send_messages = None
    await channel.set_permissions(role, overwrite=overwrite)
    await ctx.send('<:check_90:881380678938296410> | Channel unlocked.')
    await channel.send(f'Channel unlocked by {ctx.author.mention} 🔓')


@client.command(name='lockdown', description='&Lockdown the server')
async def lockdown(ctx, *, reason='No reason provided'):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send('This command requires `administrator` permission')
        return
    role = ctx.guild.default_role
    for channel in ctx.guild.text_channels:
        overwrite = channel.overwrites_for(role)
        overwrite.send_messages = False
        await channel.set_permissions(role, overwrite=overwrite)
    em = nextcord.Embed(
        description=f'You are not muted, the server is currently under lockdown for, *{reason}*.', color=nextcord.Color.red())
    em.set_footer(icon_url=ctx.author.avatar.url,
                  text=f'Issued by {ctx.author.name}')
    await ctx.send(embed=em)


@client.command(name='lockdownend', description='&End the lockdown')
async def lockdownend(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send('This command requires `administrator` permission')
        return
    role = ctx.guild.default_role
    for channel in ctx.guild.text_channels:
        overwrite = channel.overwrites_for(role)
        overwrite.send_messages = None
        await channel.set_permissions(role, overwrite=overwrite)
    em = nextcord.Embed(
        description='Lockdown has ended, thank you for being patient', color=nextcord.Color.blue())
    em.set_footer(icon_url=ctx.author.avatar.url,
                  text=f'Issued by {ctx.author.name}')
    await ctx.send(embed=em)

def get_cmds(symbol, end_index = 1):
    cmds = ''
    for cmd in client.commands:
        try:
            if cmd.description[0:end_index] == symbol:
                cmds += f'`{cmd.name.capitalize()}` | {cmd.description[end_index:]}\n'
        except:
            pass
    return cmds

class HelpButtonMenu(menus.ButtonMenu):
    def __init__(self):
        super().__init__(timeout=60.0)

    async def send_initial_message(self, ctx, channel):
        dev = client.get_user(568604697855000624)
        em = nextcord.Embed(
            description='🍂 **General** - *General commands*\n⚙ **Moderation** - *Moderation commands*\n**🔨 Utility** - *Utility commands*\n**😎 Fun** - *Fun commands*', color=nextcord.Color.blue())
        em.set_author(name='Command Overview')
        em.add_field(name='👑 Invite Me To Your Server',
                     value=f'*{client.user.name} would love to be in your server you can invite him [here](https://discord.com/api/oauth2/authorize?client_id=881336046778986518&permissions=8&scope=bot)*\n*If you need help with me you can join my support [server](https://discord.gg/72udgVqEkf)*', inline=False)
        em.add_field(
            name='❔ Info', value=f'*To access the commands use the button at the bottom*\nDeveloped by **{dev}**', inline=False)
        em.add_field(name='🔗 Useful Links',
                     value='[My Fiverr](https://www.fiverr.com/tyrus_b/program-a-professional-and-custom-discord-bot-for-you) | [Support Server](https://discord.gg/72udgVqEkf) | [Invite Me](https://top.gg/bot/881336046778986518)')
        return await channel.send(embed=em, view=self)

    @nextcord.ui.button(label="🍂 General", style=nextcord.ButtonStyle.primary)
    async def on_gen_click(self, button, interaction):
        helpcmds=get_cmds('$')
        em = nextcord.Embed(title='⚙ Commands',
                            description=helpcmds, color=nextcord.Color.blue())
        em.add_field(name='💼 How To Get Help',
                     value='*If you need help on a command you can type my prefix and then* \n`help <name of command>`', inline=False)
        await self.message.edit(embed=em)

    @nextcord.ui.button(label="⚙ Moderation", style=nextcord.ButtonStyle.primary)
    async def on_mod_click(self, button, interaction):
        modcmds=get_cmds('&')
        em = nextcord.Embed(title='⚙ Mod commands',
                            description=modcmds, color=nextcord.Color.blue())
        em.add_field(name='💼 How To Get Help',
                     value='*If you need help on a command you may type my prefix and then* \n`help <name of command>`')
        await self.message.edit(embed=em)

    @nextcord.ui.button(label="🔨 Utility", style=nextcord.ButtonStyle.primary)
    async def on_util_click(self, button, interaction):
        utilcmds=get_cmds('%')
        em = nextcord.Embed(title='🔨 Utility commands',
                            description=utilcmds, color=nextcord.Color.blue())
        em.add_field(name='💼 How To Get Help',
                     value='*If you need help on a command you may type my prefix and then* \n`help <name of command>`')
        await self.message.edit(embed=em)

    @nextcord.ui.button(label="😎 Fun", style=nextcord.ButtonStyle.primary)
    async def on_fun_click(self, button, interaction):
        funcmds=get_cmds('!')
        em = nextcord.Embed(title='😎 Fun commands',
                            description=funcmds, color=nextcord.Color.blue())
        em.add_field(name='💼 How To Get Help',
                     value='*If you need help on a command you may type my prefix and then* \n`help <name of command>`')
        await self.message.edit(embed=em)

    @nextcord.ui.button(label='🔧 Configuration', style=nextcord.ButtonStyle.primary)
    async def on_config_click(self, button, interaction):
        configcmds=get_cmds('^')
        em = nextcord.Embed(
            title='🔧 Configuration Commands',
            description=configcmds,
            color=nextcord.Color.blue()
        )
        em.add_field(
            name='💼 How To Get Help',
            value='*If you need help on a command you may type my prefix and then* \n`help <name of command>`'
        )
        await self.message.edit(embed=em)

    @nextcord.ui.button(label="🏠 Go Home", style=nextcord.ButtonStyle.danger)
    async def on_home_click(self, button, interaction):
        dev = client.get_user(568604697855000624)
        em = nextcord.Embed(
            description='🍂 **General** - *General commands*\n⚙ **Moderation** - *Moderation commands*\n**🔨 Utility** - *Utility commands*\n**😎 Fun** - *Fun commands*', color=nextcord.Color.blue())
        em.set_author(name='Command Overview')
        em.add_field(name='👑 Invite Me To Your Server',
                     value=f'*{client.user.name} would love to be in your server you can invite him [here](https://discord.com/api/oauth2/authorize?client_id=881336046778986518&permissions=8&scope=bot)*\n*If you need help with me you can join my support [server](https://discord.gg/72udgVqEkf)*', inline=False)
        em.add_field(
            name='❔ Info', value=f'*To access the commands use the button at the bottom*\nDeveloped by **{dev}**', inline=False)
        em.add_field(name='🔗 Useful Links',
                     value='[My Fiverr](https://www.fiverr.com/tyrus_b/program-a-professional-and-custom-discord-bot-for-you) | [Support Server](https://discord.gg/72udgVqEkf) | [Invite Me](https://top.gg/bot/881336046778986518)')
        await self.message.edit(embed=em)


@client.command(name='help', description='$Get help with my commands')
async def help(ctx, command=None):
    if command != None:
        for func in client.commands:
            if command.lower() == func.name.lower():
                params = ''
                if len(func.clean_params) == 0:
                    params = '*No parameters to display*'
                for param in func.clean_params:
                    params += f'*<{param}>* '
                em = nextcord.Embed(
                    title=f'Command: {func.name}', description=f'{params}', color=nextcord.Color.blue())
                await ctx.send(embed=em)
                return
    await HelpButtonMenu().start(ctx)

@client.command(name='devcmds', description='$Dev only commands')
async def devcmds(ctx):
    if ctx.author.id != 568604697855000624:
        await ctx.send('You cannot access this command because you are not the dev!')
        return
    devcmds=get_cmds('--', 2)
    em=nextcord.Embed(description=devcmds, color=nextcord.Color.blue())
    await ctx.send(embed=em)

# ECONOMY ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

async def add_to_bal(id, ammount):
    result = await bank.find_one({'_id': id})
    bal = result['bal']
    if not ammount:
        if bal - ammount <= 0:
            await bank.update_one({'_id': id}, {'$set': {'bal': 0}})
            return
    await bank.update_one({'_id': id}, {'$inc': {'bal': ammount}})
    if ammount > 0:
        await bank.update_one({'_id': id}, {'$addToSet': {'phi': ammount}})

async def transfer_bank(id, ammount):
    await bank.update_one({'_id': id}, {'$inc': {'wallet': -ammount}})
    await bank.update_one({'_id': id}, {'$inc': {'bal': ammount}})

async def transfer_wallet(id, ammount):
    await bank.update_one({'_id': id}, {'$inc': {'wallet': ammount}})
    await bank.update_one({'_id': id}, {'$inc': {'bal': -ammount}})

async def add_to_wallet(id, ammount):
    result = await bank.find_one({'_id': id})
    bal = result['wallet']
    if not ammount:
        if bal - ammount <= 0:
            await bank.update_one({'_id': id}, {'$set': {'wallet': 0}})
            return
    await bank.update_one({'_id': id}, {'$inc': {'wallet': ammount}})
    if ammount > 0:
        await bank.update_one({'_id': id}, {'$addToSet': {'phi': ammount}})

async def add_item(id, d):
    await bank.update_one({"_id": id}, {'$push': {'inv': d}})

@client.command(name='openbank', description='Open a bank')
async def openbank(ctx):
    result = await bank.find_one({'_id': ctx.author.id})
    if result:
        await ctx.reply('`You already have a a bank account open`')
    else:
        await bank.insert_one({
            '_id': ctx.author.id,
            'bal': 1000,
            'wallet': 0,
            'intrest': 5
        })
        await ctx.reply('`Successfully opened a bank account`')

@client.command(name='closebank', description='Close your bank account')
async def closebank(ctx):
    result = await bank.find_one({'_id': ctx.author.id})
    if not result:
        await ctx.reply('`You do not have an account to delete!`')
        return
    msg = await ctx.reply('`WARNING!! Are you sure you would like to close your bank account, all money will be lost forever! (y/n)`')
    try:
        choice = await client.wait_for('message', check=lambda m: m.author.id == ctx.author.id, timeout=10)
    except asyncio.TimeoutError:
        await msg.edit(content='⏳ Timed Out')
        return
    if choice.content.lower() == 'y':
        msg = await ctx.reply('`Are you 100% positive you want to close your bank account? (y/n)`')
        try:
            choice2 = await client.wait_for('message', check=lambda m: m.author.id == ctx.author.id, timeout=10)
        except asyncio.TimeoutError:
            await msg.edit(content='⏳ Timed Out')
            return
        if choice2.content.lower() == 'y':
            try:
                await bank.delete_one({'_id': ctx.author.id})
                await ctx.reply('`Account deleted`')
            except:
                await ctx.reply('`Unable to delete account`')
        else:
            await ctx.reply('`Terminated`')
    else:
        await ctx.reply('`Terminated`')

@client.command(name='bal', description = 'Check yout balance')
async def bal(ctx):
    result = await bank.find_one({'_id': ctx.author.id})
    if result:
        bal = result['bal']
        wallet = result['wallet']
        intrest = result['intrest']
        phi = 0
        aphi = 0
        try:
            try:
                for x in result['phi']:
                    phi += x
                for x in result['aphi']:
                    aphi += x
            except:
                pass
            aphi /= len(result['aphi'])
        except:
            pass
        phi * 2
        em = nextcord.Embed(description=f'*Your account balance is: ${round(bal, 2)}* \n*Your wallet balance is: ${round(wallet, 2)}*\n*Your account intrest rate is: %{intrest}* \n*Your daily inrest rate is: ${round((intrest * bal) / 100, 2)}*\n*Income in the past hour: ${round(phi, 2)}\nAverage hourly income: ${round(aphi, 2)}*', color=nextcord.Color.blue())
        em.set_author(name='Account Details')
        await ctx.reply(embed=em)
    else:
        await ctx.reply('`You do not have a bank account open, please open one first`')

@client.command(name='beg', description='Beg for money')
@commands.cooldown(1, 3, commands.BucketType.user)
async def beg(ctx):
    num = random.randint(0, 100)
    if num >= 50 and num <= 55:
        await ctx.reply(f'`Oh no! Someone stole all the money in your wallet!`')
        await bank.update_one({'_id': ctx.author.id}, {'$set': {'wallet': 0}})
        return
    elif num >= 10 and num <= 15:
        await ctx.reply(f'`Lucky! Someone gave you $1000!`')
        await add_to_wallet(ctx.author.id, 1000)
        return
    await ctx.reply(f'`Someone came by and gave you ${num}!`')
    await add_to_wallet(ctx.author.id, num)

@beg.error
async def _(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.reply('`Woah! Slow down there your still on cooldown!`')

@client.command(name='dep', description='Deposit money into your bank account')
async def dep(ctx, choice=None):
    result = await bank.find_one({'_id': ctx.author.id})
    maxx = result['wallet']

    if str(choice).lower() == 'all':
        await transfer_bank(ctx.author.id, maxx)
        await ctx.reply(f'`Successfully deposited {maxx} into your bank account!`')
        return

    if result['wallet'] <= 0:
        await ctx.reply('`You have no money in your wallet!`')
        return
    msg = await ctx.reply(f'`How much would you like to deposit: Max {round(maxx, 2)}, or type all to deposit all`')
    try:
        ammount = await client.wait_for('message', check = lambda m: m.author.id == ctx.author.id, timeout=20)
    except asyncio.TimeoutError:
        await msg.edit(content='⏳ Timed Out')
        return
    int_ammount = 0
    if ammount.content.lower() == 'all':
        int_ammount = result['wallet']
    else:
        try:
            if int(ammount.content) > maxx:
                await ctx.reply('`You can not deposit money you do not have!`')
                return
            int(ammount.content)
            int_ammount = int(ammount.content)
        except:
            await ctx.reply('`The ammount can only be a number!`')
            return
    await transfer_bank(ctx.author.id, int_ammount)
    await ctx.reply(f'`Successfully deposited {int_ammount} into your bank account!`')

@client.command(name='wd', description='Withdraw money from your bank account into your wallet')
async def wd(ctx, x = None):
    result = await bank.find_one({'_id': ctx.author.id})
    maxx = result['bal']
    if result['bal'] <= 0:
        await ctx.reply('`You have no money in your bank!`')
        return
    if x != None:
        try:
            ammount = float(x)
            if ammount < maxx:
                await transfer_wallet(ctx.author.id, float(x))
                await ctx.reply(f'`Successfully withdrew {x} into your wallet!`')
                return
            else:
                await ctx.reply('`You can not withdraw money you do not have!`')
                return
        except Exception as e:
            await ctx.reply('`The ammount can only be a number!`')
            print(e)
            return
    msg = await ctx.reply(f'`How much would you like to withdraw: Max {round(maxx, 2)}`')
    try:
        ammount = await client.wait_for('message', check = lambda m: m.author.id == ctx.author.id, timeout=20)
    except asyncio.TimeoutError:
        await msg.edit(content='⏳ Timed Out')
        return
    int_ammount = 0
    try:
        if float(ammount.content) > maxx:
            await ctx.reply('`You can not withdraw money you do not have!`')
            return
        int_ammount = float(ammount.content)
    except:
        await ctx.reply('`The ammount can only be a number!`')
        return
    await transfer_wallet(ctx.author.id, int_ammount)
    await ctx.reply(f'`Successfully withdrew {int_ammount} into your wallet!`')


@client.command(name = 'transfer', description='Transfer money')
async def transfer(ctx, user: nextcord.Member = None, ammount = None):
    result = await bank.find_one({'_id': ctx.author.id})
    trans_user = await bank.find_one({'_id': user.id})
    final_ammount = 0.0
    if user == None:
        await ctx.reply('`You must provide the user you would like to transfer money to!`')
        return
    elif ammount == None:
        await ctx.reply('`Please provide an ammount to transfer!`')
        return
    elif type(ammount) == str:
        try:
            x = float(ammount)
            final_ammount = x
        except:
            await ctx.reply('`The ammount being transfered must be a number!`')
            return
    elif ammount > 100000:
        await ctx.reply('`Max transfer ammount is 100,000!`')
        return
    elif ammount > result['bal']:
        await ctx.reply('`You do not have that much money!`')
        return
    elif result == None:
        await ctx.reply('`You need a bank account to complete this transaction!`')
        return
    if trans_user == None:
        await ctx.reply('`The user you are trying to send money to does not have a bank account!`')
        return
    else:
        msg = await ctx.reply(f'`Are you sure you would like to transfer {ammount} to {user.name}. (y/n)`')
        try:
            ans = await client.wait_for('message', check = lambda m: m.author.id == ctx.author.id, timeout=10)
        except asyncio.TimeoutError:
            await msg.edit(content='Timed Out!')
            return
        if ans.content.lower() == 'y':
            await add_to_bal(ctx.author.id, -float(final_ammount))
            await add_to_bal(user.id, final_ammount)
            await ctx.reply('`Transaction complete`')
            await user.send(f'{ctx.author.name} has sent you ${ammount}! It has been added to your balance')
        else:
            await ctx.reply('`Transaction cancelled`')

@transfer.error
async def _(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.reply('`Woah! Slow down there your still on cooldown!`')
    elif isinstance(error, commands.MemberNotFound):
        await ctx.reply('`Invalid user!`')
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply('`You must provide the user and the ammount you would like to transfer\nEx. !transfer @user 69\n`')
    

# Items and Inv

@client.command(name='inv', description='Your inventory')
async def inv(ctx):
    result = await bank.find_one({'_id': ctx.author.id})
    em = nextcord.Embed(color=nextcord.Color.blue())
    em.set_author(name='Inventory')
    em.set_footer(text='You can sell any of these items with the sell command')
    try:
        if not result['inv']:
            em.add_field(name='No items to display', value='You have no items in your inventory!', inline=False)
            await ctx.reply(embed=em)
            return
    except:
        pass
    y = {}
    for x in result['inv']:
        item, ammount = list(x.items())[0]
        if item not in list(y.keys()):
            y[item] = 1
        else:
            y[item] += 1
    for item, ammount in list(y.items()):
        price = 0
        for x in result['inv']:
            key, val = list(x.items())[0]
            if item == key:
                price = val
        em.add_field(name=f'{item} - {ammount}x', value=f'Worth ${price}', inline=False)
    await ctx.reply(embed=em)

@client.command(name='search', description='Search for items and money')
@commands.cooldown(1, 30, commands.BucketType.user)
async def search(ctx):
    items = [{'Wallet': 100}, {'Old Revolver': 150}, {'Grandmas Ashes': 50}, {'Old Guitar': 75}, {'Guitar': 100}, {'Les Paul Guitar': 1000}, {'Block Of Cheese': 10}, {'Moon Rock': 1000}]
    index = random.randint(0, len(items))
    item = items[index]
    await bank.update_one({"_id": ctx.author.id}, {'$push': {'inv': item}})
    await ctx.reply(f'`You found one {list(item.keys())[0]}!`')

@search.error
async def _(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.reply('`Woah! Slow down there your still on cooldown!`')

@client.command(name='sell', description='Sell items')
async def sell(ctx, *items):
    item = ' '.join(items)
    print(item)
    if item == '':
        await ctx.reply('`Please provide the item you would like to sell\nEx. !sell guitar`')
        return
    result = await bank.find_one({'_id': ctx.author.id})
    if not result['inv']:
        await ctx.reply('`You have no items to sell`')
        return
    elif len(result['inv']) == 0:
        await ctx.reply('`You have no items to sell`')
        return
    else:
        inv = {}
        copy = []
        for i in result['inv']:
            inv[list(i.keys())[0].lower()] = list(i.values())[0]
            copy.append(i)
        if item.lower() not in list(inv.keys()):
            await ctx.reply('`You can not sell an item you do not have!`')
            return
        elif item.lower() in inv:
            price = inv[item.lower()]
            for i, val in enumerate(copy):
                if list(val.keys())[0].lower() == item.lower():
                    del copy[i]
            await bank.update_one({"_id": ctx.author.id}, {'$set': {'inv': copy}})
            await add_to_wallet(ctx.author.id, price)
            await ctx.reply(f'`You sold {item.lower()} for ${price}`')

@sell.error
async def _(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply('`Please provide the item you would like to sell\nEx. !sell guitar`')

# Store

store_items = {'hunting rifle': 75000, 'laptop': 50000, 'ruby': 100000}
store_des = {'hunting rifle': 'Can be used to hunt animals', 'laptop': 'Post memes and get paid for it', 'ruby': 'It looks cool I guess'}

@client.command(name='store', description='Buy items')
async def store(ctx):
    des = 'Here are some items you can buy!\n\n'
    for item in list(store_items.items()):
        x, y = item
        des += f'`{x}`, `{store_des[x]}` - ${y}\n'
    em = nextcord.Embed(description = des, color=nextcord.Color.blue())
    em.set_author(name='Store')
    await ctx.reply(embed=em)

@client.command(name='buy', description='Buy items in the store')
async def buy(ctx, *item):
    choice = ' '.join(item).lower()
    result = await bank.find_one({'_id': ctx.author.id})
    if not result:
        await ctx.reply('`You need a bank account to buy stuff!`')
        return
    if not result['inv']:
        pass
    elif choice == '':
        await ctx.reply('`Please provide the item you would like to buy!\nEx. !buy hunting rifle`')
        return
    else:
        inv = {}
        for i in result['inv']:
            inv[list(i.keys())[0].lower()] = list(i.values())[0]
        if choice in list(inv.keys()):
            await ctx.reply('`You already own that item!`')
            return
    if choice not in list(store_items.keys()):
        await ctx.reply('`That item is not in the store! To buy an item type the items name seen in the store.`')
        return
    wallet = result['wallet']
    if choice in list(store_items.keys()):
        if wallet >= store_items[choice]:
            await add_to_wallet(ctx.author.id, -store_items[choice])
            await add_item(ctx.author.id, {choice: store_items[choice]})
            await ctx.reply(f'`You bought one {choice}!`')
        else:
            await ctx.reply('`You do not have enough money in your wallet to buy that!`')
            return

# Job

jobs_dict = {'janitor': 10000, 'office worker': 50000, 'car dealsman': 100000}
jobs_pay = {'janitor': 1000, 'office worker': 3000, 'car dealsman': 5000}

@client.command(name='jobs', description='Get a job for yourself!')
async def jobs(ctx):
    des = f'More jobs will become available with a higher bank balance\n\n'
    result = await bank.find_one({'_id': ctx.author.id})
    bal = float(result['bal'])
    for key, val in jobs_dict.items():
        if bal >= val:
            des += f'**{key.title()}** is available, {val} bank balance required\n'
        else:
            des += f'**{key.title()}** is not available, {val} bank balance required\n'
    em = nextcord.Embed(description=des, color=nextcord.Color.blue())
    em.set_author(name='Available Jobs (Respecting your bank balance)')
    em.set_footer(text='To apply for a job use the apply command')
    await ctx.reply(embed=em)

@client.command(name='apply', description='Apply for a job')
async def apply(ctx):
    result = await bank.find_one({'_id': ctx.author.id})
    jobs = list(jobs_dict.keys())
    des = ', '.join(jobs)
    msg = await ctx.reply(f'`Please type the job you would like to apply for.\nAvailable positions - {des}`')
    try:
        app = await client.wait_for('message', check=lambda m: m.author.id == ctx.author.id, timeout=20)
    except asyncio.TimeoutError:
        await msg.edit(content='⏳ Timed Out!')
        return
    if app.content.lower() not in jobs:
        await ctx.reply('`I do not recognise that as a job, please try again`')
        return
    elif app.content.lower() in jobs:
        bal = result['bal']
        try:
            if result['job']:
                await ctx.reply('`You have to quit your job to apply for a new one!`')
                return
        except:
            pass
        if bal >= jobs_dict[app.content.lower()]:
            await bank.update_one({'_id': ctx.author.id}, {'$set': {'job': app.content.lower()}})
            await add_to_bal(ctx.author.id, -jobs_dict[app.content.lower()])
            await ctx.reply(f'`Enjoy your job as a {app.content.title()}! Use the work command to start working!`')
        else:
            await ctx.reply('`Your bank balance is not high enough for this position!`')
            return
    else:
        await ctx.reply('`Sorry! Something went wrong!`')

@client.command(name='quit', description='Quit your job')
async def quit(ctx):
    result = await bank.find_one({'_id': ctx.author.id})
    try:
        if not result['job']:
            await ctx.reply('`You can not quit a job you do not have!`')
            return
    except:
        pass
    await bank.update_one({'_id': ctx.author.id}, {'$unset': {'job': ''}})
    await ctx.reply('`You quit your job!`')

@client.command(name='work', description='Work for money!')
@commands.cooldown(1, 60, commands.BucketType.user)
async def work(ctx):
    result = await bank.find_one({'_id': ctx.author.id})
    try:
        if not result['job']:
            await ctx.reply('`You need a job to use this command! Use the jobs command to get started!`')
            return
    except:
        pass
    job = result['job']
    pay = jobs_pay[job]
    num1 = random.randrange(2, 11, 2)
    num2 = random.randint(1, 11)
    answer = num1 * num2
    msg = await ctx.reply(f'`What is {num1} x {num2}?`')
    try:
        ans = await client.wait_for('message', check=lambda m: m.author.id == ctx.author.id, timeout=5)
    except asyncio.TimeoutError:
        await msg.edit(content='⏳ Time!')
        await add_to_bal(ctx.author.id, pay)
    try:
        int(ans.content)
    except:
        await add_to_bal(ctx.author.id, pay)
        await ctx.reply(f'`Incorrect! You have been payed ${pay}!`')
        return
    if int(ans.content) == answer:
        await add_to_bal(ctx.author.id, pay + (pay * 50 / 100))
        await ctx.reply(f'`Correct! You have been payed ${pay + (pay * 50 / 100)}!`')
    else:
        await add_to_bal(ctx.author.id, pay)
        await ctx.reply(f'`Incorrect! You have been payed ${pay}!`')

@work.error
async def _(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.reply('`Woah! Slow down there your still on cooldown!`')

# Item specific commands

@client.command(name='hunt', description='Hunt animals!')
async def hunt(ctx):
    result = await bank.find_one({'_id': ctx.author.id})
    stuff = [{'deer': 500}, {'rabbit': 250}, {'rabbit foot': 1000}, {'turtle': 150}, {'dirt': 5}, {'fat kangaroo': 1500}]
    if not result['inv']:
        await ctx.reply('`You must have a hunting rifle in your inventory to use this command!`')
        return
    elif result['inv']:
        inv = []
        for i in result['inv']:
            inv.append(list(i.keys())[0])
        if 'hunting rifle' in inv:
            index = random.randint(0, len(stuff))
            animal = stuff[index]
            await add_item(ctx.author.id, animal)
            await ctx.reply(f'`You caught {list(animal.keys())[0]}!`')
        else:
            await ctx.reply('`You must have a hunting rifle in your inventory to use this command!`')
            return

class pmButtonMenu(menus.ButtonMenu):
    def __init__(self):
        super().__init__(timeout=60.0)

    async def send_initial_message(self, ctx, channel):
        em=nextcord.Embed(description=f'`Post a meme to earn or lose money', color=nextcord.Color.blue())
        em.set_author(name='Post Meme')
        return await channel.send(embed=em, view=self)

    @nextcord.ui.button(label='Original', style=nextcord.ButtonStyle.primary)
    async def og_click(self, button, interaction):
        num = random.randint(-300, 2001)
        x = 'earned' if num>=0 else 'lost'
        y = 'LOVED' if num>=0 else 'HATED'
        des = f'`People {y} your meme!\nYou {x} ${num}!`'
        em = nextcord.Embed(description=des, color=nextcord.Color.blue())
        em.set_author(name='You posted a meme')
        await add_to_wallet(self.ctx.author.id, num)
        await self.message.edit(embed=em)

    @nextcord.ui.button(label='Copy and Paste', style=nextcord.ButtonStyle.primary)
    async def cp_click(self, button, interaction):
        num = random.randint(-1000, 3001)
        x = 'earned' if num>=0 else 'lost'
        y = 'LOVED' if num>=0 else 'HATED'
        des = f'`People {y} your meme!\nYou {x} ${num}!`'
        em = nextcord.Embed(description=des, color=nextcord.Color.blue())
        em.set_author(name='You posted a meme')
        await add_to_wallet(self.ctx.author.id, num)
        await self.message.edit(embed=em)

    @nextcord.ui.button(label='Smart', style=nextcord.ButtonStyle.primary)
    async def smart_click(self, button, interaction):
        num = random.randint(-200, 1001)
        x = 'earned' if num>=0 else 'lost'
        y = 'LOVED' if num>=0 else 'HATED'
        des = f'`People {y} your meme!\nYou {x} ${num}!`'
        em = nextcord.Embed(description=des, color=nextcord.Color.blue())
        em.set_author(name='You posted a meme')
        await add_to_wallet(self.ctx.author.id, num)
        await self.message.edit(embed=em)

    @nextcord.ui.button(label='Kind', style=nextcord.ButtonStyle.primary)
    async def kind_click(self, button, interaction):
        num = random.randint(-500, 2001)
        x = 'earned' if num>=0 else 'lost'
        y = 'LOVED' if num>=0 else 'HATED'
        des = f'`People {y} your meme!\nYou {x} ${num}!`'
        em = nextcord.Embed(description=des, color=nextcord.Color.blue())
        em.set_author(name='You posted a meme')
        await add_to_wallet(self.ctx.author.id, num)
        await self.message.edit(embed=em)

@client.command(name='pm', description='Post memes!')
@commands.cooldown(1, 45, commands.BucketType.user)
async def pm(ctx):
    result = await bank.find_one({'_id': ctx.author.id})
    if not result['inv']:
        await ctx.reply('`You must have a laptop in your inventory to use this command!`')
        return
    elif result['inv']:
        inv = []
        for i in result['inv']:
            inv.append(list(i.keys())[0])
        if 'laptop' in inv:
            await pmButtonMenu().start(ctx)
        else:
            await ctx.reply('`You must have a laptop in your inventory to use this command!`')
            return

@pm.error
async def _(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.reply('`Woah! Slow down there your still on cooldown!`')

@tasks.loop(minutes=5)
async def add_intrest():
    result = bank.find({})
    for acc in await result.to_list(length = 1000):
        intrest = acc['intrest']
        bal = acc['bal']
        intrest_full = intrest * bal / 100
        print(round(intrest_full, 2))
        await bank.update_one({'_id': acc['_id']}, {'$inc': {'bal': intrest_full}})

@tasks.loop(hours=1)
async def phi_reset():
    result = bank.find({})
    for acc in await result.to_list(length = 1000):
        phi = 0
        try:
            for x in acc['phi']:
                phi += x
        except:
            await bank.update_one({'_id': acc['_id']}, {'$set': {'phi': [0]}})
        if phi == 0:
            continue
        phi * 2
        await bank.update_one({'_id': acc['_id']}, {'$addToSet': {'aphi': phi}})
        await bank.update_one({'_id': acc['_id']}, {'$set': {'phi': [0]}})
    result = bank.find({})
    for acc in await result.to_list(length=1000):
        aphi = 0
        for x in acc['aphi']:
            aphi += x
        aphi /= len(acc['aphi'])
        if aphi == 0:
            continue
        elif aphi > 9000:
            await bank.update_one({'_id': acc['_id']}, {'$set': {'intrest': 20}})
        elif aphi > 7000:
            await bank.update_one({'_id': acc['_id']}, {'$set': {'intrest': 15}})
        elif aphi > 5000:
            await bank.update_one({'_id': acc['_id']}, {'$set': {'intrest': 10}})

# NON-ECO TASK LOOPS -------------------------------------------------------------------------------------------------------------------------------------------------------------------

@tasks.loop(seconds=120)
async def warn_reset():
    count = 0
    dump = False
    with open('warns.json') as f:
        data = json.load(f)

        for d in data:
            id = d['user_id']
            warn_date = datetime.datetime.now()
            end_date = d['warn_date_remove']

            if end_date <= str(warn_date):
                del data[count]
                dump = True
            count += 1
    if dump:
        with open('warns.json', 'w') as f:
            json.dump(data, f, indent=4)


@tasks.loop(seconds=15)
async def giveaway_check():
    now = datetime.datetime.now()
    entrants = 0
    result = collection.find({'giv': '1'})
    for doc in await result.to_list(length = 1000):
        end_time = doc['end_time']
        channel = client.get_channel(doc['channel_id'])
        msg = await channel.fetch_message(doc['_id'])
        prize = doc['prize']
        host = client.get_user(int(doc['host']))
        if end_time <= str(now):
            if len(doc['giv_list']) == 0:
                winner = '`Not enough entrants`'
            else:
                chosen_id = random.choice(doc['giv_list'])
                chosen_member = client.get_user(chosen_id)
                winner = chosen_member.mention
                for x in doc['giv_list']:
                    entrants += 1
            em = nextcord.Embed(description=f'{entrants} entrants  ✅')
            if not entrants == 0:
                await channel.send(f'Congratulations {winner} you won the **{prize}**', embed=em)
            else:
                await channel.send(f'{winner}, giveaway closed.', embed=em)
            em = nextcord.Embed(
              title=f'{prize}', description=f'\nWinner : {winner} \nHost : {host.mention}', color=nextcord.Color.blue())
            em.timestamp = datetime.datetime.utcnow()
            await msg.edit(content='🎉 **GIVEAWAY ENDED** 🎉', embed=em)
            count = 0
            await collection.delete_one({'_id': doc['_id']})

@tasks.loop(seconds=900)
async def status_update():
    guilds = 0
    for guild in client.guilds:
        guilds += 1
    all_users = 0
    for user in client.get_all_members():
        all_users += 1
    await client.change_presence(status=nextcord.Status.idle, activity=nextcord.Activity(type=nextcord.ActivityType.watching, name=f'{all_users} users in {guilds} servers!'))


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MemberNotFound):
        embed = nextcord.Embed(
            description="That user was not found", color=nextcord.Color.red())
        await ctx.send(embed=embed)
    else:
        raise error


client.run('ODgxMzM2MDQ2Nzc4OTg2NTE4.YSrWJw.0UVqrnJM_1tJpj307GBXiU4vXUM')