import asyncio
from os import name
import asyncpraw
import nextcord
from nextcord.ext import commands
import datetime
import json
import random
from dadjokes import Dadjoke


from nextcord.ext.commands.converter import VoiceChannelConverter

reddit = asyncpraw.Reddit(client_id='Oa9pF-GySCz4WRIjOKwUrA',
                    client_secret='pMRYW3aIK6W8yiochB7KeoSCtkC2wQ',
                    username='VLIXC',
                    password='Tyrus113',
                    user_agent='reddit_praw')

class Fun(commands.Cog):

    def __init__(self, client):
        self.client = client
    

    @commands.command()
    async def meme(self, ctx):
        msg = await ctx.send('<a:loading:885842920652034089> Loading your meme...')
        subreddit = await reddit.subreddit('memes')
        subs = subreddit.top(limit = 500)
        memes = []
        async for x in subs:
            memes.append(x)
        meme = random.choice(memes)
        name = meme.title
        meme_url = meme.url
        em=nextcord.Embed(title = f'**{name}**', color=nextcord.Color.blue())
        em.set_image(url=meme_url)
        em.set_footer(icon_url=ctx.author.avatar.url, text=f'Requested by {ctx.author.name}')
        em.timestamp = datetime.datetime.utcnow()
        await msg.edit(content = '', embed = em)

    @commands.command()
    async def dadjoke(self, ctx):
        dadjoke = Dadjoke()
        await ctx.send(dadjoke.joke)

    @commands.command()
    async def cat(self, ctx):
        msg = await ctx.send('<a:loading:885842920652034089> Looking for a kitty...')
        subreddit = await reddit.subreddit('cats')
        subs = subreddit.top(limit = 500)
        imgs = []
        async for x in subs:
            imgs.append(x)
        img = random.choice(imgs)
        img_url = img.url
        em=nextcord.Embed(title = f'Meoww!', color=nextcord.Color.blue())
        em.set_image(url=img_url)
        em.set_footer(icon_url=ctx.author.avatar.url, text=f'Requested by {ctx.author.name}')
        em.timestamp = datetime.datetime.utcnow()
        await msg.edit(content = '', embed = em)

    @commands.command()
    async def cute(self, ctx):
        msg = await ctx.send('<a:loading:885842920652034089> Looking for a cute image...')
        subreddit = await reddit.subreddit('aww')
        subs = subreddit.top(limit = 500)
        imgs = []
        async for x in subs:
            imgs.append(x)
        img = random.choice(imgs)
        name = img.title
        img_url = img.url
        em=nextcord.Embed(title = f'**{name}**', color=nextcord.Color.blue())
        em.set_image(url=img_url)
        em.set_footer(icon_url=ctx.author.avatar.url, text=f'Requested by {ctx.author.name}')
        em.timestamp = datetime.datetime.utcnow()
        await msg.edit(content = '', embed = em)

    @commands.command()
    async def doggy(self, ctx):
        msg = await ctx.send('<a:loading:885842920652034089> Looking for a puppy...')
        subreddit = await reddit.subreddit('DOG')
        subs = subreddit.top(limit = 500)
        imgs = []
        async for x in subs:
            imgs.append(x)
        img = random.choice(imgs)
        name = img.title
        img_url = img.url
        em=nextcord.Embed(title = f'Woof!', color=nextcord.Color.blue())
        em.set_image(url=img_url)
        em.set_footer(icon_url=ctx.author.avatar.url, text=f'Requested by {ctx.author.name}')
        em.timestamp = datetime.datetime.utcnow()
        await msg.edit(content = '', embed = em)

    @commands.command()
    async def pug(self, ctx):
        msg = await ctx.send('<a:loading:885842920652034089> Looking for a pug...')
        subreddit = await reddit.subreddit('pug')
        subs = subreddit.top(limit = 500)
        imgs = []
        async for x in subs:
            imgs.append(x)
        img = random.choice(imgs)
        img_url = img.url
        em=nextcord.Embed(title = f'', color=nextcord.Color.blue())
        em.set_image(url=img_url)
        em.set_footer(icon_url=ctx.author.avatar.url, text=f'Requested by {ctx.author.name}')
        em.timestamp = datetime.datetime.utcnow()
        await msg.edit(content = '', embed = em)

    @commands.command()
    async def nick(self, ctx, *, nickname):
        user = ctx.author
        try:
            await user.edit(nick = nickname)
            await ctx.reply(f'<:check_90:881380678938296410> Your nickname has been changed to {nickname}')
        except:
            await ctx.reply('<:xmark:884407516363108412> Failed to change nickname')
    @nick.error
    async def _(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            em=nextcord.Embed(title='Command: Nick', description='**Usage:** nick <nickname>\n**Example:** nick 123eyesonme')
            await ctx.send(embed=em)

    @commands.command()
    async def avatar(self, ctx, member : nextcord.Member):
        embed = nextcord.Embed(color = nextcord.Color.blue())
        embed.set_image(url = member.avatar.url)
        await ctx.send(embed=embed)
    @avatar.error
    async def _(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            em=nextcord.Embed(title='Command: avatar', description=f'**Usage:** avatar <member>\n**Example:** avatar {ctx.author.mention}')
            await ctx.send(embed=em)

    @commands.command()
    async def membercount(self, ctx):
        count = 0
        for member in ctx.guild.members:
            count += 1
        em = nextcord.Embed(color = nextcord.Color.blue())
        em.add_field(name='Members', value=count)
        em.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=em)

    @commands.command()
    async def roll(self, ctx):
        await ctx.send(f'You rolled a {random.randint(1, 6)}!')

    @commands.command()
    async def roulet(self, ctx):
        member=ctx.author
        num = random.randint(1, 6)
        if 2 == num:
            await ctx.send(f'`Oh no! It seems like {ctx.author.name} got unlucky and rolled a 2! They will get the maximum punishment of a 30 second mute wuahaha`')
            muted_role = nextcord.utils.get(ctx.guild.roles, name="Muted")
            guild = ctx.guild
            if not muted_role:
                muted_role = await guild.create_role(name = 'Muted')
                for channel in guild.text_channels:
                    await channel.set_permissions(muted_role, send_messages = False)
            await member.add_roles(muted_role)
            await asyncio.sleep(30)
            await member.remove_roles(muted_role)
            return
        await ctx.send(f'`You rolled a {num} lucky you...`')

    @commands.command()
    async def rps(self, ctx, choice):
        if choice not in ['rock','paper','scissors']:
            await ctx.send('`Invalid choice only use rock, paper or scissors`')
            return
        d = {'rock':1, 'paper':2, 'scissors':3}
        user_choice = d[choice]
        x = random.choice(['rock','paper','scissors'])
        bot_choice = d[x]
        if user_choice > bot_choice:
            if user_choice-2 == bot_choice:
                await ctx.send(f'You chose **{choice}**, I chose **{x}**\n{x} wins!')
                return
            await ctx.send(f'You chose **{choice}**, I chose **{x}**\n{choice} wins!')
        elif bot_choice > user_choice:
            if bot_choice-2 == user_choice:
                await ctx.send(f'You chose **{choice}**, I chose **{x}**\n{choice} wins!')
                return
            await ctx.send(f'You chose **{choice}**, I chose **{x}**\n{x} wins!')
        elif bot_choice == user_choice:
            await ctx.send(f'You chose **{choice}**, I chose **{x}**\nTie!')
    @rps.error
    async def _(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            em=nextcord.Embed(title='Command: rps', description=f'**Usage:** rps <choice>\n**Example:** rps rock')
            await ctx.send(embed=em)

    @commands.command()
    async def flip(self, ctx):
        await ctx.send(f'{ctx.author.mention} '+random.choice(['Heads','Tails']))

    @commands.command()
    async def sus(self, ctx):
        await ctx.send('Damn bro thats kinda sus 📮')

    @commands.command()
    async def rickroll(self, ctx):
        await ctx.send("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        

def setup(client):
    client.add_cog(Fun(client))