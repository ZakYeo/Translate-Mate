from discord.ext import commands

bot = commands.Bot(command_prefix='.', debug_guilds=[985963144335736902])
bot.auth_key = "ed656863-f2ce-4b89-b8be-0b55a9f10ff0:fx" # Insert your DeepL auth key here
token = "OTIwNjgyMjczNzAyMDM1NDY2.Ybn6Lw.6ZoAL1TCX30XCnDWqpiqtyQc1pU" # Insert your Discord bot key here


@bot.event
async def on_ready():
    """This function is run when the bot is first run and logged in."""
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    
    
if __name__ == "__main__":
    from os import listdir
    import warnings
    warnings.filterwarnings("ignore", category=UserWarning) 
    
    # Load any cogs in the cog directory
    print("Loading Cogs Please Wait...")
    for cog in listdir("cogs"):
        if(cog == "__pycache__"):
            pass
        else:
            bot.load_extension("cogs."+cog[:-3]) # :-3 to remove file extension (.py)

    print("Cogs Loaded, success!")
    bot.run(token)
    