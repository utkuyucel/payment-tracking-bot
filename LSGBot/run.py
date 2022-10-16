import os
import discord
import time
import pandas as pd
import requests as req
from datetime import datetime
from tabulate import tabulate
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord.ext import commands
from discord.utils import get


################################################################## AUTHENTICATION ##################################################################
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!',intents=intents)

TEXT = """
Selamlar.
Üyeliğinizin süresi maalesef doldu.
Üyeliğinize devam etmek veya üyelik durumunuzu güncellemek için lütfen @emrefx ile iletişime geçin.

(Uyarı: Bu otomatik bir mesajdır, cevap vermenize gerek yoktur.)
"""

DOWNGRADE_TEXT = """
Selamlar.
Grup üyeliğinizi yeniletmeniz için gerekli olan 1 haftalık süre bugün itibariyle maalesef dolmuştur.
Bu yüzden, @member üyelik yetkiniz alınmıştır. 
Üyeliğinize devam etmek veya üyelik durumunuzu güncellemek için lütfen @emrefx ile iletişime geçin.

(Uyarı: Bu otomatik bir mesajdır, cevap vermenize gerek yoktur.)
"""

admins = {
    "utku": 326790762517889034,
    "emrefx": 514075929862209567,
    }

GUILD_ID = 973207220953182280
    
def get_users_from_google():
    print("Getting data from google..")
    URL = "https://docs.google.com/spreadsheets/d/1thPwqNBytlqDEtFsylyyGi7upxN3eK2HeNtrh5OlbDc/edit#gid=0"
    URL = URL.replace("/edit#gid=", "/export?format=csv&gid=")
    example_df = pd.read_csv(URL, dtype = {"ID": str})
    filtered_df = example_df[["ID","Discord Name", "isExpired"]]
    expired_users = filtered_df["ID"][filtered_df.isExpired == "Yes"]
    expired_names = filtered_df["Discord Name"][filtered_df.isExpired == "Yes"]

    expired_list = [i for i in expired_users]
    expired_names_list = [i for i in expired_names]
    
    return expired_list, expired_names_list

def get_calendar_data(param: str) -> pd.DataFrame:
    URL = "https://api.fintables.com/macro/calendar/?type=json&params={%22currentTab%22:%22"+ param +"%22,%22timeZone%22:63}"

    x = req.get(URL)
    ret = x.json()

    df = pd.DataFrame(ret)
    ## Adapting dates
    df_important = df[["time","currency","provider_event_title", "forecast", "previous"]][df.importance == 3]
    df_important = df_important.rename(columns={'currency': 'cur', 'provider_event_title': 'title', 'forecast': 'for', 'previous': 'prev'})

    return df_important


def users_to_be_downgraded():
    URL = "https://docs.google.com/spreadsheets/d/1thPwqNBytlqDEtFsylyyGi7upxN3eK2HeNtrh5OlbDc/edit#gid=0"
    URL = URL.replace("/edit#gid=", "/export?format=csv&gid=")
    example_df = pd.read_csv(URL, dtype = {"ID": str})
    filtered_df = example_df[["ID","Discord Name", "Days Remaining", "isExpired"]]
    output_names = filtered_df[filtered_df["Days Remaining"] <= -7]["ID"]

    output_list = [i for i in output_names]
    return output_list


    

async def get_user_count_by_date():
    """
    A function that exports user count and today to a .csv file (appends data every running)
    """
    URL = "https://docs.google.com/spreadsheets/d/1thPwqNBytlqDEtFsylyyGi7upxN3eK2HeNtrh5OlbDc/edit#gid=0"
    URL = URL.replace("/edit#gid=", "/export?format=csv&gid=")
    df = pd.read_csv(URL, dtype = {"ID": str})
    now = datetime.now().strftime("%d-%m-%Y")
    user_count = df["Twitter Name"].count()

    data = {"date": [now], "user_count": [user_count]}

    df = pd.DataFrame(data = data)  
    df.to_csv("user_data.csv", mode = "a", index = False, header = False)

    print("Export done!\n")

async def msg_admin(inp_name: str, cant_send: list):
    _, name = get_users_from_google()
    num_name = len(name)
    admin = admins[inp_name]
    user = await bot.fetch_user(admin)
    
    everyone_ok_text = "Günaydın.\nBugün ödemesi gelen hiç kimse yok!\nBol kazançlı günler!"
    other_text = f"Günaydın.\nBugün ödemesi gelen {num_name} kişi var:\n{name}\nKendilerine bilgilendirme mesajı gönderildi."
    cant_send_text = f"{len(cant_send)} kişiye ulaşılamadı. Lütfen manuel mesaj atın:\n{cant_send}"
    
    print("Sendin msg to admins...")
    try:
        if (num_name == 0):
            await user.send(everyone_ok_text)
        else:
            if (len(cant_send) == 0):
                await user.send(other_text) 
            else:
                await user.send(other_text)
                await user.send(cant_send_text) 
    except:
        print("Exception")
        pass

