import os
import discord
import time
import pandas as pd
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger


## AUTHENTICATION ##
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

TEXT = """
Selamlar!,
Üyeliğinizin süresi bu gün itibariyle maalesef doldu.
Üyeliğinizee devam etmek veya üyelik durumunuzu güncellemek için lütfen @emrefx ile iletişime geçin.

(Not: Bu otomatik bir mesajdır, cevap vermenize gerek yoktur.)
"""

admins = {
    "utku": 326790762517889034,
    "emrefx": 514075929862209567,
    }

    
def get_users_from_google():
    URL = "https://docs.google.com/spreadsheets/d/1thPwqNBytlqDEtFsylyyGi7upxN3eK2HeNtrh5OlbDc/edit#gid=0"
    URL = URL.replace("/edit#gid=", "/export?format=csv&gid=")
    example_df = pd.read_csv(URL)
    filtered_df = example_df[["ID","Discord Name", "isExpired"]]
    expired_users = filtered_df["ID"][filtered_df.isExpired == "Yes"]
    expired_names = filtered_df["Discord Name"][filtered_df.isExpired == "Yes"]

    expired_list = [i for i in expired_users]
    expired_names_list = [i for i in expired_names]
    
    return expired_list, expired_names_list

async def msg_admin(inp_name: str):
    _, name = get_users_from_google()
    num_name = len(name)
    admin = admins[inp_name]
    user = await client.fetch_user(admin)
    print("user")
    try:
        await user.send(
            f"Günaydın.\nBugün ödemesi gelen {num_name} kişi var:\n{name}\nKendilerine bilgilendirme mesajı gönderildi."
            )
    except:
        print("Exception")
        pass

## FUNCTIONS ##
    
@client.event
async def func():
    print("Bot is running...")
    list_users, _ = get_users_from_google()
    
    # Kullanıcılara mesaj atma
    for i in list_users:
        user = await client.fetch_user(i)
        
        try:
            await user.send(TEXT)
        except:
            print("Exception")
            pass
    
    time.sleep(1)
    await msg_admin("utku")
    await msg_admin("emrefx")

## EVENTS ##
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    
     #initializing scheduler
    scheduler = AsyncIOScheduler()
    
    #sends "s!t" to the channel when time hits 10/20/30/40/50/60 seconds, like 12:04:20 PM
    scheduler.add_job(func, CronTrigger(year="*", month="*", day="*", hour="11", minute="0", second="0")) 

    #starting the scheduler
    scheduler.start()


## RUN ##
if __name__ == "__main__":
    client.run(TOKEN)
