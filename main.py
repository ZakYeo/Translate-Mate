import asyncdeepl as deepl
from discord.ext import commands, tasks
from discord.commands import Option
from discord import Embed, Color

bot = commands.Bot(command_prefix='.')
bot.auth_key = ""


@bot.event
async def on_ready():
    """This function is run when the bot is first run and logged in."""
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.slash_command(name="translate", description="Translate text!")
async def translate(
    ctx,
    text_original: Option(str, "Enter the text you wish to translate", required=True),
    language: Option(str, "Select The Language To Translate To (Blank for English-GB)",choices=["en-gb","de","fr"], required=False)
    ):
    if language is None:
        language = "en-gb"
    status, text_translated = await deepl.translate(bot.auth_key, language, text_original)
    embed = Embed(title="{} to {}".format(text_translated["translations"][0]["detected_source_language"],language)
                  ,description="", color=Color.green())
    embed.add_field(name="Original Text", value=text_original)
    embed.add_field(name="Translated Text", value=text_translated["translations"][0]["text"])
    await ctx.respond(embed=embed)

@bot.slash_command(name="usage", description="Check usage remaining!")
async def usage(ctx):
    status, text = await deepl.get_usage(bot.auth_key)
    embed = Embed(title="DeepL's API Usage Statistics",description="", color=Color.green())
    embed.add_field(name="Character Count", value=text["character_count"])
    embed.add_field(name="Character Limit", value=text["character_limit"])

    await ctx.respond(embed=embed)
    
if __name__ == "__main__":
    bot.run("")