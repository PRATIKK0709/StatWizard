import discord
from discord.ext import commands
import os
import json
from datetime import datetime

roles_filename = 'roles.json'

# Function to load allowed roles from roles.json
def load_allowed_roles():
    if os.path.exists(roles_filename):
        with open(roles_filename, 'r') as f:
            return json.load(f)
    else:
        return {}

allowed_roles = load_allowed_roles()

# Function to save allowed roles to roles.json
def save_allowed_roles():
    with open(roles_filename, 'w') as f:
        json.dump(allowed_roles, f, indent=4)

# Function to count user messages in a specific channel
async def count_user_messages_in_channel(user, channel, target_month=None, target_year=None):
    message_count = 0
    async for message in channel.history(limit=None):
        if message.author == user:
            if (target_month is None or message.created_at.month == target_month) and (target_year is None or message.created_at.year == target_year):
                message_count += 1
    return message_count

class ModActivity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='modstats', aliases=['mstats'], help='Show detailed statistics for members with a specific role, month, and year')
    async def mod_stats(self, ctx, role: discord.Role, month: str = None, year: str = None):
        current_date = datetime.utcnow()

        if year:
            try:
                target_year = int(year)
            except ValueError:
                await ctx.send(f'Invalid year format. Please enter a valid year (e.g., 2023).')
                return
        else:
            target_year = None

        if month:
            try:
                target_month = datetime.strptime(month, '%b').month
            except ValueError:
                await ctx.send(f'Invalid month format. Please use the first three letters of the month (e.g., Jan, Feb, Mar).')
                return
        else:
            target_month = None

        # Check if target date is in the future
        if target_year and target_month:
            target_date = datetime(year=target_year, month=target_month, day=1)
            if target_date > current_date:
                await ctx.send("Searching messages from the future? I can't help you with that!")
                return

        members_with_role = role.members

        if not members_with_role:
            await ctx.send(f'No members found with the role {role.name}.')
            return

        embed = discord.Embed(title=f'{role.name} Stats', color=discord.Color.blue(), timestamp=datetime.utcnow())

        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url)

        for member in members_with_role:
            total_messages = 0
            channel_message_counts = {}

            for channel in ctx.guild.text_channels:
                message_count = await count_user_messages_in_channel(member, channel, target_month, target_year)
                if message_count > 0:
                    channel_message_counts[channel.name] = message_count
                    total_messages += message_count

            if channel_message_counts:
                channels_info = '\n'.join(f'• **{channel_name}:** {count} messages' for channel_name, count in channel_message_counts.items())
            else:
                channels_info = 'No messages found in any channel.'

            embed.add_field(
                name=f'{member.display_name} | {member.id}',
                value=f'**Total Messages:** {total_messages}\n{channels_info}',
                inline=False
            )

        if target_month and target_year:
            month_name = datetime(year=2000, month=target_month, day=1).strftime('%B')
            embed.set_footer(text=f'Statistics for {month_name} {target_year}')
        elif target_month:
            month_name = datetime(year=2000, month=target_month, day=1).strftime('%B')
            embed.set_footer(text=f'Statistics for {month_name}')
        elif target_year:
            embed.set_footer(text=f'Statistics for {target_year}')

        await ctx.send(embed=embed)

    @commands.command(name='setadminrole', aliases=['sar'], help='Set a role that can use modstats command')
    @commands.has_permissions(administrator=True)
    async def set_mod_role(self, ctx, role: discord.Role):
        guild_id = str(ctx.guild.id)
        if guild_id not in allowed_roles:
            allowed_roles[guild_id] = []

        if role.id not in allowed_roles[guild_id]:
            allowed_roles[guild_id].append(role.id)
            save_allowed_roles()
            await ctx.send(f'{role.name} role can now use modstats command.')
        else:
            await ctx.send(f'{role.name} role already has permission.')

async def setup(bot):
    await bot.add_cog(ModActivity(bot))

