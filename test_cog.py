import discord 
from discord.ext import commands
from discord.ui import Button
import asyncio 

class TestCog(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.interaction = None
        self.check_msg = discord.Message
        self.bot = bot
        self.btn_msg = discord.Message
        self.temp_interaction = discord.Interaction

    @commands.command()
    async def tt(self, ctx:commands.Context):
        author = ctx.message.author
        print(author.name, author.nick, author.id)
        await ctx.reply(content = "HI!", ephemeral=True)

    @commands.command()
    async def ttt(self, ctx:commands.Context):
        from gameprocess import WaitForClick
        check_msg = await ctx.send("Check")
        btns = [["1", "1", discord.ButtonStyle.blurple]
                , ["2", "2", discord.ButtonStyle.blurple]
                , ["hai", "shit", discord.ButtonStyle.blurple]
                , ["boob", "big", discord.ButtonStyle.blurple]
        ]
        content = "Edited"
        await ctx.send("Main msg", view=TempResponseView(self))
        await asyncio.sleep(5)
        edit_msg = self.temp_interaction
        print("waiting")
        wait = WaitForClick(self.bot, edit_msg, content, btns, check_msg)
        value = await wait.create_btn_and_wait(is_delete_btn=True)
        print(value)

    @commands.command()
    async def wait_btn(self, ctx:commands.Context):
        self.check_msg = await ctx.send("this is for check")
        self.btn_msg = await ctx.send('test', view=WaitBtnResponseView(self))
        await ctx.send("hay")
        print("waiting")
        comfirm_str = ""
        reaction = discord.Reaction
        member = discord.Member
        def check(r:discord.Reaction, m:discord.Member):
            return r.emoji=="✅" and m.id == self.bot.user.id
        reaction, member = await self.bot.wait_for("reaction_add", check=check)
        print(reaction, member)
        print("wait over!")

class TempResponseView(discord.ui.View):
    def __init__(self, main_class:TestCog):
        super().__init__()
        self.main_class = main_class
    
    @discord.ui.button(label="click", style = discord.ButtonStyle.blurple)
    async def click(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("hi", ephemeral=True)
        await interaction.edit_original_response(content="hay")
        self.main_class.temp_interaction = interaction

class TestResponseView(discord.ui.View):
    def __init__(self, main_class: TestCog):
        super().__init__()
        self.main_class = main_class

    @discord.ui.button(label="click", style = discord.ButtonStyle.blurple)
    async def click(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.main_class.interaction is None:
            await interaction.response.send_message(
                content="Hello Mom.", 
                view=TestResponseView(self.main_class), 
                ephemeral=True)
            self.main_class.interaction = interaction
        else:
            await self.main_class.interaction.edit_original_response(content="editted")
            await interaction.response.defer()

class WaitBtnResponseView(discord.ui.View):
    def __init__(self, main_class: TestCog):
        super().__init__()
        self.main_class = main_class 
    
    @discord.ui.button(label = "stop waiting!", style = discord.ButtonStyle.green)
    async def stop_waiting(self, interaction: discord.Interaction, button: discord.ui.Button):
        # await interaction.response.defer()
        await self.main_class.check_msg.add_reaction("✅")
        await self.main_class.check_msg.clear_reactions()
        await interaction.response.send_message("1")


async def setup(bot):
    await bot.add_cog(TestCog(bot))
