import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from datetime import datetime
import json
import matplotlib.pyplot as plt
import io
import seaborn as sns

load_dotenv()

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True
intents.webhooks = True  # Required for creating webhooks
intents.guilds = True
bot = commands.Bot(command_prefix='.', intents=intents, help_command=None)

roles_filename = 'allowed_roles.json'
config_filename = 'config.json'

def load_config():
    if os.path.exists(config_filename):
        with open(config_filename, 'r') as f:
            return json.load(f)
    else:
        return {}

config = load_config()

def load_allowed_roles():
    if os.path.exists(roles_filename):
        with open(roles_filename, 'r') as f:
            return json.load(f)
    else:
        return {}

allowed_roles = load_allowed_roles()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    await bot.change_presence(activity=discord.Game(name="Monitoring Server Activity"))

    # Load edit log channel from config on bot startup
    for guild_id, guild_config in config.items():
        if 'edit_log_channel' in guild_config:
            edit_log_channel_id = guild_config['edit_log_channel']
            edit_log_channel = bot.get_channel(edit_log_channel_id)
            if edit_log_channel:
                print(f'Loaded edit log channel: {edit_log_channel.name} ({edit_log_channel.id}) for guild {guild_id}')
            else:
                print(f'Error: Edit log channel with ID {edit_log_channel_id} not found for guild {guild_id}.')
        else:
            print(f'Error: Edit log channel not configured for guild ID {guild_id}. Use .seteditlog command to set it.')


#CommandAdd- modstats - setailed statistics for members with a specific role!

@bot.command(name='modstats', aliases=['mstats'], help='Show detailed statistics for members with a specific role, month, and year', cog_name='Staff Activity')
async def mod_stats(ctx, role: discord.Role, month: str = None, year: str = None):
    guild_id = str(ctx.guild.id)
    if guild_id not in allowed_roles or not allowed_roles[guild_id]:
        await ctx.send('No Admin role set. Please ask a server manager to set a admin role using `!setadminrole @role`.')
        return
    
    # Check if the user has one of the allowed roles
    member_roles = [r.id for r in ctx.author.roles]
    if role.id not in allowed_roles[guild_id] or role.id not in member_roles:
        await ctx.send('You do not have permission to use this command.')
        return

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

async def count_user_messages_in_channel(user, channel, target_month=None, target_year=None):
    message_count = 0
    async for message in channel.history(limit=None):
        if message.author == user:
            if (target_month is None or message.created_at.month == target_month) and (target_year is None or message.created_at.year == target_year):
                message_count += 1
    return message_count

#CommandAdd - setadminrole - Set a role that can use modstats

# Command to set allowed roles
@bot.command(name='setadminrole', aliases=['sar'], help='Set a role that can use modstats command\n\nUsage: `.setadminrole @role` or `.sar @role`')
@commands.has_permissions(administrator=True)
async def set_mod_role(ctx, role: discord.Role):
    guild_id = str(ctx.guild.id)
    if guild_id not in allowed_roles:
        allowed_roles[guild_id] = []

    if role.id not in allowed_roles[guild_id]:
        allowed_roles[guild_id].append(role.id)
        with open(roles_filename, 'w') as f:
            json.dump(allowed_roles, f, indent=4)
        await ctx.send(f'{role.name} role can now use modstats command.')
    else:
        await ctx.send(f'{role.name} role already has permission.')

#CommandAdd tells you wtf is bot for, like what's it's purpose!
@bot.command(name='help', aliases=['h'], help='Shows the list of available commands and their usage.')
async def help_command(ctx, command_name: str = None):
    if command_name:
        # Check if the specified command exists
        command = bot.get_command(command_name)
        if not command:
            await ctx.send(f'Command `{command_name}` not found.')
            return
        
        # Build detailed help for the specified command
        embed = discord.Embed(title=f'Command: {command.name}', description=command.help, color=discord.Color.green())
        if command.aliases:
            embed.add_field(name='Aliases', value=', '.join(command.aliases), inline=False)
        await ctx.send(embed=embed)
    else:
        # Define hardcoded categories and their commands
        categories = {
            "Staff Activity": ["modstats", "setadminrole"],
            "Uncategorized": []
        }

        embed = discord.Embed(title='Bot Commands', description='Use `.help <command>` for more details on a command.', color=discord.Color.blue())

        for category, commands in categories.items():
            category_name = category.capitalize()
            command_list = "\n".join(f"`{cmd}`" for cmd in commands)
            embed.add_field(name=category_name, value=command_list, inline=False)

        await ctx.send(embed=embed)

