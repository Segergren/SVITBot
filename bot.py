import discord
import discord.utils
from discord.utils import get
from discord.ext import commands
import asyncio
import re
from io import BytesIO
intents = discord.Intents.default()
intents.members = True
credentials = open('C:/Users/database/Desktop/SVIT/credentials.txt').read().splitlines()

TOKEN = credentials[0]
STATUS = "rindi.com/svit"
CHAIRMAN_DISCORD_ID = 623491039726141451
VOTE_CURRENTLY_OPEN = "<:inprogress:801223023939289099> *Denna omröstning är öppen!*"
VOTE_YES = "<:yes:801237811595575386> Förslaget fick ett **Ja** i omröstningen"
VOTE_NO = "<:no:801237793073922069> Förslaget fick ett **Nej** i omröstningen"
VOTE_CANCELED = "<:cancel:801237919469142016> Omröstningen kunde inte avslutas då det blev lika."
WELCOME_MESSAGE_ID = 758740542044504084
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
async def on_raw_reaction_remove(payload):   
    #Tar bort en användares roll.
    if(payload.message_id == WELCOME_MESSAGE_ID):
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

@bot.event
async def on_raw_reaction_add(payload):
    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)

    #Lägger till en användares roll
    if(payload.message_id == WELCOME_MESSAGE_ID):
        emoji = payload.emoji
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

    #Om en SVIT-medlem har klickat på VOTERING AVSLUTAT-emojin
    if(str(member) != "SVIT#9050" and str(payload.emoji) == "<:votedone:801238564238000179>"):
        channel = await bot.fetch_channel(payload.channel_id)
        reaction_message = await channel.fetch_message(payload.message_id)
        acceptable_channels = [801237039345172511,760184150509879376,760100589627244546,763762846584537110]
        if("RÖSTNING" in reaction_message.content and (channel.id in acceptable_channels)):
            print("Giltig röstning")
            #Röstningsresultat
            yes_reactions = reaction_message.reactions[0].count
            no_reactions = reaction_message.reactions[1].count
            
            #Skriver ut vad personer har röstat på (Till votesTextBuilder)
            yes_users = await reaction_message.reactions[0].users().flatten()
            no_users = await reaction_message.reactions[1].users().flatten()
            votes_text_builder = "__Röster__\n"
            for user in yes_users:
                if(user.display_name != "SVIT"):
                    votes_text_builder = votes_text_builder + "<:yes:801237811595575386> " + user.display_name + "\n"
            for user in no_users:
                if(user.display_name != "SVIT"):
                    votes_text_builder = votes_text_builder + "<:no:801237793073922069> " +user.display_name + "\n"
            votes_text_builder = votes_text_builder + "\n**RESULTAT**\n"
            bot_votes = 2
            
            #Kontrollerar att 4 eller fler har röstat
            if((yes_reactions + no_reactions - bot_votes) >= 4):

                #Ändrar resultatet till JA
                if(yes_reactions > no_reactions):
                    await reaction_message.edit(content=reaction_message.content.replace(VOTE_CURRENTLY_OPEN, votes_text_builder + VOTE_YES))
                
                #Ändrar resultatet till NEJ
                if(no_reactions > yes_reactions):
                    await reaction_message.edit(content=reaction_message.content.replace(VOTE_CURRENTLY_OPEN, votes_text_builder + VOTE_NO))
                
                #Om rösterna är lika så kollar botten om ordförande har röstat. Isåfall är det ordförandes röst som vinner 
                #TODO: Förbättra denna funktion.
                if(yes_reactions == no_reactions): 
                    chairman_vote_yes = None
                    users_voted_no = await reaction_message.reactions[1].users().flatten()
                    
                    #Kontrollerar om ordförande har röstat NEJ
                    for user in users_voted_no:
                        if(int(user.id) == CHAIRMAN_DISCORD_ID):
                            chairman_vote_yes = False
                    
                    if(chairman_vote_yes == None):
                        #Kontrollerar om ordförande har röstat JA
                        users_voted_yes = await reaction_message.reactions[0].users().flatten()
                        for user in users_voted_yes:
                            if(int(user.id) == CHAIRMAN_DISCORD_ID):
                                chairman_vote_yes = True

                    #Ändra resultatet beroende på vad ordförande röstade på
                    if(chairman_vote_yes == True):
                        await reaction_message.edit(content=reaction_message.content.replace(VOTE_CURRENTLY_OPEN, votes_text_builder + VOTE_YES))
                    elif(chairman_vote_yes == False):
                        await reaction_message.edit(content=reaction_message.content.replace(VOTE_CURRENTLY_OPEN, votes_text_builder + VOTE_NO))
                    else:
                        await reaction_message.edit(content=reaction_message.content.replace(VOTE_CURRENTLY_OPEN, VOTE_CANCELED))
            else:
                #Om färre än 4 personer har röstat
                not_enough_votes_message = await channel.send("<:no:801237793073922069> Minst 4 personer måste delta i en votering.")
                await asyncio.sleep(3)
                await not_enough_votes_message.delete()
                   
