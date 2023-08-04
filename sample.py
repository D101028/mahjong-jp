import discord
from discord.ext import commands
import json
import shutil
import os
import math
from pathlib import Path
import asyncio
# with open("./setting.json", mode = "rb") as file:
#     data = file.read()
# setting = json.loads(data)
# token = setting["TOKEN"]
# permission = setting["Permission"]

def create_embed(struct, choices: list, split = 25) -> discord.Embed:
    root = struct[0]
    dirs = struct[1]
    files = struct[2]
    descript = "Root: `{}`\n".format(root)
    descript += "Dirs:`\n"
    count = 0
    r = 0
    for dir in dirs:
        if count % split == 0:
            r += 1
            descript += f"  --list {r}--\n"
        descript += "    " + dir + "\n"
        count += 1
    descript += "`"
    descript += "Files:`\n"
    count = 0
    r = 0
    for file in files:
        if count % split == 0:
            r += 1
            descript += f"  --list {r}--\n"
        descript += "    " + file + "\n"
        count += 1
    descript += "`"
    descript += "you chose: \n  Dir: `{}`\n  File: `{}`".format(choices[0], choices[1])
    return discord.Embed(description=descript)

def split_for_num(input: list, num: int) -> list[list]:
    output = []
    count = 0
    r = 0
    l = []
    for n in input:
        l.append(input[count + r*num])
        count += 1
        if count == num:
            output.append(l)
            count = 0
            l = []
            r += 1
    if len(input) % num != 0:
        output.append(l)
    return output

def file_size(filepath: str):
    with open(filepath, mode="rb") as file:
        return len(file.read())

