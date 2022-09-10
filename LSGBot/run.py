import os
import discord
import time
import datetime
import pandas as pd
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord import DMChannel

## AUTHENTICATION ##
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

TEXT = """
Selam bro,
Üyeliğinin süresi bu gün itibariyle maalesef doldu.
Üyeliğine devam etmek veya üyelik durumunu güncellemek için lütfen @emrefx ile iletişime geç.

"""


## FLOW ##  
def get_users_from_google():
    URL = "https://docs.google.com/spreadsheets/d/1aDv2wWxeJrGViqDeDCC5OsAKv2VDzX9PXzjWdOznUfQ/edit#gid=0"
    URL = URL.replace("/edit#gid=", "/export?format=csv&gid=")
    example_df = pd.read_csv(URL)
    filtered_df = example_df[["ID","Discord Name", "isExpired"]]
    expired_users = filtered_df["ID"][filtered_df.isExpired == "Yes"]
    expired_lists = [user for user in expired_users]
    return expired_lists
    

## FUNCTIONS ##
    
@client.event
async def func():
    print("Hello world!")
    list_users = get_users_from_google()
    
    # Kullanıcılara mesaj atma
    for i in list_users:
        user = await client.fetch_user(i)
        
        try:
            await user.send(TEXT)
        except:
            print("Exception")
            pass

## EVENTS ##
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    
     #initializing scheduler
    scheduler = AsyncIOScheduler()
    
    #sends "s!t" to the channel when time hits 10/20/30/40/50/60 seconds, like 12:04:20 PM
    scheduler.add_job(func, CronTrigger(second="0, 10, 20, 30, 40, 50")) 

    #starting the scheduler
    scheduler.start()
    
    
    
@client.event
async def on_message(message):
    id = message.author.id
    user = await client.fetch_user(id)

    try:
        await user.send(f"Hey, {current_time}")
    except:
        print("Exception")
        pass



## RUN ##
if __name__ == "__main__":
    client.run(TOKEN)
    



