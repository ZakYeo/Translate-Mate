import discord
from discord.ext import commands
from discord.commands import Option
import asyncdeepl as deepl
from discord import Embed, Color
from langdetect import detect_langs
from requests import get
import easyocr
import shutil
import warnings
from os import remove

       
latin_reader = easyocr.Reader(["no","pl","ro","rs_latin","sq","sv","it","is","hr","az","bs","cs","cy","et", "hr",
"hu", "id", "lt", "lv", "mi", "nl", "pl", "pt", "sk", "sl", "sq", "tr"], verbose=False, gpu=True) # this needs to run only once to load the model into memory
warnings.filterwarnings("ignore", category=UserWarning) 


class Translator(commands.Cog):
    """
    Translation Discord Bot Cog
    """

    def __init__(self, bot): 
        self.bot = bot
        self.DETECTABLE_LANGS = {'af': 'Afrikaans', 'ar': 'Arabic', 'bg': 'Bulgarian', 'bn': 'Bengali', 'ca': 'Catalan, Valencian', 'cs': 'Czech', 'cy': 'Welsh', 'da': 'Danish',
            'de': 'German', 'el': 'Greek, Modern', 'en': 'English', 'es': 'Spanish, Castilian', 'et': 'Estonian', 'fa': 'Persian', 'fi': 'Finnish', 'fr': 'French', 'gu': 'Gujarati',
            'he': 'Hebrew', 'hi': 'Hindi', 'hr': 'Croatian', 'hu': 'Hungarian', 'id': 'Indonesian', 'it': 'Italian', 'ja': 'Japanese', 'kn': 'Kannada', 'ko': 'Korean',
            'lt': 'Lithuanian', 'lv': 'Latvian', 'mk': 'Macedonian', 'ml': 'Malayalam', 'mr': 'Marathi', 'ne': 'Nepali', 'nl': 'Dutch, Flemish', 'no': 'Norwegian', 'pa': 'Punjabi, Panjabi',
            'pl': 'Polish', 'pt': 'Portuguese', 'ro': 'Romanian', 'ru': 'Russian', 'sk': 'Slovak', 'sl': 'Slovenian', 'so': 'Somali', 'sq': 'Albanian', 'sv': 'Swedish',
            'sw': 'Swahili', 'ta': 'Tamil', 'te': 'Telugu', 'th': 'Thai', 'tl': 'Tagalog', 'tr': 'Turkish', 'uk': 'Ukranian', 'ur': 'Urdu', 'vi': 'Vietnamese',
            'zh-cn': 'Chinese (Simplified)', 'zh-tw': 'Chinese (Traditional)'} 
        self.TRANSLATABLE_LANGS = {'Bulgarian': 'BG', 'Czech': 'CS', 'Danish': 'DA', 'German': 'DE', 'Greek': 'EL', 'English (British)': 'EN-GB', 'English': 'EN-US', 'Spanish':'ES',
            'Estonian': 'ET', 'Finnish': 'FI', 'French': 'FR', 'Hungarian': 'HU', 'Indonesian': 'ID', 'Italian': 'IT', 'Japanese': 'JA', 'Lithuanian': 'LT', 'Latvian': 'LV', 'Dutch': 'NL',
            'Polish': 'PL', 'Portuguese (Brazilian)': 'PTBR', 'Romanian': 'RO', 'Russian': 'RU', 'Slovak': 'SK',
            'Slovenian': 'SL', 'Swedish': 'SV', 'Turkish': 'TR', 'Chinese': 'ZH',}
        self.SWAPPED_TRANS_LANGS = dict([(value, key) for key, value in self.TRANSLATABLE_LANGS.items()])
        self.img_handler = ImageHandler()
    
    @discord.slash_command(name="translate", description="Translate text!")
    async def translate_command(self,
        ctx,
        text_original: Option(str, "Enter the text you wish to translate", required=True),
        language: Option(str, "Select The Language To Translate To (Blank for English-GB)",
        choices=['Bulgarian', 'Czech', 'Danish', 'German', 'Greek', 'English', 
        'Spanish', 'Estonian', 'Finnish', 'French', 'Hungarian', 'Indonesian', 'Italian', 'Japanese',
        'Lithuanian', 'Dutch', 'Polish','Romanian', 'Russian', 'Slovak',
        'Slovenian', 'Swedish', 'Turkish', 'Chinese'], 
        required=False)
    ):
        """
        Translation Slash Command
        Takes some string of characters, and will translate said string into the desired language
        """
        if(language is not None):
            choice = self.TRANSLATABLE_LANGS[language]
        else:
            choice = "EN-US" # Default choice

        await ctx.respond(embed=await self.handle_translation(choice, text_original), ephemeral=True)

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
            embed.add_field(name=self.DETECTABLE_LANGS[lang.lang], value="{:.2f}%".format(float(lang.prob)*100))

        await ctx.respond(embed=embed, ephemeral=True)   

    @discord.message_command(name="Extract Image Text")
    async def image_to_text_command(self, ctx, message: discord.Message):
        """
        Image To Text Slash Command
        Extracts any text from an image and sends it as a message.
        By default, it will assume the language of the image is from a pre-defined set of latin script languages
        The user can change this language to something specific using Discord's dropdown selection
        e.g Russian
        """
        await ctx.defer(ephemeral=True)
        text = await self.img_handler.message_images_to_text(message)
        await ctx.respond(embed=await self.img_handler.create_embed(text), ephemeral=True, view=DropdownView(self.bot,1,message))  

    async def handle_translation(self, choice, text_original):
        """Handle translation of text and returns an embed"""
        status, text_translated = await deepl.translate(self.bot.auth_key, choice, text_original)
        
        if status == 200: # 200 = OK
            embed = Embed(title="{} to {}".format(self.SWAPPED_TRANS_LANGS[text_translated["translations"][0]["detected_source_language"]],self.SWAPPED_TRANS_LANGS[choice])
                        ,description="", color=Color.green())
            embed.add_field(name="Original Text", value=text_original)
            embed.add_field(name="Translated Text", value=text_translated["translations"][0]["text"])
        else: # Non-200 Response Handling
            embed = Embed(title="Error {}".format(status), description=text_translated["message"],
            color=Color.red())
    
        
        return embed

