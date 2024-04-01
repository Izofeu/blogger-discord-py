import discord
import json
import asyncio
import time
import asyncmy as mysql


internalDebug = False
disableTags = False
passwordpath = ""
domain = "https://nutsuki.fun"

startup = open("preventstartup.txt", "r")
if int(startup.read()) == 1:
    print("Startup is disabled.")
    quit()
startup.close()

starttime = int(time.time())

uploadPending = False
tags = 0
g_messageText = g_imageUrl = g_videoUrl = g_uploadername = 0

async def submit(text, imagelink, videolink, uploader, tags, paid):
    db = await mysql.connect(host="127.0.0.1", user="pyth", port=3306, password=passwordpath, database="website", autocommit=True)
    # 0 - id
    # 1 - title
    # 2 - tags
    # 3 - uploader
    # 4 - date (YYYY-MM-DD HH:mm:ss)
    # 5 - videourl
    # 6 - imageurl
    # 7 - ispaid
    paid = str(paid)
    date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    date = str(date)
    query = ("INSERT INTO posts"
            " (title, tags, uploader, date, videourl, imageurl, ispaid)"
            " VALUES (%s, %s, %s, '" + date + "', %s, %s, %s)"
            )
    async with db.cursor() as cursor:
        await cursor.execute(query, [text, tags, uploader, videolink, imagelink, paid])
        postid = cursor.lastrowid
    url = domain + "/index.php?id=" + str(postid)
    db.close()
    return url

def getpending():
    global uploadPending, g_messageText, g_imageUrl, g_videoUrl, g_uploadername
    return g_messageText, g_imageUrl, g_videoUrl, g_uploadername
    
def setpending(p_messageText, p_imageUrl, p_videoUrl, p_uploadername):
    global uploadPending, g_messageText, g_imageUrl, g_videoUrl, g_uploadername
    g_messageText = p_messageText
    g_imageUrl = p_imageUrl
    g_videoUrl = p_videoUrl
    g_uploadername = p_uploadername
    uploadPending = True
    return
    
#ids of accounts with permission override, doesnt affect uploading
master = [186894189252968449,471135780694261761]
#bot access token
token = ""

chid = open("channelid.txt", "r")
allowed_channel_id = int(chid.read())
chid.close()

chid = open("channelid_paid.txt", "r")
allowed_channel_id_paid = int(chid.read())
chid.close()

prol = open("permittedrole.txt", "r")
permitted_role = int(prol.read())
prol.close()

def setnewrole(id):
    file = open("permittedrole.txt", "w")
    file.write(str(id))
    global permitted_role
    permitted_role = id
    file.close()
    return
    
def setnewid(id):
    file = open("channelid.txt", "w")
    file.write(str(id))
    global allowed_channel_id
    allowed_channel_id = id
    file.close()
    return

def setnewpaidid(id):
    file = open("channelid_paid.txt", "w")
    file.write(str(id))
    global allowed_channel_id_paid
    allowed_channel_id_paid = id
    file.close()
    return

def isserveradmin(message):
    return message.author.guild_permissions.manage_guild
    
def isuploader(message):
    for x in message.author.roles:
        if x.id == permitted_role:
            return True
    return False
    
def uploadprepare(message):
    #returns all falses or image and videourl
    validimg = ["image/png", "image/jpeg"]
    hasImage = False
    hasVideo = False
    imageUrl = ""
    videoUrl = ""
    for array in message.attachments:
        type = array.content_type
        if type in validimg and not hasImage:
            hasImage = True
            imageUrl = array.url
        if type == "video/mp4" and not hasVideo:
            hasVideo = True
            videoUrl = array.url
    if not hasVideo:
        return False, False, False, False
    messageText = str(message.content)
    if not messageText:
        messageText = "Untitled post"
    
    if len(messageText) > 80:
        messageText = messageText[0:77] + str("...")

    uploadername = str(message.author.name)
    #discriminator = message.author.discriminator
    return messageText, imageUrl, videoUrl, uploadername
    
def preventStartup():
    file = open("preventstartup.txt", "w")
    file.write(str(1))
    file.close()
    return
    
permerror = "Permission required: Manage server. Account ids with permission override: " + str(master)
help = ("Help menu:\n"
        "Command prefix - ]\n"
        "Permission prefixes: U - uploader only, A - admin only\n"
        "]help - Open this menu.\n"
        "]uptime - Get bot uptime.\n"
        "A ]switch <id> - Change listening channel.\n"
        "A ]switch <id> - Change listening channel of paid posts.\n"
        "A ]exit - Shut down the bot - this is semi-permanent, only the bot owner can restart the bot, use only in case of emergency.\n"
        "A ]setid <id> - Set the id of a role permitted to post on the blog.\n"
        "U ]enabletags / ]disabletags - Toggle tagging system.\n"
        "U ]skip - Skips entering tags.\n"
        "U ]tags <tags separated by commas> - Publish a pending post with selected tags.\n"
        "U Posting: Post title (your message), image and video as attachments in one message in the listening channel.\n"
        "Account ids with permission override: " + str(master) + "\n"
        "Bot is currently listening on channel id " + str(allowed_channel_id)
       )
       
       
intents = discord.Intents().default()
#print(dir(intents))
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print("Logged in")
    return
    
