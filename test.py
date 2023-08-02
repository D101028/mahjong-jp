import discord
from discord.ext import commands
import asyncio
async def Test(ctx:commands.Context, bot:commands.Bot):
  message = await ctx.send("hello")
  await asyncio.sleep(1)
  await message.edit(content="newcontent")
