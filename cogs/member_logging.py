#cogs/member_logging.py
import discord
from discord.ext import commands
import json
import os

class MemberLogging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_file = 'member_log_config.json'
        self.config = self.load_config()

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        else:
            return {}

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    async def send_log(self, embed, guild_id):
        guild_id = str(guild_id)
        if guild_id in self.config and 'member_log_channel' in self.config[guild_id]:
            log_channel_id = self.config[guild_id]['member_log_channel']
            log_channel = self.bot.get_channel(log_channel_id)
            if log_channel:
                await log_channel.send(embed=embed)
            else:
                print(f'Error: Log channel with ID {log_channel_id} not found for guild {guild_id}.')
        else:
            print(f'Error: Log channel not configured for guild ID {guild_id}. Use .setmemberlog command to set it.')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = member.guild.id
        embed = discord.Embed(
            title="Member Joined",
            color=discord.Color.green()
        )
        embed.add_field(name='User', value=f'{member} ({member.id})')
        embed.set_footer(text=f'Joined at {member.joined_at.strftime("%Y-%m-%d %H:%M:%S")} UTC')
        embed.set_thumbnail(url=member.avatar.url)
        await self.send_log(embed, guild_id)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild_id = member.guild.id
        embed = discord.Embed(
            title="Member Left",
            color=discord.Color.red()
        )
        embed.add_field(name='User', value=f'{member} ({member.id})')
        embed.set_footer(text=f'Left at {discord.utils.utcnow().strftime("%Y-%m-%d %H:%M:%S")} UTC')
        embed.set_thumbnail(url=member.avatar.url)
        await self.send_log(embed, guild_id)

    @commands.command(name='setmemberlog')
    @commands.has_permissions(administrator=True)
    async def set_member_log_channel(self, ctx, channel: discord.TextChannel):
        guild_id = str(ctx.guild.id)
        if guild_id not in self.config:
            self.config[guild_id] = {}
        self.config[guild_id]['member_log_channel'] = channel.id
        self.save_config()
        await ctx.send(f'Member join/leave log channel has been set to {channel.mention}')

async def setup(bot):
    await bot.add_cog(MemberLogging(bot))
