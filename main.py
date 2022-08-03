from discord.ext import commands

bot = commands.Bot(command_prefix='.')
bot.auth_key = "" # Insert your DeepL auth key here
token = "" # Insert your Discord bot key here

@bot.event
async def on_ready():
    """This function is run when the bot is first run and logged in."""
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    
    
if __name__ == "__main__":
    from os import listdir

    # Load any cogs in the cog directory
    print("Loading Cogs Please Wait...")
    for cog in listdir("cogs"):
        if(cog == "__pycache__"):
            pass
        else:
            bot.load_extension("cogs."+cog[:-3]) # :-3 to remove file extension (.py)

    print("Cogs Loaded, success!")
    bot.run(token)
    