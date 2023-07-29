import discord
from discord.ext import commands
import asyncio

async def Test(bot:commands.Bot):
    msg = await bot.wait_for("message")
    return msg.content