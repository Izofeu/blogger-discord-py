# blogger-discord-py
A simple Python app that automatically posts videos from a listening channel to Blogger. This version of the app is dedicated for Blogger.

**Opensourced at 2024.04.01 due to Discord time limiting URLs. No more updates will be released. This repo and source code is provided as-is. You'll likely have to change the code in some way to make it work.**

# What is this?
This app is a Discord bot coded in Python whose job is to create posts on a Blogger blog via links to content hosted on Discord's servers, as Discord file links are permalinks.

# Features
- Automatic uploading of videos with thumbnail (preview) support to Blogger
- Manual uploading
- Plenty of commands (oldschool style), help menu accessible with ]help
- Basic permissions support, only uploads from users with a role
- Semi-permanent killswitch
- Automatically delete posts if the original message gets deleted
- Auto scanning for missing posts in case bot went offline (v12+)

# Limitations
- The bot's code only supports a single server and a single blog. Upgrading it to support multiple servers / blogs shouldn't be difficult, just need to add a guild and blogid to all files and operations as well as multiple roles (one per server). Considering the niche nature of this kind of a bot, multi server support is the lowest on my priority list, if at all.
- No permission checking, ensure the bot has permission to send messages else you'll get 403s.

# Usage
1. Extract all files in a single directory. Go to step 6 if you already have the OAuth 2.0 API credentials
2. Go to https://console.cloud.google.com/
3. Create a project
4. Enable Blogger API
5. Create an OAuth 2.0 Client ID, download the file and put it in the bot's directory
6. Rename the oauth file to google_credentials.json. Go to step 9 if you already have a Discord bot created
7. Create a Discord application at https://discord.com/developers/applications
8. Create a bot token and copy it
9. Set loginDebug to true
10. Set myblogid, earlier copied token and optionally master variables.
11. Edit channelid.txt with a channel ID the bot will listen to
12. Start the bot
13. Send a message with a video file attachment in the listening channel
14. Send a valid tags command
15. Open a webpage that has appeared in the bot's console, log in with your Google account and grant access to Blogger API
16. Shut down the bot, set loginDebug to false
17. Start the bot

# Updates?
I plan on releasing updates eventually. My goal is to make everything as documented and as user friendly as possible. Some of the things plannned: an sql database instead of text files, a proper config file and very maybe a multi server support. However, because right now I don't need any extra features, I can't promise I will release any updates. There's a possibility of me losing interest in the project, most likely because I won't need it anymore and I'd rather create something new that will be of value to me rather than maintain a project that doesn't benefit me at all. Chances are, if you're reading this it means I published the bot because I don't use / need it anymore. And the most important part is, a bot like this is extremely niche, the amount of people / servers that could benefit from it or would like to use it is close to zero.
