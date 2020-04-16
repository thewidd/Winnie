# bot.py
import os
import csv
import discord
import model.dataStore as dataStore
import memberNotifications
import registration

from dotenv import load_dotenv
from discord.ext import commands
from typing import Union

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='~')
print('bot created')
registeredChannels = dataStore.RegisteredChannels(bot)
print('channels registered')
# registeredUsers = dataStore.RegisteredUsers(bot)
# print('users registered')

@bot.event
async def on_ready():
    global registeredChannel
    registeredChannels.initialize()
    # registeredUsers.initialize()
    
# send message if a member's activity state has changed
@bot.event
async def on_member_update(before, after):
    print(f'Received on_member_update for {before.id}')
    await memberNotifications.checkGameSessionStarted(bot, registeredChannels, before, after)
    await memberNotifications.checkGameSessionEnded(bot, registeredChannels, before, after)     

# update registered channels when one is removed
@bot.event
async def on_guild_channel_delete(channel):
    print(f"channel removed with channeldId: {channel.id}")
    if channel.id in registeredChannels:
        print(f"A channel that's registered was removed. channeldId: {channel.id}")
        registeredChannels.remove(channel.id)

# register a new channel
@bot.command(name='reg', help='Register this text channel as the channel to receive notificatinos of members entering/exiting gaming sessions.')
async def registerChannel(ctx):
    await registration.registerChannel(ctx, registeredChannels)

# unregister an existing channel
@bot.command(name='unreg', help='Unregister a previously registered channel.')
async def unregisterChannel(ctx):
    await registration.unregisterChannel(ctx, registeredChannels)

@bot.command(name='regUser', help='Register to get a DM when a specific user enter/exit a game session')
async def registerUser(ctx, user: Union[discord.User, discord.Member]):
    print(f'regUser called on {user.id}')
    await registration.registerUser(ctx, registeredUsers, user)

@bot.command(name='blacklist')
async def blacklistGame(ctx, subCmd, nameToBlacklist):
    subCmd = subCmd.lower()
    if subCmd == 'game':
        print('blacklist a game')
        # 1. Check if the game bing requested is in my Games library (better name than "Games')
        # 2. If it is, put it on my blackList
        # 3. Update memberNotifications to first check the blacklist before notifying
        # 4. Save blacklisted games to DB

    # elif subCmd =  'user':
    #     print('blacklist a user. Not available yet')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        print('Bad Argument')
        # await ctx.send('I could not find that member...')
    print(f'Command error! error: {error}')

bot.run(TOKEN)