import discord 
from discord.ext import commands

class Test(commands.Cog):
    def __init__(self, bot):
        self.interaction = None

    @commands.command()
    async def example(self, ctx:commands.Context):
        await ctx.send("hay", view=TestResponseView(self))


class TestResponseView(discord.ui.View):
    def __init__(self, main_class: Test):
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



async def setup(bot):
    await bot.add_cog(Test(bot))
