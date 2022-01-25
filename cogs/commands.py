import asyncio
from os import name
import asyncpraw
import nextcord
from nextcord.ext import commands
import datetime
import json
import random
import motor
from motor import motor_asyncio
from nextcord.ext.commands import context

from nextcord.ext.commands.core import check

try:
    cluster = motor_asyncio.AsyncIOMotorClient(
        "mongodb+srv://tyrus:Tyrus113@cluster0.qifea.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")  # here will be the link for your cluster
    db = cluster["cloud_bot"]  # write your db name here
    # write the name of the collection present in the db where data will be stored
    collection = db["data"]
    print('Database Connected Successfully - commands.py')
except:
    print('Database Connection Failed - commands.py')

reddit = asyncpraw.Reddit(client_id='Oa9pF-GySCz4WRIjOKwUrA',
                          client_secret='pMRYW3aIK6W8yiochB7KeoSCtkC2wQ',
                          username='VLIXC',
                          password='Tyrus113',
                          user_agent='reddit_praw')


class Commands(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def ping(self, ctx):
        em = nextcord.Embed(title='Pong 🏓', description='⌛**Time** ' +
                            f'{round(self.client.latency * 1000)}ms', color=nextcord.Color.blue())
        em.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=em)

    @commands.command()
    async def fiverr(self, ctx):
        em = nextcord.Embed(title='Dev Fiverr Link',
                            description=f"With this link you can order a custom discord bot from {self.client.user.name}'s dev on fiverr, [Fiverr Link](https://www.fiverr.com/tyrus_b/program-a-professional-and-custom-discord-bot-for-you) \n[Fiverr Link 2](https://www.fiverr.com/share/3V5Y19)", color=nextcord.Color.green())
        em.set_thumbnail(
            url='https://cdn-images-1.medium.com/max/1200/1*FfEOiku2EkgoQy_bf8UL6A.png')
        em.set_footer(icon_url=ctx.author.avatar.url,
                      text=f'Requested by {ctx.author.name}')
        await ctx.send(embed=em)

    @commands.command()
    async def info(self, ctx):
        dev = self.client.get_user(568604697855000624)
        guilds = 0
        for guild in self.client.guilds:
            guilds += 1
        all_users = 0
        for user in self.client.get_all_members():
            all_users += 1
        result = await collection.find_one({'_id': ctx.guild.id})
        prefix = result['prefix']
        with open('C:\\Users\\Tyrus\\OneDrive\\Desktop\\peepo bot\\bot_data.json') as f:
            data = json.load(f)
            bot_version = data['bot_version']
        em = nextcord.Embed(
            description=f'**Guild prefix :** `{prefix}`', color=nextcord.Color.blue())
        em.set_author(name='Bot Info')
        em.add_field(name='Developer', value=f'{dev.mention}', inline=False)
        em.add_field(name='Guilds', value=f'`{guilds} guilds`')
        em.add_field(name='Users', value=f'`{all_users} Current users`')
        em.add_field(
            name='🏓 Ping', value=f'`{round(self.client.latency * 1000)}ms`', inline=False)
        em.add_field(name='OS', value='`Windows 10`')
        em.add_field(name='Bot Version', value=f'`{bot_version}`')
        em.add_field(name='🔗 Useful Links',
                     value='[My Fiverr](https://www.fiverr.com/tyrus_b/program-a-professional-and-custom-discord-bot-for-you) | [Support Server](https://discord.gg/72udgVqEkf) | [Invite Me](https://top.gg/bot/881336046778986518)', inline=False)
        em.set_footer(icon_url=ctx.author.avatar.url,
                      text=f'Requested by {ctx.author.name}')
        em.set_thumbnail(url=self.client.user.avatar.url)
        await ctx.send(embed=em)

    @commands.command()
    async def feedback(self, ctx):
        log = self.client.get_channel(885342944821919795)
        try:
            em = nextcord.Embed(title=f'Welcome to the feedback section of {self.client.user.name}',
                                description='Here you can submit feedback such as what you like about me, what you dont like about me, what you think can be improved, suggest new features to be added to me etc. Please enter your response now, you have 5 minutes', color=nextcord.Color.blue())
            await ctx.author.send(embed=em)
            await ctx.send('`I have sent you a DM.`')
        except:
            await ctx.send('`Please enable DMs and try again.`')
            return
        try:
            msg = await self.client.wait_for('message', timeout=60*5)
        except asyncio.TimeoutError:
            await ctx.author.send('`Timed Out ⌛`')
        if len(str(msg.content)) < 15:
            await ctx.author.send('Please provide a longer explanation, Min char lenghth [15]')
            return
        em = nextcord.Embed(
            description=f'Feedback submitted by {ctx.author.mention}', color=nextcord.Color.red())
        em.set_author(icon_url=ctx.author.avatar.url,
                      name='Suggestion Submitted')
        em.add_field(name='Feedback Description',
                     value=f'*{str(msg.content)}*')
        em.set_thumbnail(url=self.client.user.avatar.url)
        em.timestamp = datetime.datetime.utcnow()
        await log.send(embed=em)
        await ctx.author.send('`Your suggestion has been submitted 👍`')

    @commands.command()
    async def update_version(self, ctx, version):
        if ctx.author.id == 568604697855000624:
            with open('C:\\Users\\Tyrus\\OneDrive\\Desktop\\peepo bot\\bot_data.json') as f:
                data = json.load(f)
                prev_version = data['bot_version']
                data['bot_version'] = version
            await ctx.send(f'`Are you sure you want to change my version to {version}`')
            msg = await self.client.wait_for('message', timeout=10)
            if str(msg.content) == 'y':
                with open('C:\\Users\\Tyrus\\OneDrive\\Desktop\\peepo bot\\bot_data.json', 'w') as f:
                    json.dump(data, f)
                await ctx.send(f'`Bot version changed to : {version} | Previous version : {prev_version}`')
            else:
                await ctx.send('`Update aborted`')

    @commands.command()
    async def support(self, ctx):
        em = nextcord.Embed(
            description='Heres my support server! \nhttps://discord.gg/72udgVqEkf', color=nextcord.Color.blue())
        await ctx.author.send(embed=em)

    @commands.command()
    async def invite(self, ctx):
        user = ctx.author
        em = nextcord.Embed(
            description='https://top.gg/bot/881336046778986518', color=nextcord.Color.blue())
        await user.send(embed=em)

    @commands.command()
    async def send_update(self, ctx):
        if not ctx.author.id == 568604697855000624:
            await ctx.send(f'<:xmark:884407516363108412> Sorry, but this is a developer only command')
            return

        version_ask = await ctx.author.send('Please choose a version to update to (type nill to terminate)')
        try:
            version = await self.client.wait_for(
                'message',
                check=lambda m: m.author.id == 568604697855000624,
                timeout=10
            )
        except asyncio.TimeoutError:
            await version_ask.edit(content='⏳ Timed Out')
            return
        if str(version.content).lower() == 'nill':
            await ctx.author.send('Update terminated')
            return

        major_ask = await ctx.author.send('Please choose major changes (type nill to terminate)')
        try:
            major = await self.client.wait_for(
                'message',
                check=lambda m: m.author.id == 568604697855000624,
                timeout=60*5
            )
        except asyncio.TimeoutError:
            await major_ask.edit(content='⏳ Timed Out')
            return
        if str(major.content).lower() == 'nill':
            await ctx.author.send('Update terminated')
            return

        with open('bot_data.json') as f:
            data = json.load(f)
            correctPin = data['pin']
        minor_ask = await ctx.author.send('Please choose minor changes (type nill to terminate)')
        try:
            minor = await self.client.wait_for(
                'message',
                check=lambda m: m.author.id == 568604697855000624,
                timeout=60*5
            )
        except asyncio.TimeoutError:
            await minor_ask.edit(content='⏳ Timed Out')
            return
        if str(minor.content).lower() == 'nill':
            await ctx.author.send('Update terminated')
            return

        pin_ask = await ctx.author.send('Please authorize this update (Enter pin)')
        try:
            pin = await self.client.wait_for(
                'message',
                check=lambda m: m.author.id == 568604697855000624,
                timeout=20
            )
        except asyncio.TimeoutError:
            await pin_ask.edit('⏳ Timed Out')
            return
        if str(pin.content) == correctPin:
            await ctx.author.send('Update authorized')
        else:
            await ctx.author.send('Incorrect Pin, Update terminated')
            return

        for guild in self.client.guilds:
            channel = nextcord.utils.get(
                guild.text_channels, name='cloud-announcments')
            if channel:
                em = nextcord.Embed(
                    title=f'Version {str(version.content)} Patch Notes',
                    description=f'**Major Changes** - *{str(major.content)}*\n**Minor Changes** - *{str(minor.content)}*\n\nInvite Me! - <https://top.gg/bot/881336046778986518>\nSupport Server - <https://discord.gg/72udgVqEkf>\nOrder a Bot - <https://www.fiverr.com/share/BdeeAG>',
                    color=nextcord.Color.blue()
                )
                await channel.send(embed=em)
            else:
                continue

        with open('bot_data.json') as f:
            data = json.load(f)
            prev_version = data['bot_version']
            data['bot_version'] = str(version.content)
            current = data['bot_version']
        with open('bot_data.json', 'w') as f:
            json.dump(data, f)
        await ctx.author.send(f'Version Updated | Prev [{prev_version}] | Current [{current}]')

    @commands.command()
    async def send_announcment(self, ctx):
        if not ctx.author.id == 568604697855000624:
            await ctx.send(f'<:xmark:884407516363108412> Sorry, but this is a developer only command')
            return

        with open('bot_data.json') as f:
            data = json.load(f)
            correctPin = data['pin']

        announce_ask = await ctx.author.send('What annoucment would you like to make (type nill to terminate)')
        try:
            announcment = await self.client.wait_for(
                'message',
                check=lambda m: m.author.id == 568604697855000624,
                timeout=60*10
            )
        except asyncio.TimeoutError:
            await announce_ask.edit(content='⏳ Timed Out')
            return
        if str(announcment.content).lower() == 'nill':
            await ctx.author.send('Announcment terminated')
            return

        pin_ask = await ctx.author.send('Please authorize this announcment (Enter pin)')
        try:
            pin = await self.client.wait_for(
                'message',
                check=lambda m: m.author.id == 568604697855000624,
                timeout=20
            )
        except asyncio.TimeoutError:
            await pin_ask.edit('⏳ Timed Out')
            return
        if str(pin.content) == correctPin:
            await ctx.author.send('Update authorized')
        else:
            await ctx.author.send('Incorrect Pin, Update terminated')
            return

        count = 0
        for guild in self.client.guilds:
            channel = nextcord.utils.get(
                guild.text_channels, name='cloud-announcments')
            if channel:
                count += 1
                em = nextcord.Embed(
                    title=f'Announcment',
                    description=f'{str(announcment.content)}\n\nInvite Me! - <https://top.gg/bot/881336046778986518>\nSupport Server - <https://discord.gg/72udgVqEkf>\nOrder a Bot - <https://www.fiverr.com/share/BdeeAG>',
                    color=nextcord.Color.blue()
                )
                await channel.send(embed=em)
            else:
                continue

        await ctx.auhtor.send(f'Announcment Sent to {count} servers!')


def setup(client):
    client.add_cog(Commands(client))