async def msg_downgrade_to_admin(inp_name: str, downgraded: list):
    admin = admins[inp_name]
    user = await bot.fetch_user(admin)
    DOWNGRADED_TEST_SUCCESS = f"{len(downgraded)} kişinin @member rolü alındı.\n{downgraded}"
    DOWNGRADED_TEST_FAIL = "@member rolü alınan hiç kimse yok.."
    print("Sendin downgrade msg to admins...")
    try:
        if (len(downgraded) > 0):
            await user.send(DOWNGRADED_TEST_SUCCESS)
        else:
            await user.send(DOWNGRADED_TEST_FAIL)
    except:
        print("Exception")
        pass
################################################################## FUNCTIONS ##################################################################
    
@bot.event
async def func():
    print("Bot is running...")
    list_users, _ = get_users_from_google()
    cant_send = []
    
    # Kullanıcılara mesaj atma
    for i in list_users:
        user = await bot.fetch_user(i)
        
        try:
            await user.send(TEXT) 
            print("Sent: ", user)
            time.sleep(0.33)
        except:
            print(f"Can't send msg to: {user}")
            cant_send.append(user.name)
            pass
    
    time.sleep(1)
    await msg_admin("utku", cant_send)
    await msg_admin("emrefx", cant_send) 
    print("Done!")

@bot.event
async def calendar():
    channel_id = 1019662109346369586
    data = get_calendar_data("today")
    channel = bot.get_channel(channel_id)
    
    data = tabulate(data, numalign = "left", disable_numparse = True, headers = "keys", tablefmt="psql", stralign='center', showindex = False)
    out_text = """
    İyi günler. Bugünkü önemli veriler:
    ```{}```
    """.format(data)
    
    await channel.send(out_text)

    print("Calendar Done!")
    
################################################################## COMMANDS ####################################################################
@bot.command(name = "today")
async def test(ctx):
    data = get_calendar_data("today")
    data = tabulate(data, numalign = "left", disable_numparse = True, headers = "keys", tablefmt="psql", stralign='center', showindex = False)
    out_text = """
    Update:
    ```{}```
    """.format(data)
    await ctx.send(out_text)

@bot.command(name = "fedrate")
async def fedRate(ctx):
    URL = "https://markets.newyorkfed.org/read?productCode=50&eventCodes=500&limit=25&startPosition=0&sort=postDt:-1&format=xlsx"
    fed_rate = pd.read_excel(URL, usecols = ["Effective Date", "Rate (%)"], engine="openpyxl")
    fed_rate = fed_rate.rename(columns = {"Effective Date": "date", "Rate (%)": "rate"})
    out_text = fed_rate.head(1)
    out_text.style.hide_index()
    x, y = out_text.date, out_text.rate
    x, y = str(x.values[0]), str(y.values[0])
    
    classic_text = f"```{x} tarihi itibariyle FED Faiz oranı: {y}%\n```"
    await ctx.send(classic_text)

@bot.event
async def downgrade_users():
    """
    A function that downgrades users who have not renewed their membership
    """
    users = []
    print("Downgrading users..")
    guild = bot.get_guild(GUILD_ID)
    role = get(guild.roles, name = "member")

    users_to_be_downgraded_list = users_to_be_downgraded()
    
    if (len(users_to_be_downgraded_list) > 0):
        for user in users_to_be_downgraded_list:
            try:
                user = await guild.fetch_member(user)
    
                if (role in user.roles):
                    await user.remove_roles(role) 
                    await user.send(DOWNGRADE_TEXT) 
                    print(f"{user.name} has been downgraded!")
                    users.append(user.name)
                else:
                    print("User is already downgraded!")
            
            except:
                print(f"Exception: {user}")
                continue
            
    else:
        print("Henüz üyelik süresini aşan kullanıcı yok.")
        
    await msg_downgrade_to_admin("utku", users)
    await msg_downgrade_to_admin("emrefx", users)
    
    print("Downgrading done!\n")

################################################################## CRON JOBS ####################################################################
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    
     #initializing scheduler
    
    
    scheduler = AsyncIOScheduler()
    
    scheduler.add_job(get_user_count_by_date, CronTrigger(year="*", month="*", day="*", hour="3", minute="0"))
    scheduler.add_job(calendar, CronTrigger(year="*", month="*", day="*", hour="6", minute="0"))

    scheduler.add_job(func, CronTrigger(year="*", month="*", day="*", hour="8", minute="0"))
    scheduler.add_job(downgrade_users, CronTrigger(year="*", month="*", day="*", hour="8", minute="15"), max_instances=50)
    
    
    # scheduler.add_job(downgrade_users, CronTrigger(second="10, 20, 30, 40,50"), max_instances=50)
    #starting the scheduler
    scheduler.start()
    

## RUN ##
if __name__ == "__main__":
    bot.run(TOKEN)

