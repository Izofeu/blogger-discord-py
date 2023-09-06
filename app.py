#from discord.ext import commands
import discord
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
import json

scopes = ["https://www.googleapis.com/auth/blogger"]


internalDebug = False
uploadDisabled = False
loginDebug = False
noDelete = False
disableTags = False


startup = open("preventstartup.txt", "r")
if int(startup.read()) == 1:
    print("Startup is disabled.")
    quit()
startup.close()

uploadPending = False
tags = 0
g_messageText = g_imageUrl = g_videoUrl = g_uploadername = g_messageid = 0
def getpending():
    global uploadPending, g_messageText, g_imageUrl, g_videoUrl, g_uploadername, g_messageid
    return g_messageText, g_imageUrl, g_videoUrl, g_uploadername, g_messageid
    
def setpending(p_messageText, p_imageUrl, p_videoUrl, p_uploadername, p_messageid):
    global uploadPending, g_messageText, g_imageUrl, g_videoUrl, g_uploadername, g_messageid
    g_messageText = p_messageText
    g_imageUrl = p_imageUrl
    g_videoUrl = p_videoUrl
    g_uploadername = p_uploadername
    g_messageid = p_messageid
    uploadPending = True
    return

#id of the blog to upload videos to
myblogid = 0
#ids of accounts with permission override, doesnt affect uploading
master = [0]
#bot access token
token = ""
chid = open("channelid.txt", "r")
allowed_channel_id = int(chid.read())
chid.close()

prol = open("permittedrole.txt", "r")
permitted_role = int(prol.read())
prol.close()

def authenticate():
    global loginDebug
    if loginDebug:
        flow = InstalledAppFlow.from_client_secrets_file(
                'google_credentials.json', scopes)
        creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    try:
        creds = Credentials.from_authorized_user_file("token.json", scopes)
        if not creds.valid:
            creds.refresh(Request())
    except:
        print("WRONG1")
        return False
    try:
        auth = build("blogger", "v3", credentials=creds)
    except:
        #raise Exception("Authentication failed.")
        return False
    return auth

def submit(text, imagelink, videolink, uploader, tags):
    try:
        blogger = authenticate()
        if not blogger:
            print("error")
            raise Exception("Authentication error.")
        #print("success1")
        rbody = {
                "kind": "blogger#post",
                "title": text,
                "labels": "" + uploader + "," + tags + "",
                "content": ("<p>Video:</p>"
                            "<img src=\"" + imagelink + "\" style=\"display:none;\" loading=\"lazy\">"
                            "<video controls name=\"media\" preload=\"none\" class=\"lazy videostags\" data-poster=\"" + imagelink + "\">"
                            "<source src=\"" + videolink + "\" type=\"video/mp4\">"
                            "</video>"
                           )
                }
        #print("success2")
        global myblogid
        ret = blogger.posts().insert(blogId=myblogid, body=rbody, isDraft=False).execute()
        #print("success3")
        oret = ret.get("url")
        oid = ret.get("id")
        return oret, oid
    except:
        print("SOMETHING WENT WRONG")
        return False, False

def wasposted(messageid):
    posts = open("posts.txt", "r")
    for line in posts:
        splitted = line.split(",")
        splitted = splitted[0]
        if messageid == str(splitted):
            posts.close()
            return True
    posts.close()
    return False
    
def addmessageid(messageid, postid):
    file = open("posts.txt", "a")
    file.write(str("\n") + messageid + "," + postid)
    file.close()
    return
    
    
def deletemessageid(messageid):
    file = open("posts.txt", "r+")
    all_lines = []
    all_lines = file.readlines()
    lines = []
    index = 0
    for x in all_lines:
        lines = x.split(",")
        lines = str(lines[0])
        if messageid == lines:
            all_lines.pop(index)
            break
        index+=1
    file.seek(0)
    file.truncate()
    length = len(all_lines)
    finalline = all_lines[length-1]
    if finalline[-1] == "\n":
        all_lines[length-1] = finalline[:-1]
    for x in all_lines:
        file.write(x)
    file.close()
    return

def deletepost(postid):
    try:
        blogger = authenticate()
        if not blogger:
            raise Exception("Login error.")
        global myblogid
        res = blogger.posts().delete(blogId=myblogid, postId=postid, useTrash=True)
        res.execute()
        return True
    except:
        return False

