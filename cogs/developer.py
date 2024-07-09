# cogs/developer.py
import discord
from discord.ext import commands
import asyncio
import inspect

def is_bot_owner():
    async def predicate(ctx):
        return await ctx.bot.is_owner(ctx.author)
    return commands.check(predicate)

class Developer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='eval', hidden=True)
    @is_bot_owner()  # Restrict this command to bot owners only
    async def eval_command(self, ctx, *, code: str):
        """Evaluates a Python code snippet."""
        code = code.strip('` ')
        python = '```py\n{}\n```'
        result = None

        # Prepare the execution environment
        local_vars = {
            'ctx': ctx,
            'bot': self.bot,
            'discord': discord,
            'commands': commands,
            'asyncio': asyncio,
            'inspect': inspect
        }

        try:
            # Execute the code
            result = eval(code, local_vars)
            if inspect.isawaitable(result):
                result = await result
        except Exception as e:
            result = type(e).__name__ + ': ' + str(e)
        finally:
            # Send the result back to the user
            await ctx.send(python.format(result))

    @commands.command(name='restart', hidden=True)
    @is_bot_owner()  # Restrict this command to bot owners only
    async def restart_bot(self, ctx):
        """Restarts the bot."""
        await ctx.send('Restarting...')
        await self.bot.logout()

    @restart_bot.error
    async def restart_bot_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("You don't have permission to restart the bot.")

    @commands.command(name='listguilds', hidden=True)
    @is_bot_owner()  # Restrict this command to bot owners only
    async def list_guilds(self, ctx):
        """Lists all the guilds the bot is currently in."""
        guilds_info = []
        for guild in self.bot.guilds:
            guild_info = f'Name: {guild.name}\nID: {guild.id}\nMembers: {guild.member_count}\n'
            guilds_info.append(guild_info)
        guilds_list = '\n'.join(guilds_info)
        await ctx.send(f'```ini\n{guilds_list}\n```')

    @commands.command(name='bkick', hidden=True)
    @is_bot_owner()  # Restrict this command to bot owners only
    async def bkick(self, ctx, server_id: int):
        """Kicks the bot from a server using its ID."""
        guild = self.bot.get_guild(server_id)
        if guild:
            await guild.leave()
            await ctx.send(f'Left server "{guild.name}" ({guild.id})')
        else:
            await ctx.send(f'Could not find server with ID {server_id}')

async def setup(bot):
    await bot.add_cog(Developer(bot))