@bot.event
async def on_message(msg):
    #Skicka en fil som BOTTEN
    if ('!file' in msg.content.lower() and ("svit elit" in [y.name.lower() for y in msg.author.roles])):
        files = []
        for file in msg.attachments:
            fp = BytesIO()
            await file.save(fp)
            files.append(discord.File(fp, filename=file.filename, spoiler=file.is_spoiler()))
        await msg.channel.send(files=files)
        await msg.delete()
        
    #Starta en votering
    if ('!vote' in msg.content.lower() and ("svit elit" in [y.name.lower() for y in msg.author.roles])):
        message_formatted = replace("!vote ","",msg.content,False)
        await msg.delete()
        vote_builder = "━━━━━━━━━━━━━━━\n**RÖSTNING**\n" + message_formatted + "\n\n<:yes:801237811595575386> för godkännande av förslag\n<:no:801237793073922069> för nekande av förslag, förslaget diskuteras vid nästa styrelsemöte.\n\n<:inprogress:801223023939289099> *Denna omröstning är öppen!*\n━━━━━━━━━━━━━━━"
        sent_message = await msg.channel.send(vote_builder)
        await sent_message.add_reaction(bot.get_emoji(801237811595575386))
        await sent_message.add_reaction(bot.get_emoji(801237793073922069))
        await sent_message.add_reaction(bot.get_emoji(801238564238000179))
    
    #Skicka meddelande som botten
    if ('!say' in msg.content.lower() and ("svit elit" in [y.name.lower() for y in msg.author.roles])):
        formatted_message = replace("everyone","@everyone",replace("!say","",msg.content,False),False)

        await msg.channel.send(formatted_message)
        if(len(msg.attachments) > 0):
            files = []
            for file in msg.attachments:
                fp = BytesIO()
                await file.save(fp)
                files.append(discord.File(fp, filename=file.filename, spoiler=file.is_spoiler()))
            await msg.channel.send(files=files)
        await msg.delete()
        
    #Ändra ett bot-meddelande med hjälp av meddelandets ID. (Meddelande -> Högerklicka -> Copy ID)
    if ('!edit' in msg.content.lower() and ("svit elit" in [y.name.lower() for y in msg.author.roles])):
        channel = msg.channel
        message = await channel.fetch_message(msg.content.lower().split(" ")[1])
        await message.edit(content=replace("!edit ","", msg.content, False).replace(msg.content.lower().split(" ")[1], ""))
        await msg.delete()
        
    #Radera ett meddelande
    if ('!remove' in msg.content.lower() and ("svit elit" in [y.name.lower() for y in msg.author.roles])):
        channel = msg.channel
        message = await channel.fetch_message(msg.content.lower().split(" ")[1])
        await message.delete()
        await msg.delete()

    #Stäng av botten (Ifall botten exempelvis skulle spamma @everyone vilket verkligen inte har hänt förut :) )
    if ('!emergency' in msg.content.lower() and ("svit elit" in [y.name.lower() for y in msg.author.roles])):
        await bot.close()

def replace(old, new, str, caseinsentive = False):
    if caseinsentive:
        return str.replace(old, new)
    else:
        return re.sub(re.escape(old), new, str, flags=re.IGNORECASE)
    
bot.run(TOKEN)