def getpostid(messageid):
    file = open("posts.txt", "r")
    lines = []
    lines = file.readlines()
    for x in lines:
        line = x.split(",")
        if messageid == str(line[0]):
            postid = str(line[1])
            if postid[-1] == "\n":
                postid = postid[:-1]
            break
    file.close()
    return postid

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
        "A ]switch <id> - Change listening channel.\n"
        "A ]exit - Shut down the bot - this is semi-permanent, only the bot owner can restart the bot, use only in case of emergency.\n"
        "A ]setid <id> - Set the id of a role permitted to post on the blog.\n"
        "U ]enabletags / ]disabletags - Toggle tagging system.\n"
        "U ]skip - Skips entering tags.\n"
        "U ]tags <tags separated by commas> - Publish a pending post with selected tags.\n"
        "U ]submit post title;videourl;imageurl - Manually submit a new post.\n"
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
    global allowed_channel_id, disableTags, uploadPending
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
    
    if message.channel.id != allowed_channel_id:
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
        
        messageText, imageUrl, videoUrl, uploadername, messageid = getpending()
        result_url, result_id = submit(messageText, imageUrl, videoUrl, uploadername, tags)
        if not result_url:
            await message.channel.send("Something went wrong. Login credentials are likely expired. Contact the bot owner. New blog post has not been posted.")
        else:
            result_id = str(result_id)
            addmessageid(messageid, result_id)
            uploadPending = False
            await message.channel.send("New blog post has successfully been posted! " + str(result_url))
        return
    
    
    if message.content.startswith("]skip"):
        if not isuploader(message):
            return
        if not uploadPending:
            await message.channel.send("No upload is pending.")
            return
            
        messageText, imageUrl, videoUrl, uploadername, messageid = getpending()
        result_url, result_id = submit(messageText, imageUrl, videoUrl, uploadername, "")
        if not result_url:
            await message.channel.send("Something went wrong. Login credentials are likely expired. Contact the bot owner. New blog post has not been posted.")
        else:
            result_id = str(result_id)
            addmessageid(messageid, result_id)
            uploadPending = False
            await message.channel.send("New blog post has successfully been posted! " + str(result_url))
    
    
    if message.content.startswith("]submit"):
        if not isuploader(message):
            return
        messagestring = message.content[8:]
        if not messagestring:
            await message.channel.send("Command usage: ]submit post title;videourl;imageurl\nMake sure there are no spaces in between the semicolons.")
            return
        splitted = messagestring.split(";")
        if len(splitted) < 2 or len(splitted) > 3 or not splitted[1]:
            await message.channel.send("That doesn\'t look right. Expected arguments: 2 or 3. Arguments received: " + str(len(splitted)) + ". Separate your arguments with a semicolon. Run this command without arguments to see help.")
            return
        messageText = splitted[0]
        videoUrl = splitted[1]
        if len(splitted) == 3:
            imageUrl = splitted[2]
        else:
            imageUrl = ""
        if not messageText:
            messageText = "Untitled post"
        if len(messageText) > 80:
            messageText = messageText[0:77] + str("...")
        uploadername = str(message.author.name)
        messageid = str(message.id)
        #discriminator = message.author.discriminator
        if not disableTags:
            setpending(messageText, imageUrl, videoUrl, uploadername, messageid)
            await message.channel.send("Message parsed successfully. Awaiting tags input before upload. ]skip to skip.")
            return
        result_url, result_id = submit(messageText, imageUrl, videoUrl, uploadername, "")
        if not result_url:
            await message.channel.send("Something went wrong. Login credentials are likely expired. Contact the bot owner. New blog post has not been posted.")
        else:
            result_id = str(result_id)
            addmessageid(messageid, result_id)
            await message.channel.send("New blog post has successfully been posted! " + str(result_url))
        return
        
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
                messageid = str(message.id)
                if not disableTags:
                    setpending(messageText, imageUrl, videoUrl, uploadername, messageid)
                    await message.channel.send("Message parsed successfully. Awaiting tags input before upload. ]skip to skip.")
                    return
                if uploadDisabled:
                    #addmessageid(messageid)
                    await message.channel.send("Message parsed successfully. Upload is disabled.")
                    return
                result_url, result_id = submit(messageText, imageUrl, videoUrl, uploadername, "")
                if not result_url:
                    await message.channel.send("Something went wrong. Login credentials are likely expired. Contact the bot owner. New blog post has not been posted.")
                else:
                    result_id = str(result_id)
                    addmessageid(messageid, result_id)
                    await message.channel.send("New blog post has successfully been posted! " + str(result_url))
            return
    return

@client.event
async def on_raw_message_delete(message):
    id = str(message.message_id)
    global noDelete
    if noDelete:
        varr = wasposted(id)
        print(varr)
        if varr:
            deletemessageid(id)
        #deletemessageid(id)
        return

    if not wasposted(id):
        return
    postid = getpostid(id)
    if not deletepost(postid):
        print("Deletion error, deletion has been disabled.")
        noDelete = True
    deletemessageid(id)
    return
    
client.run(token)