#CommandAdd serverstats- tells you a little stats about how active your server channels are and a nice graph as well
@bot.command(name='serverstats', aliases=['sstats'], help='Show server message statistics. Optionally specify a month (e.g., June)')
async def server_stats(ctx, month: str = None):
    current_date = datetime.utcnow()
    total_messages = 0
    month_activity = {}  # Dictionary to store message counts per month and per channel

    # Calculate message counts for each channel and each month
    for channel in ctx.guild.text_channels:
        async for message in channel.history(limit=None):
            if message.created_at.year == current_date.year:
                month_name = message.created_at.strftime('%B')
                if month_name not in month_activity:
                    month_activity[month_name] = {}
                if channel.name not in month_activity[month_name]:
                    month_activity[month_name][channel.name] = 0
                month_activity[month_name][channel.name] += 1

                if month and message.created_at.strftime('%b').lower() == month.lower():
                    total_messages += 1

    # Determine the month with the highest activity
    if month_activity:
        most_active_month = max(month_activity, key=lambda x: sum(month_activity[x].values()))
    else:
        most_active_month = "N/A"

    # Create an embed for displaying statistics
    embed = discord.Embed(title='Server Message Statistics', color=discord.Color.blue(), timestamp=current_date)
    embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url)

    if month:
        embed.set_footer(text=f'Statistics for {month.capitalize()}')
        total_messages = sum(month_activity.get(month.capitalize(), {}).values())
        if total_messages:
            channel_names = []
            message_counts = []
            for channel_name, count in month_activity.get(month.capitalize(), {}).items():
                embed.add_field(name=channel_name, value=f'• **{count}** messages', inline=True)
                channel_names.append(channel_name)
                message_counts.append(count)

            # Generate a pie chart for the message distribution across channels
            plt.figure(figsize=(8, 6))
            plt.pie(message_counts, labels=channel_names, autopct='%1.1f%%', startangle=140)
            plt.title(f'Message Distribution in {month.capitalize()}')
            plt.axis('equal')

            # Save the pie chart to a BytesIO object
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            plt.close()

            # Send the pie chart as a file
            file = discord.File(buf, filename='channel_distribution.png')
            embed.set_image(url='attachment://channel_distribution.png')
        else:
            embed.add_field(name=f'Total Messages in {month.capitalize()}', value='No messages found.', inline=False)
    else:
        embed.set_footer(text='Overall Server Statistics')

        # Prepare data for the line chart
        months = list(month_activity.keys())
        message_counts = [sum(channel_counts.values()) for channel_counts in month_activity.values()]

        # Generate a line chart for the trend of messages over the months
        plt.figure(figsize=(12, 6))
        sns.lineplot(x=months, y=message_counts, marker='o')
        plt.xlabel('Months')
        plt.ylabel('Messages')
        plt.title('Monthly Message Activity Trend')
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Save the line chart to a BytesIO object
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()

        # Send the line chart as a file
        file = discord.File(buf, filename='monthly_trend.png')
        embed.set_image(url='attachment://monthly_trend.png')

        # Display activity for each month
        for month_name, channel_counts in month_activity.items():
            channels_info = '\n'.join(f'• **{channel}:** {count} messages' for channel, count in channel_counts.items())
            embed.add_field(name=f'{month_name} Activity', value=channels_info, inline=True)

    embed.add_field(name='Most Active Month', value=most_active_month, inline=False)

    # Send embed and file (if applicable) to the channel
    if not month:
        await ctx.send(embed=embed, file=file)
    else:
        await ctx.send(embed=embed, file=file)

@bot.event
async def on_message_edit(before, after):
    guild_id = str(before.guild.id)
    if guild_id in config and 'edit_log_channel' in config[guild_id]:
        edit_log_channel_id = config[guild_id]['edit_log_channel']
        edit_log_channel = bot.get_channel(edit_log_channel_id)
        
        if edit_log_channel:
            webhook = await edit_log_channel.create_webhook(name='Message Edit Log')
            
            embed = discord.Embed(title='Message Edited', color=discord.Color.gold())
            embed.add_field(name='Author', value=f'{after.author} ({after.author.id})')
            embed.add_field(name='Channel', value=after.channel.mention)
            embed.add_field(name='Original Message', value=before.content, inline=False)
            embed.add_field(name='Edited Message', value=after.content, inline=False)
            embed.add_field(name='Jump to Message', value=f'[Click here]({after.jump_url})')
            embed.set_footer(text=f'Edited at {after.edited_at.strftime("%Y-%m-%d %H:%M:%S")} UTC')

            bot_user = bot.user
            embed.set_author(name=bot_user.display_name, icon_url=bot_user.avatar.url)

            await webhook.send(embed=embed, username=bot_user.display_name, avatar_url=bot_user.avatar.url)
            await webhook.delete()  # Delete the webhook after use to clean up

        else:
            print(f'Error: Edit log channel with ID {edit_log_channel_id} not found for guild {guild_id}.')
    else:
        print(f'Error: Edit log channel not configured for guild ID {guild_id}. Use .seteditlog command to set it.')

# Command to set the logging channel for message edits
@bot.command(name='seteditlog', help='Set the channel for message edit logs.\nUsage: .seteditlog #channel')
@commands.has_permissions(administrator=True)
async def set_edit_log_channel(ctx, channel: discord.TextChannel):
    guild_id = str(ctx.guild.id)
    if guild_id not in config:
        config[guild_id] = {}
    
    config[guild_id]['edit_log_channel'] = channel.id
    with open(config_filename, 'w') as f:
        json.dump(config, f, indent=4)
    await ctx.send(f'Message edit logs will now be sent to {channel.mention}.')

# Ensure to check for guild_id as a string
def load_config():
    if os.path.exists(config_filename):
        with open(config_filename, 'r') as f:
            return {str(k): v for k, v in json.load(f).items()}
    else:
        return {}

config = load_config()

bot.run(os.getenv('DISCORD_TOKEN'))
