import discord
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    
@client.event
async def on_message(message):
    id = message.author.id
    user = await client.fetch_user(id)
    try:
        await user.send("Hello there!")
    except:
        print("Exception")
        pass

client.run(TOKEN)


## Azure cloud üzerinden botu çalıştırabiliriz. Free credit var ve hem de öğrenmiş olurum.