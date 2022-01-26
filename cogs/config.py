from datetime import datetime
from logging import exception
from os import name
from typing import Text
import nextcord
from nextcord.channel import VocalGuildChannel
from nextcord.colour import Color
from nextcord.components import C
from nextcord.ext import commands, menus
import json
import motor
from motor import motor_asyncio

try:
    cluster = motor_asyncio.AsyncIOMotorClient(
        "mongodb+srv://tyrus:Tyrus113@cluster0.qifea.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")  # here will be the link for your cluster
    db = cluster["cloud_bot"]  # write your db name here
    # write the name of the collection present in the db where data will be stored
    collection = db["data"]
    print('Database Connected Successfully - config.py')
except:
    print('Database Connection Failed - config.py')


welcdes = '`Defset` - *Set a channel to the default channel for your server*\n`Welcomeset <channel>` - *Set a channel to recieve welcomes*\n`Leaveset <channel>` - *Set a channel to recieve leaves*\n`On` - *Turn welcomes on*\n`Off` - *Turn welcomes off*\n`Msgset` - *Customize the message I send when somebody joins*\n`Msgreset` - *Return to the default welcome message*\n`Welcomestats` - *Display important information about your welcome status*\n'
welcdes += '`Addrole` - *Add a role to be given to new member that join*\n'
welcdes += '`Removerole` - *Remove a role from your on join add role event*\n'
welcdes += '`Welcomedm` - *Configure the dm i sent to a user that joins this guild*\n'
welcdes += '`Welcomedm_remove` - *Remove your previously set welcome dm*\n'

botdes = ''
botdes += '`block_invites` - *Block messages that contain discord invites*\n'
botdes += '`unblock_invites` - *Allow discord invites to be sent*\n'
botdes += '`block_links` - *Blocks all links from chat*\n'
botdes += '`unblock_links` - *Unblocks all links from chat*\n'
botdes += '`Updates` - *Recieve the latest updates from cloud bot in a channel*\n'
botdes += '`Spamchannel` - *Users will not be muted for spam in this channel*\n'
botdes += '`Delspamchannel` - *Users will be muted for spam in this channel*\n'
botdes += '`Prefix` - *Change my prefix for your server*\n'
botdes += '`Configstats` - *Configuration settings overview*\n'


