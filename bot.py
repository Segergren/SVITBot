import discord
from discord import File
import discord.utils
from discord.utils import get
import requests
import sys
from discord.ext import commands
import asyncio
import os
import re
from io import BytesIO
import xlsxwriter
from datetime import datetime
intents = discord.Intents.default()
intents.members = True
credentials = open('credentials.txt').read().splitlines()

TOKEN = credentials[0]

bot = commands.Bot(command_prefix='!',intents=intents)
@bot.command(pass_context=True)

@bot.event
async def on_connect():
    print("Connected to Discord")

@bot.event
async def on_ready():
    print("Ready!")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="rindi.com/svit"))
    
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(758712839975993438)
    welcomeMessage = await channel.send("Hej och välkommen " + member.name.replace("@","") + "!")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="Hej "  + member.name.replace("@","") + "!"))
    await asyncio.sleep(30)
    await bot.change_presence(activity=discord.Activity())
    await welcomeMessage.delete()
    
@bot.event
async def on_raw_reaction_add(payload):
    if(payload.message_id == 758740542044504084):
        channel = await bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        emoji = payload.emoji
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        
        if(str(emoji) == '1️⃣'):
            role = discord.utils.get(guild.roles, name="År 1")
            await member.add_roles(role, reason="År 1")
            print("Added " + member.name + " to år 1")
        if(str(emoji) == '2️⃣'):
            role = discord.utils.get(guild.roles, name="År 2")
            await member.add_roles(role, reason="År 2")
            print("Added " + member.name + " to år 2")
        if(str(emoji) == '3️⃣'):
            role = discord.utils.get(guild.roles, name="År 3")
            await member.add_roles(role, reason="År 3")
            print("Added " + member.name + " to år 3")
@bot.event
async def on_raw_reaction_remove(payload):
    if(payload.message_id == 758740542044504084):
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        emoji = payload.emoji
        
        if(emoji.name == '1️⃣'):
            role = discord.utils.get(guild.roles, name="År 1")
            await member.remove_roles(role, reason="År 1")
            print("Removed " + member.name + " from år 1")
        if(emoji.name == '2️⃣'):
            role = discord.utils.get(guild.roles, name="År 2")
            await member.remove_roles(role, reason="År 2")
            print("Removed " + member.name + " from år 2")
        if(emoji.name == '3️⃣'):
            role = discord.utils.get(guild.roles, name="År 3")
            await member.remove_roles(role, reason="År 3")
            print("Removed " + member.name + " from år 3")
    
async def analyzeNSFW(msg):
    try:
        api_key = credentials[1]
        api_secret = credentials[2]

        response = requests.get(
            'https://api.imagga.com/v2/categories/nsfw_beta?image_url=' + msg.attachments[0].url,
            auth=(api_key, api_secret))

        obj = response.json()
        print("Checking...")
        for categorie in obj["result"]["categories"]:
            print(categorie["name"]["en"])
            if('nsfw' in categorie["name"]["en"]):
                print("NSFW: " + str(categorie["confidence"]))
                if(int(categorie["confidence"]) > 60):
                    await msg.delete()
                    
    except Exception as ex:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
    
@bot.event
async def on_message(msg):
    if(len(msg.attachments) > 0):
        print(msg.attachments[0].filename)
        print("--")
        print("Starting NSFW check")
        loopNSFW = asyncio.get_event_loop()
        loopNSFW.create_task(analyzeNSFW(msg))

    if ('!file' in msg.content.lower() and ("svit elit" in [y.name.lower() for y in msg.author.roles])):
        files = []
        for file in msg.attachments:
            fp = BytesIO()
            await file.save(fp)
            files.append(discord.File(fp, filename=file.filename, spoiler=file.is_spoiler()))
        await msg.channel.send(files=files)
        await msg.delete()
    
    if ('!say' in msg.content.lower() and ("svit elit" in [y.name.lower() for y in msg.author.roles])):
        await msg.channel.send(replace("!say","",msg.content,False))
        if(len(msg.attachments) > 0):
            files = []
            for file in msg.attachments:
                fp = BytesIO()
                await file.save(fp)
                files.append(discord.File(fp, filename=file.filename, spoiler=file.is_spoiler()))
            await msg.channel.send(files=files)
        await msg.delete()
        
    if ('!edit' in msg.content.lower() and ("svit elit" in [y.name.lower() for y in msg.author.roles])):
        channel = msg.channel
        message = await channel.fetch_message(msg.content.lower().split(" ")[1])
        await message.edit(content=replace("!edit ","", msg.content, False).replace(msg.content.lower().split(" ")[1], ""))
        await msg.delete()
        
    if ('!remove' in msg.content.lower() and ("svit elit" in [y.name.lower() for y in msg.author.roles])):
        channel = msg.channel
        message = await channel.fetch_message(msg.content.lower().split(" ")[1])
        await message.delete()
        await msg.delete()

    if ('!emergency' in msg.content.lower() and ("svit elit" in [y.name.lower() for y in msg.author.roles])):
        await bot.close()

def replace(old, new, str, caseinsentive = False):
    if caseinsentive:
        return str.replace(old, new)
    else:
        return re.sub(re.escape(old), new, str, flags=re.IGNORECASE)
    
bot.run(TOKEN)