class File(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.root = r"D:\\"
        self.upload_drive_root = r"J:\我的雲端硬碟\remote"
        self.dir_choice = None
        self.file_choice = None
        self.struct = []
        for x,y,z in os.walk(self.root):
            self.struct.append(x)
            self.struct.append(y)
            self.struct.append(z)
            break
        self.select_list_pos = [0,0]
    @commands.command()
    async def file(self, ctx: commands.Context, root = None):
        if not root is None:
            if os.path.isdir(root):
                self.root = root
                self.struct = []
                for x,y,z in os.walk(self.root):
                    self.struct.append(x)
                    self.struct.append(y)
                    self.struct.append(z)
                    break
        await ctx.send(
            embed=create_embed(
                self.struct, 
                [self.dir_choice, self.file_choice]
            ), 
            view = FileResponseView(self)
        )

    async def reload_message(self):
        return create_embed(
                self.struct, 
                [self.dir_choice, self.file_choice]
            ), FileResponseView(self)

class FileResponseView(discord.ui.View):
    def __init__(self, main_class: File):
        super().__init__()
        self.main_class = main_class
        self.select_list = [] # [[dir_selects], [file_selects]]

        dir_options = []
        file_options = []
        for d in self.main_class.struct[1]:
            dir_options.append(
                discord.SelectOption(label = d[:97]+"..." if len(d)>=100 else d)
            )
        for f in self.main_class.struct[2]:
            file_options.append(
                discord.SelectOption(label = f[:97]+"..." if len(f)>=100 else f)
            )
        
        dir_list = split_for_num(dir_options, 25)
        file_list = split_for_num(file_options, 25)
        
        count = 0
        dir_selects = []
        for dir_part_opts in dir_list:
            count += 1
            select = discord.ui.Select(placeholder=f"dir list {count}", options=dir_part_opts)
            dir_selects.append(select)
        count = 0
        file_selects = []
        for file_part_opts in file_list:
            count += 1
            select = discord.ui.Select(placeholder=f"file list {count}", options=file_part_opts)
            file_selects.append(select)

        self.select_list.append(dir_selects)
        self.select_list.append(file_selects)

        if len(dir_options) == 0 and len(file_options) == 0:
            pass 
        elif len(file_options) == 0 and not len(dir_options) == 0:
            dir_select = self.select_list[0][self.main_class.select_list_pos[0]]

            async def dir_callback(interaction: discord.Interaction):
                chose = dir_select.values[0]
                self.main_class.dir_choice = chose
                await interaction.response.edit_message(
                    embed=create_embed(
                        self.main_class.struct, 
                        [self.main_class.dir_choice, self.main_class.file_choice]
                    ), 
                    view = FileResponseView(self.main_class)
                )

            dir_select.callback = dir_callback

            self.add_item(dir_select)
        elif len(dir_options) == 0 and not len(file_options) == 0:
            file_select = self.select_list[1][self.main_class.select_list_pos[1]]

            async def file_callback(interaction: discord.Interaction):
                chose = file_select.values[0]
                self.main_class.file_choice = chose
                await interaction.response.edit_message(
                    embed=create_embed(
                        self.main_class.struct, 
                        [self.main_class.dir_choice, self.main_class.file_choice]
                    ), 
                    view = FileResponseView(self.main_class)
                )

            file_select.callback = file_callback

            self.add_item(file_select)
        else:
            dir_select = self.select_list[0][self.main_class.select_list_pos[0]]
            file_select = self.select_list[1][self.main_class.select_list_pos[1]]

            async def dir_callback(interaction: discord.Interaction):
                chose = dir_select.values[0]
                self.main_class.dir_choice = chose
                await interaction.response.edit_message(
                    embed=create_embed(
                        self.main_class.struct, 
                        [self.main_class.dir_choice, self.main_class.file_choice]
                    ), 
                    view = FileResponseView(self.main_class)
                )
            async def file_callback(interaction: discord.Interaction):
                chose = file_select.values[0]
                self.main_class.file_choice = chose
                await interaction.response.edit_message(
                    embed=create_embed(
                        self.main_class.struct, 
                        [self.main_class.dir_choice, self.main_class.file_choice]
                    ), 
                    view = FileResponseView(self.main_class)
                )

            dir_select.callback = dir_callback
            file_select.callback = file_callback

            self.add_item(dir_select)
            self.add_item(file_select)

    @discord.ui.button(label="test", style = discord.ButtonStyle.blurple)
    async def test(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(str((self.main_class.dir_choice, self.main_class.file_choice)), ephemeral=True)

    @discord.ui.button(label="◀ dir", style = discord.ButtonStyle.blurple)
    async def dir_left(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.main_class.select_list_pos[0] = (self.main_class.select_list_pos[0] - 1) % len(self.select_list[0])
        embed, view = await self.main_class.reload_message()
        await interaction.response.edit_message(embed = embed, view = view)
        return 
    @discord.ui.button(label="▶", style = discord.ButtonStyle.blurple)
    async def dir_right(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.main_class.select_list_pos[0] = (self.main_class.select_list_pos[0] + 1) % len(self.select_list[0])
        embed, view = await self.main_class.reload_message()
        await interaction.response.edit_message(embed = embed, view = view)
        return 
    
    @discord.ui.button(label="◀ file", style = discord.ButtonStyle.blurple)
    async def file_left(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.main_class.select_list_pos[1] = (self.main_class.select_list_pos[1] - 1) % len(self.select_list[1])
        embed, view = await self.main_class.reload_message()
        await interaction.response.edit_message(embed = embed, view = view)
        return 
    @discord.ui.button(label="▶", style = discord.ButtonStyle.blurple)
    async def file_right(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.main_class.select_list_pos[1] = (self.main_class.select_list_pos[1] + 1) % len(self.select_list[1])
        embed, view = await self.main_class.reload_message()
        await interaction.response.edit_message(embed = embed, view = view)
        return 


    @discord.ui.button(label="↶parent dir", style = discord.ButtonStyle.gray)
    async def parent(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.main_class.root = Path(self.main_class.root).parent
        self.main_class.dir_choice = None
        self.main_class.file_choice = None
        self.main_class.struct = []
        for x,y,z in os.walk(self.main_class.root):
            self.main_class.struct.append(x)
            self.main_class.struct.append(y)
            self.main_class.struct.append(z)
            break
        self.main_class.select_list_pos = [0,0]
        embed, view = await self.main_class.reload_message()
        await interaction.response.edit_message(embed = embed, view = view)

    @discord.ui.button(label="go to dir", style = discord.ButtonStyle.gray)
    async def goto_dir(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.main_class.dir_choice is None:
            return await interaction.response.send_message("You need to choose a dir.")
        directory = os.path.join(self.main_class.root, self.main_class.dir_choice)
        self.main_class.root = directory
        self.main_class.dir_choice = None
        self.main_class.file_choice = None
        self.main_class.struct = []
        for x,y,z in os.walk(self.main_class.root):
            self.main_class.struct.append(x)
            self.main_class.struct.append(y)
            self.main_class.struct.append(z)
            break
        self.main_class.select_list_pos = [0,0]
        embed, view = await self.main_class.reload_message()
        await interaction.response.edit_message(embed = embed, view = view)

    @discord.ui.button(label="send file", style = discord.ButtonStyle.green)
    async def send_file(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.main_class.file_choice is None:
            return await interaction.response.send_message("You need to choose a file.")
        fp = os.path.join(self.main_class.root, self.main_class.file_choice)
        size = file_size(fp)
        if size >= 26214400:
            return await interaction.response.send_message("Too Big :hot_face:")
        else:
            print(fp)
            file = discord.File(fp)
            await interaction.response.defer()
            # await asyncio.sleep(3)
            return await interaction.followup.send(file=file)
            # return await interaction.response.send_message(file=file)
        
    @discord.ui.button(label="upload to Google Drive", style = discord.ButtonStyle.green)
    async def upload(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.main_class.file_choice is None:
            return await interaction.response.send_message("You need to choose a file.")
        fp = os.path.join(self.main_class.root, self.main_class.file_choice)
        shutil.copy(fp, self.main_class.upload_drive_root)
        return await interaction.response.send_message("uploading...")


async def setup(bot):
    await bot.add_cog(File(bot))


if __name__=="__main__":
    a = [1,2,3,4,5,6,7,8,9]
    print(split_for_num(a, 3))
    pass