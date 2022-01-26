import asyncio
from os import name
import nextcord
from nextcord.ext import commands
import datetime
import json
import random
import motor
from motor import motor_asyncio

try:
    cluster = motor_asyncio.AsyncIOMotorClient(
        "mongodb+srv://tyrus:Tyrus113@cluster0.qifea.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")  # here will be the link for your cluster
    db = cluster["cloud_bot"]  # write your db name here
    # write the name of the collection present in the db where data will be stored
    collection = db["data"]
    print('Database Connected Successfully - util.py')
except:
    print('Database Connection Failed - util.py')


class Util(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def cancel_giv(self, ctx, msg_id = 0):
        if msg_id == 0:
            await ctx.send('<:xmark:884407516363108412> Please include the giveaways id as an argument')
            return
        with open('giveaway_data.json') as f:
            data = json.load(f)
            counter = 0
            for d in data:
                if d['msg_id'] == int(msg_id):
                    if d['host'] == ctx.author.id:
                        channel = self.client.get_channel(d['channel_id'])
                        msg = await channel.fetch_message(msg_id)
                        prize = d['prize']

                        em = nextcord.Embed(
                            title='❌ Giveaway Terminated', description=f'Giveaway terminated by {ctx.author.mention}', color=nextcord.Color.red()
                        )
                        await msg.edit(embed=em)
                        del data[counter]
                        await ctx.send(f'<:check_90:880570776879775835> Success! The giveaway for {prize} has been terminated')
                        break
                    else:
                        await ctx.send(f'<:xmark:884407516363108412> Only the host can terminate this giveaway')
                counter += 1
            else:
                await ctx.send('<:xmark:884407516363108412> Unable to locate giveaway, make sure the message id is correct')
        with open('giveaway_data.json', 'w') as f:
            json.dump(data, f)

    @commands.command()
    async def reminder(self, ctx, time, *, reminder='No Reminder Set'):
        x = ''
        f = ''
        if time[-1].lower() == 'd':
            timer = int(time[:-1]) * 86400
            x = 'days'
            f = str(time[:-1])
        elif time[-1].lower() == 'h':
            timer = int(time[:-1]) * 3600
            x = 'hours'
            f = str(time[:-1])
        elif time[-1].lower() == 'm':
            timer = int(time[:-1]) * 60
            x = 'minutes'
            f = str(time[:-1])
        else:
            try:
                timer = int(time)
                x = 'seconds'
                f = str(time)
            except:
                await ctx.send('`Invalid time format`')
                return

        em = nextcord.Embed(
            title='Reminder Set',
            description=f'Your reminder for {reminder} will conclude in {f} {x}',
            color=nextcord.Color.blue()
        )

        await ctx.send(embed=em)
        await asyncio.sleep(timer)

        doneEm = nextcord.Embed(
            title='Reminder Finished',
            description=f'Your reminder for {reminder} has finished!',
            color=nextcord.Color.red()
        )
        doneEm.set_footer(text=f'You set this reminder {f} {x} ago')

        await ctx.author.send(embed=doneEm)

    @commands.command()
    async def serverinfo(self, ctx):
        result = await collection.find_one({'_id': ctx.guild.id})
        prefix = result['prefix']
        if result['welc'] == 1:
            welc_status = 'Welcomes On!'
        else:
            welc_status = 'Welcomes Off!'
        name = ctx.guild.name
        owner = ctx.guild.owner
        id = ctx.guild.id
        region = ctx.guild.region
        members = ctx.guild.member_count
        textcha = 0
        voicecha = 0
        icon = ctx.guild.icon.url
        creation_date = ctx.guild.created_at

        for channel in ctx.guild.text_channels:
            textcha = textcha + 1
        for channel in ctx.guild.voice_channels:
            voicecha = voicecha + 1

        em = nextcord.Embed(color=nextcord.Color.blue())
        em.add_field(name='*Owner*', value=owner, inline=False)
        em.add_field(name='*Creation Date*',
                     value=creation_date.strftime("%m/%d/%Y"), inline=False)
        em.add_field(name='*Region*', value=region, inline=False)
        em.add_field(name='*Member Count*', value=members, inline=False)
        em.add_field(name='*Text Channels*', value=str(textcha), inline=False)
        em.add_field(name='*Voice Channels*',
                     value=str(voicecha), inline=False)
        em.add_field(name='*Welc status*',
                     value=f'{welc_status}', inline=False)
        em.add_field(name='Bot prefix', value=prefix, inline=False)
        em.set_thumbnail(url=icon)
        em.set_footer(text='ID: ' + str(id))
        em.set_author(name=name)
        em.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=em)

    @commands.command()
    async def setafk(self, ctx):
        member = ctx.author
        member_name = member.display_name
        try:
            await member.edit(nick='[AFK] ' + str(member_name))
            await ctx.send('You are now AFK!')
        except:
            await ctx.send('Unable to set afk status')

    @commands.command()
    async def warns(self, ctx, member: nextcord.Member = None):
        member = member or ctx.author
        with open('warns.json') as f:
            data = json.load(f)
            for d in data:
                if d['user_id'] == member.id:
                    warns = d['warns']
                    date = d['warn_date_remove'][:11]
                    em = nextcord.Embed(
                        description=f'*Warnings expire -* `{date}`')
                    em.set_author(
                        name=f'{member} currently has {warns} warnings', icon_url=member.avatar.url)
                    em.set_footer(icon_url=ctx.author.avatar.url,
                                  text=f'Requested by - {ctx.author}')
                    em.timestamp = datetime.datetime.utcnow()
                    await ctx.send(embed=em)
                    return
            else:
                await ctx.send(f'`{member} does not have any warnings`')

    @commands.command()
    async def whois(self, ctx, member: nextcord.Member):
        roles = []
        creation_date = member.created_at
        join_date = member.joined_at

        for role in member.roles[1:]:
            roles.append(role.mention)
        embed = nextcord.Embed(description=member.mention,
                               color=nextcord.Color.blue())
        embed.set_author(name=member.name, icon_url=member.avatar.url)
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(icon_url=ctx.author.avatar.url,
                         text=f'ID: ' + str(member.id))
        embed.add_field(name='🔓 ID', value=f'`{member.id}`', inline=False)
        embed.add_field(name='❌ Discriminator',
                        value=f'`{member.discriminator}`', inline=False)
        embed.add_field(name='⚡ Highest Role',
                        value=f'{roles[-1]}', inline=False)
        embed.add_field(name='🕔 Joined At', value=join_date.strftime(
            "%m/%d/%Y"), inline=False)
        embed.add_field(name='🕔 Account Created At',
                        value=creation_date.strftime("%m/%d/%Y"), inline=False)
        embed.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Util(client))
