import aiohttp

API_URL = r"https://api-free.deepl.com/v2/"

async def get_usage(key):
    data={
            "auth_key": key,
        }
    async with aiohttp.ClientSession() as session:
        async with session.get(API_URL+'usage', params=data) as resp:
            text = await resp.json()
            return (resp.status, text)

async def translate(key, lang, text):
    data= {
        "target_lang": lang,
        "auth_key": key,
        "text": text,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(API_URL+'translate', params=data) as resp:
            text = await resp.json()
            return (resp.status, text)
