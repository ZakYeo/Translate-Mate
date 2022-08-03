import discord
from discord.ext import commands
from discord.commands import Option
import asyncdeepl as deepl
from discord import Embed, Color

class Translator(commands.Cog):
    """
    Translation Discord Bot Cog
    """

    def __init__(self, bot): 
        self.bot = bot
    
    @discord.slash_command(name="translate", description="Translate text!")
    async def translate(self,
        ctx,
        text_original: Option(str, "Enter the text you wish to translate", required=True),
        language: Option(str, "Select The Language To Translate To (Blank for English-GB)",choices=["en-gb","de","fr"], required=False)
        ):
        """
        Translation Slash Command
        Takes some string of characters, and will translate said string into the desired language
        """

        status, text_translated = await deepl.translate(self.bot.auth_key, language, text_original)

        if status == 200: # 200 = OK
            embed = Embed(title="{} to {}".format(text_translated["translations"][0]["detected_source_language"],language)
                        ,description="", color=Color.green())
            embed.add_field(name="Original Text", value=text_original)
            embed.add_field(name="Translated Text", value=text_translated["translations"][0]["text"])
        else: # Non-200 Response Handling
            embed = Embed(title="Error {}".format(status), description=text_translated["message"],
            color=Color.red())
        await ctx.respond(embed=embed)

    @discord.slash_command(name="usage", description="Check usage remaining!")
    async def usage(self, ctx):
        """
        Usage Slash Command
        Returns the current usage statistics of the DeepL API
        """
        status, text = await deepl.get_usage(self.bot.auth_key)
        if status == 200: # 200 = OK
            embed = Embed(title="DeepL's API Usage Statistics",description="", color=Color.green())
            embed.add_field(name="Character Count", value=text["character_count"])
            embed.add_field(name="Character Limit", value=text["character_limit"])
        else: # Non-200 Response Handling
            embed = Embed(title="Error {}".format(status), description=text["message"],
            color=Color.red())

        await ctx.respond(embed=embed)



def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Translator(bot)) # add the cog to the bot