@client.event
async def on_message(message):
    global allowed_channel_id, allowed_channel_id_paid, disableTags, uploadPending
    if message.author == client.user:
        return
        
    if internalDebug:
        if message.content.startswith("]test"):
            await message.channel.send(str(isuploader(message)))
        #return
        
    if message.content.startswith("]switch"):
        if message.author.id not in master and not isserveradmin(message):
            await message.channel.send(permerror)
            return
        else:
            try:
                newid = int(message.content[-19:])
            except:
                await message.channel.send("Incorrect channel ID string. Channel not changed.")
                return
            if len(str(newid)) != 19:
                await message.channel.send("Incorrect channel ID length. Channel not changed.")
                return
            setnewid(newid)
            await message.channel.send("Allowed channel ID changed to " + str(allowed_channel_id))
            return
            
    elif message.content.startswith("]paidswitch"):
        if message.author.id not in master and not isserveradmin(message):
            await message.channel.send(permerror)
            return
        else:
            try:
                newid = int(message.content[-19:])
            except:
                await message.channel.send("Incorrect channel ID string. Channel not changed.")
                return
            if len(str(newid)) != 19:
                await message.channel.send("Incorrect channel ID length. Channel not changed.")
                return
            setnewpaidid(newid)
            await message.channel.send("Allowed paid channel ID changed to " + str(allowed_channel_id_paid))
            return

    elif message.content.startswith("]exit"):
        if message.author.id in master or isserveradmin(message):
            await message.channel.send("Terminating.")
            preventStartup()
            quit()
        else:
            await message.channel.send(permerror)
            return
    
    if message.content.startswith("]help"):
        await message.channel.send(help)
        return
    
    if message.channel.id not in [allowed_channel_id, allowed_channel_id_paid]:
        return
    
    paid = 0
    if message.channel.id == allowed_channel_id_paid:
        paid = 1
        
    if message.content.startswith("]uptime"):
        ttime = int(time.time()) - starttime
        ttime_m = str((ttime // 60) % 60)
        ttime_h = str((ttime // 3600) % 24)
        ttime_d = str(ttime // 86400)
        tosend = "Bot uptime: "
        if int(ttime_d) > 0:
            tosend = tosend + ttime_d + "d " + ttime_h + "h " + ttime_m + "m."
        elif int(ttime_h) > 0:
            tosend = tosend + ttime_h + "h " + ttime_m + "m."
        else:
            tosend = tosend + ttime_m + "m."
        await message.channel.send(tosend)
        return
        
    if message.content.startswith("]enabletags"):
        if not isuploader(message):
            return
        disableTags = False
        await message.channel.send("Tagging system has been enabled.")
        return
        
    if message.content.startswith("]disabletags"):
        if not isuploader(message):
            return
        disableTags = True
        await message.channel.send("Tagging system has been disabled.")
        return
        
    if message.content.startswith("]tags"):
        if not isuploader(message):
            return
        if not uploadPending:
            await message.channel.send("No upload is pending.")
            return
        
        tags = message.content[6:]
        if not tags:
            await message.channel.send("No tags provided.")
            return
        
        messageText, imageUrl, videoUrl, uploadername = getpending()
        result_url = await submit(messageText, imageUrl, videoUrl, uploadername, tags, paid)
        if not result_url:
            await message.channel.send("Something went wrong. Login credentials are likely expired. Contact the bot owner. New blog post has not been posted.")
        else:
            uploadPending = False
            await message.channel.send("New blog post has successfully been posted! " + str(result_url))
        return
        
    if message.content.startswith("]skip"):
        if not isuploader(message):
            return
        if not uploadPending:
            await message.channel.send("No upload is pending.")
            return
            
        messageText, imageUrl, videoUrl, uploadername = getpending()
        result_url = await submit(messageText, imageUrl, videoUrl, uploadername, "", paid)
        if not result_url:
            await message.channel.send("Something went wrong. Login credentials are likely expired. Contact the bot owner. New blog post has not been posted.")
        else:
            uploadPending = False
            await message.channel.send("New blog post has successfully been posted! " + str(result_url))
            
            
    if message.content.startswith("]setid"):
        if message.author.id not in master and not isserveradmin(message):
            await message.channel.send(permerror)
            return
        else:
            try:
                newid = int(message.content[-19:])
            except:
                await message.channel.send("Incorrect role ID string. Permitted role not changed.")
                return
            if len(str(newid)) != 19:
                await message.channel.send("Incorrect role ID length. Permitted role not changed.")
                return
            setnewrole(newid)
            await message.channel.send("Allowed role ID changed to " + str(permitted_role))
            return
        return
        
    else:
        if isuploader(message):
            if not message.attachments:
                return
            else:
                messageText, imageUrl, videoUrl, uploadername = uploadprepare(message)
                if not messageText:
                    return
                if not disableTags:
                    setpending(messageText, imageUrl, videoUrl, uploadername)
                    await message.channel.send("Message parsed successfully. Awaiting tags input before upload. ]skip to skip.")
                    return
                result_url = await submit(messageText, imageUrl, videoUrl, uploadername, "", paid)
                if not result_url:
                    await message.channel.send("Something went wrong. Login credentials are likely expired. Contact the bot owner. New blog post has not been posted.")
                else:
                    await message.channel.send("New blog post has successfully been posted! " + str(result_url))
            return
    return
    
client.run(token)
