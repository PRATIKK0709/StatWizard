import discord
from discord.ext import commands
from datetime import timedelta
import re

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ping', help='Check the bot\'s latency')
    async def ping(self, ctx):
        await ctx.send('Pong!')

    @commands.command(name='avatar', aliases=['av'], help='Get the avatar of a user by mention, Discord user ID, or the author\'s avatar if no ID is provided')
    async def avatar(self, ctx, target: discord.User = None):
        try:
            if target is None:
                user = ctx.author
            else:
                user = target
            
            avatar_url = user.avatar.url if user.avatar else user.default_avatar.url
            
            embed = discord.Embed(title=f"{user.name}'s Avatar", color=discord.Color.blue())
            embed.set_image(url=avatar_url)
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            
            await ctx.send(embed=embed)
        except discord.NotFound:
            await ctx.send('User not found. Please provide a valid user ID or mention.')
        except discord.HTTPException as e:
            await ctx.send(f'Failed to fetch avatar. Error: {e}')

    @commands.command(name='banner', help='Get the banner of a user by mention, Discord user ID, or the author\'s banner if no ID is provided')
    async def banner(self, ctx, user: discord.User = None):
        if user is None:
            user = ctx.author
        
        try:
            user = await self.bot.fetch_user(user.id)
            
            if user.banner:
                banner_url = user.banner.url
                embed = discord.Embed(title=f"{user.name}'s Banner", color=discord.Color.blue())
                embed.set_image(url=banner_url)
                embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"{user.name} does not have a banner set.")
        
        except discord.NotFound:
            await ctx.send('User not found. Please provide a valid user ID or mention.')
        except discord.HTTPException as e:
            await ctx.send(f'Failed to fetch banner. Error: {e}')

    @commands.command(name='userinfo', aliases=['ui'], help='Show information about a user')
    async def userinfo(self, ctx, user: discord.User = None):
        if user is None:
            user = ctx.author
        
        try:
            user = await self.bot.fetch_user(user.id)  # Ensure we fetch the full user object
            embed = discord.Embed(title=f"User Info - {user.name}", color=discord.Color.blue())
            embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)

            # Basic info
            embed.add_field(name="Username", value=user.name, inline=True)
            embed.add_field(name="User ID", value=user.id, inline=True)

            # Account creation date
            embed.add_field(name="Account Created On", value=user.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)

            # Fetching banner if it exists
            if user.banner:
                embed.set_image(url=user.banner.url)
            else:
                embed.add_field(name="Banner", value="None", inline=False)

            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            
            await ctx.send(embed=embed)
        
        except discord.NotFound:
            await ctx.send(f"User not found.")
        
        except discord.HTTPException as e:
            await ctx.send(f"An error occurred while fetching user info: {e}")

    @userinfo.error
    async def userinfo_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Invalid argument. Please provide a valid user mention or user ID.")
        else:
            await ctx.send(f"An error occurred: {error}")

    @commands.command(name='serverinfo', aliases=['si'], help='Show detailed information about the server')
    async def serverinfo(self, ctx):
     guild = ctx.guild
    
    # Fetching the owner
     owner = await self.bot.fetch_user(guild.owner_id)
    
    # Getting the number of roles
     role_count = len(guild.roles)
    
    # Getting the number of text and voice channels
     text_channels = len(guild.text_channels)
     voice_channels = len(guild.voice_channels)
     categories = len(guild.categories)
    
    # Getting the server creation date
     created_at = guild.created_at.strftime("%Y-%m-%d %H:%M:%S")
    
    # Getting the number of members
     member_count = guild.member_count
    
    # Getting the number of bots
     bot_count = sum(1 for member in guild.members if member.bot)
    
    # Getting the server boost level
     boost_level = guild.premium_tier
     boost_count = guild.premium_subscription_count
    
    # Getting the server icon URL
     icon_url = guild.icon.url if guild.icon else None
    
    # Getting the server banner URL
     banner_url = guild.banner.url if guild.banner else None

    # Getting server features
     feature_mapping = {
         'ANIMATED_BANNER': 'Animated Banner',
         'ANIMATED_ICON': 'Animated Icon',
         'APPLICATION_COMMAND_PERMISSIONS_V2': 'Application Command Permissions V2',
         'AUTO_MODERATION': 'Auto Moderation',
         'BANNER': 'Banner',
         'COMMUNITY': 'Community',
         'DEVELOPER_SUPPORT_SERVER': 'Developer Support Server',
         'DISCOVERABLE': 'Discoverable',
         'FEATURABLE': 'Featurable',
         'INVITE_SPLASH': 'Invite Splash',
         'MEMBER_VERIFICATION_GATE_ENABLED': 'Member Verification Gate Enabled',
         'MONETIZATION_ENABLED': 'Monetization Enabled',
         'MORE_STICKERS': 'More Stickers',
         'NEWS': 'News',
         'PARTNERED': 'Partnered',
         'PREVIEW_ENABLED': 'Preview Enabled',
         'PRIVATE_THREADS': 'Private Threads',
         'ROLE_ICONS': 'Role Icons',
         'SEVEN_DAY_THREAD_ARCHIVE': '7-Day Thread Archive',
         'TICKETED_EVENTS_ENABLED': 'Ticketed Events Enabled',
         'VANITY_URL': 'Vanity URL',
         'VERIFIED': 'Verified',
         'VIP_REGIONS': 'VIP Regions',
         'WELCOME_SCREEN_ENABLED': 'Welcome Screen Enabled'
    }

     server_features = [feature_mapping.get(feature, feature.replace('_', ' ').title()) for feature in guild.features]
     formatted_features = '\n'.join([f"- {feature}" for feature in server_features]) if server_features else 'None'
    
     embed = discord.Embed(title=f"Server Info - {guild.name}", color=discord.Color.blue())
    
     if icon_url:
         embed.set_thumbnail(url=icon_url)
    
     if banner_url:
         embed.set_image(url=banner_url)
    
     embed.add_field(name="Server Name", value=guild.name, inline=True)
     embed.add_field(name="Server ID", value=guild.id, inline=True)
     embed.add_field(name="Owner", value=f"{owner} (ID: {guild.owner_id})", inline=True)
     embed.add_field(name="Boost Level", value=boost_level, inline=True)
     embed.add_field(name="Boost Count", value=boost_count, inline=True)
     embed.add_field(name="Member Count", value=member_count, inline=True)
     embed.add_field(name="Bot Count", value=bot_count, inline=True)
     embed.add_field(name="Role Count", value=role_count, inline=True)
     embed.add_field(name="Text Channels", value=text_channels, inline=True)
     embed.add_field(name="Voice Channels", value=voice_channels, inline=True)
     embed.add_field(name="Categories", value=categories, inline=True)
     embed.add_field(name="Created On", value=created_at, inline=True)
     embed.add_field(name="Server Features", value=formatted_features, inline=False)
    
     embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
    
     await ctx.send(embed=embed)



async def setup(bot):
    await bot.add_cog(Utility(bot))
