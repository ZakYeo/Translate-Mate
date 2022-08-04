import discord
from discord.ext import commands
from discord.commands import Option
import asyncdeepl as deepl
from discord import Embed, Color
from langdetect import detect_langs

class Translator(commands.Cog):
    """
    Translation Discord Bot Cog
    """

    def __init__(self, bot): 
        self.bot = bot
        self.LANGS = {'af': 'Afrikaans', 'ar': 'Arabic', 'bg': 'Bulgarian', 'bn': 'Bengali', 'ca': 'Catalan, Valencian', 'cs': 'Czech', 'cy': 'Welsh', 'da': 'Danish',
            'de': 'German', 'el': 'Greek, Modern', 'en': 'English', 'es': 'Spanish, Castilian', 'et': 'Estonian', 'fa': 'Persian', 'fi': 'Finnish', 'fr': 'French', 'gu': 'Gujarati',
            'he': 'Hebrew', 'hi': 'Hindi', 'hr': 'Croatian', 'hu': 'Hungarian', 'id': 'Indonesian', 'it': 'Italian', 'ja': 'Japanese', 'kn': 'Kannada', 'ko': 'Korean',
            'lt': 'Lithuanian', 'lv': 'Latvian', 'mk': 'Macedonian', 'ml': 'Malayalam', 'mr': 'Marathi', 'ne': 'Nepali', 'nl': 'Dutch, Flemish', 'no': 'Norwegian', 'pa': 'Punjabi, Panjabi',
            'pl': 'Polish', 'pt': 'Portuguese', 'ro': 'Romanian', 'ru': 'Russian', 'sk': 'Slovak', 'sl': 'Slovenian', 'so': 'Somali', 'sq': 'Albanian', 'sv': 'Swedish',
            'sw': 'Swahili', 'ta': 'Tamil', 'te': 'Telugu', 'th': 'Thai', 'tl': 'Tagalog', 'tr': 'Turkish', 'uk': 'Ukranian', 'ur': 'Urdu', 'vi': 'Vietnamese',
            'zh-cn': 'Chinese (Simplified)', 'zh-tw': 'Chinese (Traditional)'} 
    
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
        await ctx.respond(embed=embed, ephemeral=True)

    @discord.slash_command(name="usage", description="Check usage remaining!")
    async def usage(self, ctx):
        """
        Usage Slash Command
        Returns the current usage statistics of the DeepL API
        """
        status, text = await deepl.get_usage(self.bot.auth_key)
        if status == 200: # 200 = OK
            embed = Embed(title="DeepL's API Usage Statistics",description="", color=Color.green(), ephemeral=True)
            embed.add_field(name="Character Count", value=text["character_count"])
            embed.add_field(name="Character Limit", value=text["character_limit"])
        else: # Non-200 Response Handling
            embed = Embed(title="Error {}".format(status), description=text["message"],
            color=Color.red())

        await ctx.respond(embed=embed, ephemeral=True)

    
    @discord.slash_command(name="detect", description="Detect a language!")
    async def detect(self,
        ctx,
        text: Option(str, "Enter the text you wish to detect the language of", required=True)
    ):
        """
        Detect Slash Command
        Detects a language from a given string and returns the detected language
        """

        detected_langs = detect_langs(text)

        embed = Embed(title="Here Are My Confidence Levels Of The Detected Language"
                        ,description="", color=Color.green())
        for lang in detected_langs:
            embed.add_field(name=self.LANGS[lang.lang], value="{:.2f}%".format(float(lang.prob)*100))

        await ctx.respond(embed=embed, ephemeral=True)        



def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Translator(bot)) # add the cog to the bot