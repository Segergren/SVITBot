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
intents = discord.Intents.default()
intents.members = True
credentials = open('credentials.txt').read().splitlines()

TOKEN = credentials[0]
STATUS = "rindi.com/svit"

bot = commands.Bot(command_prefix='!',intents=intents)
@bot.command(pass_context=True)

@bot.event
async def on_connect():
    print("Connected to Discord")

@bot.event
async def on_ready():
    print("Ready!")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=STATUS))
    
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(758712839975993438)
    welcomeMessage = await channel.send("Hej och välkommen " + member.name.replace("@","") + "!")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="Hej "  + member.name.replace("@","") + "!"))
    await asyncio.sleep(30)
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=STATUS))
    await welcomeMessage.delete()
    
@bot.event
async def on_raw_reaction_add(payload):
    if(payload.message_id == 758740542044504084):
        channel = await bot.fetch_channel(payload.channel_id)
        await channel.fetch_message(payload.message_id)
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
    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)

    if(str(member) != "SVIT#9050" and str(payload.emoji) == "<:votedone:801238564238000179>"):
        channel = await bot.fetch_channel(payload.channel_id)
        reactionMessage = await channel.fetch_message(payload.message_id)
        if("RÖSTNING" in reactionMessage.content and (channel.id == 801237039345172511 or channel.id == 760184150509879376)):
            yesReaction = reactionMessage.reactions[0].count
            noReaction = reactionMessage.reactions[1].count
            
            yesusers = await reactionMessage.reactions[0].users().flatten()
            nousers = await reactionMessage.reactions[1].users().flatten()
            votes = "__Röster__\n"
            for user in yesusers:
                if(user.display_name != "SVIT"):
                    votes = votes + "<:yes:801237811595575386> " + user.display_name + "\n"
            for user in nousers:
                if(user.display_name != "SVIT"):
                    votes = votes + "<:no:801237793073922069> " +user.display_name + "\n"
            votes = votes + "\n**RESULTAT**\n"
            
            if(yesReaction > noReaction):
                await reactionMessage.edit(content=reactionMessage.content.replace("<:inprogress:801223023939289099> *Denna omröstning är öppen!*", votes + "<:yes:801237811595575386> Förslaget fick ett **Ja** i omröstningen"))
            if(noReaction > yesReaction):
                await reactionMessage.edit(content=reactionMessage.content.replace("<:inprogress:801223023939289099> *Denna omröstning är öppen!*", votes + "<:no:801237793073922069> Förslaget fick ett **Nej** i omröstningen"))
            if(yesReaction == noReaction):
                chairmanVoteYes = None
                usersVotedNo = await reactionMessage.reactions[1].users().flatten()
                for user in usersVotedNo:
                    if(int(user.id) == 623491039726141451):
                        chairmanVoteYes = False
                if(chairmanVoteYes == None):
                    usersVotedYes = await reactionMessage.reactions[0].users().flatten()
                    if(int(user.id) == 623491039726141451):
                        chairmanVoteYes = True
                if(chairmanVoteYes == True):
                    await reactionMessage.edit(content=reactionMessage.content.replace("<:inprogress:801223023939289099> *Denna omröstning är öppen!*", votes + "<:yes:801237811595575386> Förslaget fick ett **Ja** i omröstningen"))
                    pass
                elif(chairmanVoteYes == False):
                    await reactionMessage.edit(content=reactionMessage.content.replace("<:inprogress:801223023939289099> *Denna omröstning är öppen!*", votes + "<:no:801237793073922069> Förslaget fick ett **Nej** i omröstningen"))
                    pass
                else:
                    await reactionMessage.edit(content=reactionMessage.content.replace("<:inprogress:801223023939289099> *Denna omröstning är öppen!*", "<:cancel:801237919469142016> Omröstningen kunde inte avslutas då det blev lika."))
                    pass
                   
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
        
    if ('!vote' in msg.content.lower() and ("svit elit" in [y.name.lower() for y in msg.author.roles])):
        messageFormatted = replace("!vote ","",msg.content,False)
        await msg.delete()
        stringBuilder = "━━━━━━━━━━━━━━━\n**RÖSTNING**\n" + messageFormatted + "\n\n<:inprogress:801223023939289099> *Denna omröstning är öppen!*\n━━━━━━━━━━━━━━━"
        sentMessage = await msg.channel.send(stringBuilder)
        await sentMessage.add_reaction(bot.get_emoji(801237811595575386))
        await sentMessage.add_reaction(bot.get_emoji(801237793073922069))
        await sentMessage.add_reaction(bot.get_emoji(801238564238000179))
    
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