class Dropdown(discord.ui.Select):
    """
    Dropdown Selection
    Holds the list of possible languages available to be used for image extraction
    The final option in the selection is always a "next page" option, cycling to the beginning after page 4
    """
    def __init__(self, bot_: discord.Bot, page: int, original_msg: discord.Message):
        self.bot = bot_
        self.page = page
        self.original_msg = original_msg
        self.OCR_LANGS = {'Abaza': 'abq', 'Adyghe': 'ady', 'Afrikaans': 'af', 'Angika': 'ang', 'Arabic': 'ar', 'Assamese': 'as', 'Avar': 'ava', 'Azerbaijani': 'az', 'Belarusian': 'be', 'Bulgarian': 'bg', 'Bihari': 'bh', 'Bhojpuri': 'bho', 'Bengali': 'bn', 'Bosnian': 'bs', 'Simplified Chinese': 'ch_sim', 'Traditional Chinese': 'ch_tra', 'Chechen': 'che', 'Czech': 'cs', 'Welsh': 'cy', 'Danish': 'da', 'Dargwa': 'dar', 'German': 'de', 'English': 'en', 'Spanish': 'es', 'Estonian': 'et', 'Persian (Farsi)': 'fa', 'French': 'fr', 'Irish': 'ga', 'Goan Konkani': 'gom', 'Hindi': 'hi', 'Croatian': 'hr', 'Hungarian': 'hu', 'Indonesian': 'id', 'Ingush': 'inh', 'Icelandic': 'is', 'Italian': 'it', 'Japanese': 'ja', 'Kabardian': 'kbd', 'Kannada': 'kn', 'Korean': 'ko', 'Kurdish': 'ku', 'Latin': 'la', 'Lak': 'lbe', 'Lezghian': 'lez', 'Lithuanian': 'lt', 'Latvian': 'lv', 'Magahi': 'mah', 'Maithili': 'mai', 'Maori': 'mi', 'Mongolian': 'mn', 'Marathi': 'mr', 'Malay': 'ms', 'Maltese': 'mt', 'Nepali': 'ne', 'Newari': 'new', 'Dutch': 'nl', 'Norwegian': 'no', 'Occitan': 'oc', 'Pali': 'pi', 'Polish': 'pl', 'Portuguese': 'pt', 'Romanian': 'ro', 'Russian': 'ru', 'Serbian (cyrillic)': 'rs_cyrillic', 'Serbian (latin)': 'rs_latin', 'Nagpuri': 'sck', 'Slovak': 'sk', 'Slovenian': 'sl', 'Albanian': 'sq', 'Swedish': 'sv', 'Swahili': 'sw', 'Tamil': 'ta', 'Tabassaran': 'tab', 'Telugu': 'te', 'Thai': 'th', 'Tajik': 'tjk', 'Tagalog': 'tl', 'Turkish': 'tr', 'Uyghur': 'ug', 'Ukranian': 'uk', 'Urdu': 'ur', 'Uzbek': 'uz', 'Vietnamese': 'vi'}
 
        options = [
            discord.SelectOption(label=lang, description="Select this language") for lang in self.OCR_LANGS.keys()
        ]
        
        if(page == 1):
            options = options[0:24]
            label = "More? Select for page 2"
        elif(page == 2):
            options = options[25:49]
            label = "More? Select for page 3"
        elif(page == 3):
            options = options[50:74]
            label = "More? Select for page 4"
        elif(page == 4):
            options = options[75:83]
            label = "Back to beginning?"

        options.append(discord.SelectOption(label=label,value="pageplus", description="Select this language"))
        super().__init__(
            placeholder="Select A Language",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        """
        Called once a selection has been made by the user.
        Will either cycle to the next page, or change the extraction language
        """
        selection = self.values[0]
        if(selection == "pageplus"):
            if(self.page == 4):
                self.page = 0
            await interaction.response.edit_message(view=DropdownView(self.bot, self.page+1,self.original_msg))
        else:

            await interaction.response.edit_message(embed=Embed(title="Image Text Extraction", description="Extracting text, please wait..."))

            img_handler = ImageHandler()
            text = await img_handler.message_images_to_text(self.original_msg,self.OCR_LANGS[selection])

            await interaction.edit_original_message(embed=await img_handler.create_embed(text))

class DropdownView(discord.ui.View):
    """Defines a simple View that allows the user to use the Select menu."""
    def __init__(self, bot_: discord.Bot, page: int, original_msg: discord.Message):
        self.bot = bot_
        super().__init__()
        self.page = page
        self.original_msg = original_msg

        # Adds the dropdown to our View object
        self.add_item(Dropdown(self.bot, self.page, self.original_msg))


class ImageHandler():

    def __init__(self):
        self.IMAGE_FILE_EXTENSIONS = ["jpg", "jpeg", "png", "webp", "tiff"]
    async def image_to_text(self, url, reader=None):
        """Extracts the text from an image url"""

        is_image = await self.verify_image(url)
        if(not is_image):
            return ""

        r = get(url, stream = True)
        filename = url.split("/")[-1] # Grab the filename (last part of the url)


        # Check if the image was retrieved successfully
        if r.status_code == 200:
            # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
            r.raw.decode_content = True
            
            # Open a local file with wb ( write binary ) permission.
            with open(r"images/"+filename,'wb') as f:
                shutil.copyfileobj(r.raw, f)
                
        else:
            r.raise_for_status() # Raise an exception for 4xx and 5xx response codes
        if(reader is None):
            result = latin_reader.readtext("images/"+filename, detail=0)
        else:
            result = easyocr.Reader([reader], gpu=True).readtext("images/"+filename, detail=0)
        
        remove("images/"+filename) # Delete the file -> no longer needed
        return result  

    async def message_images_to_text(self, message, reader=None):
        """Loops through the embeds and attachments of a discord message and extracts the text"""
        text = []
        for embed in message.embeds:
            if(reader is None):
                text.append(await self.image_to_text(embed.url))
            else:
                text.append(await self.image_to_text(embed.url, reader))
        
        for attachment in message.attachments:
            if(reader is None):
                text.append(await self.image_to_text(attachment.url))
            else:
                text.append(await self.image_to_text(attachment.url, reader))  
        return text   

    async def create_embed(self, text):
        """Generates the embedded messages used for a response"""

        if(len(text) == 1):
            embed = Embed(title="Image Text Extraction",description=" ".join(text[0]), color=Color.green())
            embed.set_footer(text="\n\nExpected a different output? Want a more accurate result? Select the specific language below and retry")

        elif(len(text) > 1):
            embed = Embed(title="Image Text Extraction",description="", color=Color.green())
            for extraction in text:
                embed.add_field(name="Extraction", value=" ".join(extraction))
        else:
            embed = Embed(title="Unable To Perform Extraction",description="", color=Color.red())

        return embed
    
    async def verify_image(self, url):
        """Verifies a url by checking the file extension"""
        for file_extension in self.IMAGE_FILE_EXTENSIONS:
            if(url.endswith(file_extension)):
                return True
        return False



def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Translator(bot)) # add the cog to the bot