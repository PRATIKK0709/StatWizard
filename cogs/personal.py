import discord
from discord.ext import commands

class Personal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def profile(self, ctx):
        await ctx.send(f'Username: {ctx.author.name}\nID: {ctx.author.id}')

    # Add more personal commands here

async def setup(bot):
    await bot.add_cog(Personal(bot))
