import discord
from discord.ext import commands
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import io

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='serverstats', aliases=['sstats'], help='Show server message statistics. Optionally specify a month (e.g., June)')
    async def server_stats(self, ctx, month: str = None):
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

async def setup(bot):
    await bot.add_cog(Stats(bot))
