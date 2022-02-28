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

    user = message.author
    guild = message.guild
    counter = 0
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