class Config(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def updates(self, ctx):
        if not ctx.author.guild_permissions.manage_messages:
            await ctx.send('This command requires `manage_messages` permission')
            return

        guild = ctx.guild
        defRole = ctx.guild.default_role
        channel = nextcord.utils.get(
            guild.text_channels, name='cloud-announcments')

        if not channel:
            channel = await guild.create_text_channel('cloud-announcments')
            await channel.set_permissions(defRole, send_messages=False)
        else:
            await ctx.send('<:xmark:884407516363108412> An update channel has already been created')
            return

        class btnMenu(menus.ButtonMenu):

            def __init__(self):
                super().__init__()

            async def send_initial_message(self, ctx, ctxchannel):
                em = nextcord.Embed(
                    title='Update Channel Set!',
                    description='This channel will now recieve updates about me!',
                    color=nextcord.Color.green()
                )
                return await channel.send(embed=em, view=self)

            @nextcord.ui.button(label='Awesome!', style=nextcord.ButtonStyle.primary)
            async def on_role_click(self, button, interaction):
                pass

        await btnMenu().start(ctx)
        await ctx.send('<:check_90:881380678938296410> I have created a channel to recieve updates')

    @commands.command()
    async def welc(self, ctx):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send('This command requires `administrator` permmisions')
            return
        em = nextcord.Embed(title='Welcome config',
                            description=welcdes, color=nextcord.Color.blue())
        await ctx.send(embed=em)

    @commands.command()
    async def defset(self, ctx, channel: nextcord.TextChannel = None):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send('This command requires `administrator` permmisions')
            return
        channel = channel or ctx.channel
        await collection.update_one({'_id': ctx.guild.id}, {'$set': {'default_channel': channel.id}})
        await ctx.send(f'<:check_90:881380678938296410> | Default channel set to {channel.name}')

    @commands.command()
    async def welcomeset(self, ctx, channel: nextcord.TextChannel = None):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send('This command requires `administrator` permmisions')
            return
        channel = channel or ctx.channel
        try:
            await collection.update_one({'_id': ctx.guild.id}, {'$set': {'welcome_channel': channel.id}})
            await ctx.send(f'<:check_90:881380678938296410> | Welcome channel set to : {channel}')
        except:
            await ctx.send('<:xmark:884407516363108412> Something went wrong')

    @commands.command()
    async def leaveset(self, ctx, channel: nextcord.TextChannel = None):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send('This command requires `administrator` permmisions')
            return
        channel = channel or ctx.channel
        try:
            await collection.update_one({'_id': ctx.guild.id}, {'$set': {'leave_channel': channel.id}})
            await ctx.send(f'<:check_90:881380678938296410> | Leave channel set to : {channel}')
        except:
            await ctx.send('<:xmark:884407516363108412> Something went wrong')

    @commands.command()
    async def off(self, ctx):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send('This command requires `administrator` permmisions')
            return
        await collection.update_one({'_id': ctx.guild.id}, {'$set': {'welc': 0}})
        await ctx.send('<:check_90:881380678938296410> | Welcomes set to off')

    @commands.command()
    async def on(self, ctx):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send('This command requires `administrator` permmisions')
            return
        await collection.update_one({'_id': ctx.guild.id}, {'$set': {'welc': 1}})
        await ctx.send('<:check_90:881380678938296410> | Welcomes set to on')

    @commands.command()
    async def msgset(self, ctx, *, text):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send('This command requires `administrator` permmisions')
            return
        try:
            await collection.update_one({'_id': ctx.guild.id}, {'$set': {'welc_msg': str(text)}})
            await ctx.send('<:check_90:881380678938296410> | Custom welcome message set')
        except:
            await ctx.send('<:xmark:884407516363108412> | Something went wrong')

    @msgset.error
    async def _(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            count = 0
            guild = self.client.get_guild(ctx.guild.id)
            members = guild.members
            for member in members:
                count = count + 1

            em = nextcord.Embed(
                title='Command: Msgset', description='**Usage:** *msgset <message>*\n**Example:** *msgset hello new user*')
            em.add_field(
                name='Key', value='{members} shows how many members and in a guild\n{member} mentions the new user in the welcome embed\n{guild} shows the name of the guild in the welcome embed', inline=False)
            em.add_field(
                name='Key Example', value='Welcome to {guild} {member} you are the {members} member to join!', inline=False)
            em.add_field(name='Example Translation',
                         value=f'Welcome to {ctx.guild.name} {ctx.author.mention} you are the {count} member to join!', inline=False)
            await ctx.send(embed=em)

    @commands.command()
    async def msgreset(self, ctx):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send('This command requires `administrator` permmisions')
            return
        try:
            await collection.update_one({'_id': ctx.guild.id}, {'$set': {'welc_msg': 0}})
            await ctx.send('<:check_90:881380678938296410> | Custom welcome message reset')
        except:
            await ctx.send('<:xmark:884407516363108412> | Something went wrong')

    @commands.command()
    async def welcomestats(self, ctx):
        result = await collection.find_one({'_id': ctx.guild.id})
        default_channel = self.client.get_channel(result['default_channel'])
        if result['welc'] == 0:
            welc = 'Welcomes Off!'
        else:
            welc = 'Welcomes On!'
        if result['welcome_channel'] == 0:
            welc_channel = default_channel
        else:
            welc_channel = self.client.get_channel(result['welcome_channel'])
        if result['leave_channel'] == 0:
            leave_channel = default_channel
        else:
            leave_channel = self.client.get_channel(result['leave_channel'])
        if result['welc_msg'] == 0:
            welc_msg = 'Default'
        else:
            welc_msg = result['welc_msg']
        try:
            roles = ''
            if len(result['roles']) == 0:
                roles = 'No welcome roles!'
            else:
                for role in result['roles']:
                    x = nextcord.utils.get(ctx.guild.roles, id=role)
                    roles += f'{x.mention} '
        except:
            roles = 'No welcome roles'
        try:
            welc_dm = result['welc_dm']
        except:
            welc_dm = 'Default'

        em = nextcord.Embed(color=nextcord.Color.blue())
        em.add_field(name='Default Channel',
                     value=default_channel.mention, inline=False)
        em.add_field(name='Welcome Channel',
                     value=welc_channel.mention, inline=False)
        em.add_field(name='Leave Channel',
                     value=leave_channel.mention, inline=False)
        em.add_field(name='Welcome Status',
                     value=welc, inline=False)
        em.add_field(name='Welcome Message',
                     value=welc_msg, inline=False)
        em.add_field(name='Welcome Roles',
                     value=roles, inline=False)
        em.add_field(name='Welcome DM',
                     value=welc_dm, inline=False)
        em.add_field(
            name='🔗 Useful Links', value='[My Fiverr](https://www.fiverr.com/tyrus_b/program-a-professional-and-custom-discord-bot-for-you) | [Support Server](https://discord.gg/72udgVqEkf) | [Invite Me](https://top.gg/bot/881336046778986518)')
        em.set_author(name='Welcome Status')
        em.set_thumbnail(url=self.client.user.avatar.url)
        em.set_footer(icon_url=ctx.author.avatar.url,
                      text=f'Requested by {ctx.author.name}')
        await ctx.send(embed=em)

    @commands.command()
    async def addrole(self, ctx, role: nextcord.Role):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send('This command requires `administrator` permmisions')
            return
        try:
            try:
                result = await collection.find_one({'_id': ctx.guild.id})
                arr = result['roles']
                if not role.id in arr:
                    arr.append(role.id)
                    await collection.update_one({'_id': ctx.guild.id}, {'$push': {'roles': role.id}})
                else:
                    await ctx.send('Role already set')
                    return
            except:
                await collection.update_one({'_id': ctx.guild.id}, {'$set': {'roles': [role.id]}})
            await ctx.send(f'<:check_90:881380678938296410> | Success! {role.name} has been added')
        except:
            await ctx.send('<:xmark:884407516363108412> | Something went wrong')

    @commands.command()
    async def removerole(self, ctx, role: nextcord.Role):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send('This command requires `administrator` permmisions')
            return
        try:
            try:
                await collection.update_one({'_id': ctx.guild.id}, {'$pull': {'roles': role.id}})
                await ctx.send(f'<:check_90:881380678938296410> | Success! {role.name} has been removed')
            except:
                await ctx.send('No welcome roles setup')
        except:
            await ctx.send('<:xmark:884407516363108412> | Something went wrong')

    @commands.command()
    async def welcomedm(self, ctx, *, message):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send('This command requires `administrator` permmisions')
            return
        try:
            await collection.update_one({'_id': ctx.guild.id}, {'$set': {'welc_dm': str(message)}})
            await ctx.send('<:check_90:881380678938296410> | Success welcome dm has been set')
        except:
            await ctx.send('<:xmark:884407516363108412> | Something went wrong')

    @commands.command()
    async def welcomedm_remove(self, ctx):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send('This command requires `administrator` permmisions')
            return
        try:
            result = await collection.find_one({'_id': ctx.guild.id})
            try:
                result['welc_dm']
                await collection.update_one({'_id': ctx.guild.id}, {'$unset': {'welc_dm': ''}})
                await ctx.send('<:check_90:881380678938296410> Success, welcome dm removed')
            except:
                await ctx.send('<:xmark:884407516363108412> No welcome dm found')
                return
        except:
            await ctx.send('<:xmark:884407516363108412> | Something went wrong')

    @commands.group(invoke_without_command=True)
    async def bot(self, ctx):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send('This command requires `administrator` permmisions')
            return
        em = nextcord.Embed(title='Bot config',
                            description=botdes, color=nextcord.Color.blue())
        em.add_field(name='🔗 Useful Links',
                     value='[My Fiverr](https://www.fiverr.com/tyrus_b/program-a-professional-and-custom-discord-bot-for-you) | [Support Server](https://discord.gg/72udgVqEkf) | [Invite Me](https://top.gg/bot/881336046778986518)')
        await ctx.send(embed=em)

    @commands.command()
    async def block_links(self, ctx):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send('This command requires `administrator` permmisions')
            return
        try:
            await collection.update_one({'_id': ctx.guild.id}, {'$set': {'blocked_invites': 2}})
            await ctx.send('<:check_90:881380678938296410> All links will be blocked')
        except:
            await ctx.send('<:xmark:884407516363108412> Something went wrong')

    @commands.command()
    async def unblock_links(self, ctx):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send('This command requires `administrator` permmisions')
            return
        try:
            await collection.update_one({'_id': ctx.guild.id}, {'$set': {'blocked_invites': 0}})
            await ctx.send('<:check_90:881380678938296410> All links will be unblocked')
        except:
            await ctx.send('<:xmark:884407516363108412> Something went wrong')

    @commands.command()
    async def block_invites(slef, ctx):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send('This command requires `administrator` permmisions')
            return
        result = await collection.find_one({'_id': ctx.guild.id})
        try:
            await collection.update_one({'_id': ctx.guild.id}, {'$set': {'blocked_invites': 1}})
            await ctx.send('<:check_90:881380678938296410> Discord invites will now be blocked')
        except:
            await ctx.send('<:xmark:884407516363108412> Something went wrong')

    @commands.command()
    async def unblock_invites(slef, ctx):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send('This command requires `administrator` permmisions')
            return
        result = await collection.find_one({'_id': ctx.guild.id})
        try:
            await collection.update_one({'_id': ctx.guild.id}, {'$set': {'blocked_invites': 0}})
            await ctx.send('<:check_90:881380678938296410> Discord invites will now not be blocked')
        except:
            await ctx.send('<:xmark:884407516363108412> Something went wrong')

    @commands.command()
    async def spamchannel(self, ctx, channel: nextcord.TextChannel):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send('This command requires `administrator` permmisions')
            return
        result = await collection.find_one({'_id': ctx.guild.id})
        try:
            await collection.update_one({'_id': ctx.guild.id}, {'$addToSet': {'spam_channel': channel.id}})
            await ctx.send('<:check_90:881380678938296410> Success, spam channel added')
        except exception as e:
            print(e)
            await ctx.send('<:xmark:884407516363108412> Something went wrong')

    @commands.command()
    async def delspamchannel(self, ctx, channel: nextcord.TextChannel):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send('This command requires `administrator` permmisions')
            return
        try:
            await collection.update_one({'_id': ctx.guild.id}, {'$pull': {'spam_channel': channel.id}})
            await ctx.send('<:check_90:881380678938296410> Success, spam channel removed')
        except:
            await ctx.send('<:xmark:884407516363108412> Something went wrong')

    @commands.command()
    async def prefix(self, ctx, prefix):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send('This command requires `administrator` permmisions')
            return
        if len(prefix) > 2:
            await ctx.send('<:xmark:884407516363108412> Prefix Denied - Max length 2 characters')
            return
        await collection.update_one({'_id': ctx.guild.id}, {'$set': {'prefix': str(prefix)}})
        await ctx.send(f'<:check_90:881380678938296410> | `Prefix set to : {prefix}`')

    @commands.command()
    async def configstats(self, ctx):
        result = await collection.find_one({'_id': ctx.guild.id})
        spam = ''
        prefix = result['prefix']
        try:
            for x in result['spam_channel']:
                cha = self.client.get_channel(x)
                spam += cha.mention + ' '
        except:
            spam = 'No spam channels'
        try:
            if result['blocked_invites'] == 2:
                block = 'All Links'
            elif result['blocked_invites'] == 1:
                block = 'Discord Invites'
            else:
                block = 'Off'
        except:
            block = 'False'
        if len(spam) == 0:
            spam = 'No spam channels'
        if result['welc'] == 0:
            welc = 'Welcomes Off!'
        else:
            welc = 'Welcomes On!'
        em = nextcord.Embed(color=nextcord.Color.blue())
        em.add_field(name='Bot Prefix', value=prefix, inline=False)
        em.add_field(name='Spam Channels', value=spam, inline=False)
        em.add_field(name='Links Blocked?', value=block)
        em.add_field(name='Welcome Status', value=welc, inline=False)
        em.add_field(name='🔗 Useful Links',
                     value='[My Fiverr](https://www.fiverr.com/tyrus_b/program-a-professional-and-custom-discord-bot-for-you) | [Support Server](https://discord.gg/72udgVqEkf) | [Invite Me](https://top.gg/bot/881336046778986518)')
        em.set_author(name='Config Overview')
        em.timestamp = datetime.utcnow()
        await ctx.send(embed=em)


def setup(client):
    client.add_cog(Config(client))
