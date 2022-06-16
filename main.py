import asyncdeepl as deepl
from discord.ext import commands, tasks
import discord
from discord.commands import Option

bot = commands.Bot(command_prefix='.', debug_guilds=[])
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
    text: Option(str, "Enter the text you wish to translate", required=True),
    language: Option(str, "Select The Language To Translate To (Blank for English-GB)",choices=["en-gb","de","fr"], required=False)
    ):
    if language is None:
        language = "en-gb"
    status, text = await deepl.translate(bot.auth_key, language, text)
    await ctx.respond(text)

@bot.slash_command(name="usage", description="Check usage remaining!")
async def usage(ctx):
    status, text = await deepl.get_usage(bot.auth_key)
    await ctx.respond(text)
    
if __name__ == "__main__":
    bot.run("")