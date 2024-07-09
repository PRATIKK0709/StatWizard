# cogs/logging.py
import discord
from discord.ext import commands
import json
import os

class MessageLogging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channels = {}
        self.load_log_channels()

    def load_log_channels(self):
        if os.path.exists('log_channels.json'):
            with open('log_channels.json', 'r') as f:
                self.log_channels = json.load(f)

    def save_log_channels(self):
        with open('log_channels.json', 'w') as f:
            json.dump(self.log_channels, f)

    @commands.command(name='setlogchannel', help='Set the channel for message logging')
    @commands.has_permissions(administrator=True)
    async def set_log_channel(self, ctx, channel: discord.TextChannel):
        guild_id = str(ctx.guild.id)
        self.log_channels[guild_id] = channel.id
        self.save_log_channels()
        await ctx.send(f'Log channel set to {channel.mention} for this server.')

    async def send_log(self, embed: discord.Embed, guild_id: int):
        guild_id = str(guild_id)
        if guild_id in self.log_channels:
            log_channel = self.bot.get_channel(self.log_channels[guild_id])
            if log_channel:
                permissions = log_channel.permissions_for(log_channel.guild.me)
                if permissions.manage_webhooks and permissions.send_messages:
                    try:
                        webhook = await log_channel.create_webhook(name='Message Log')
                        bot_user = self.bot.user
                        await webhook.send(embed=embed, username=bot_user.display_name, avatar_url=bot_user.avatar.url)
                        await webhook.delete()
                    except discord.Forbidden:
                        print(f'Error: Missing permissions to create webhook in channel {log_channel.id}.')
                else:
                    print(f'Error: Bot lacks required permissions in channel {log_channel.id}.')
            else:
                print(f'Error: Log channel with ID {self.log_channels[guild_id]} not found.')

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        guild_id = message.guild.id
        embed = discord.Embed(
            title="Message Deleted",
            color=discord.Color.red()
        )
        embed.add_field(name='Author', value=f'{message.author} ({message.author.id})')
        embed.add_field(name='Channel', value=message.channel.mention)
        embed.add_field(name='Message Content', value=message.content, inline=False)
        embed.set_footer(text=f'Deleted at {discord.utils.utcnow().strftime("%Y-%m-%d %H:%M:%S")} UTC')
        embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar.url)
        await self.send_log(embed, guild_id)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        guild_id = after.guild.id
        embed = discord.Embed(
            title="Message Edited",
            color=discord.Color.gold()
        )
        embed.add_field(name='Author', value=f'{after.author} ({after.author.id})')
        embed.add_field(name='Channel', value=after.channel.mention)
        embed.add_field(name='Original Message', value=before.content, inline=False)
        embed.add_field(name='Edited Message', value=after.content, inline=False)
        embed.add_field(name='Jump to Message', value=f'[Click here]({after.jump_url})')
        embed.set_footer(text=f'Edited at {after.edited_at.strftime("%Y-%m-%d %H:%M:%S")} UTC')
        embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar.url)
        await self.send_log(embed, guild_id)

async def setup(bot):
    await bot.add_cog(MessageLogging(bot))
