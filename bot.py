# bot.py
import os
import csv
import discord
import model.registeredChannels
import model.guildConfigs
import memberNotifications as mn
import roleManagement as rm
import registration

from dotenv import load_dotenv
from discord.ext import commands
from typing import Union

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_IDS_TO_IGNORE = ''.split() # os.getenv('GUILD_IDS_TO_IGNORE').split()

bot = commands.Bot(command_prefix='~')
print('bot created')
registeredChannels = model.registeredChannels.RegisteredChannels(bot)
print('channels registered')
# registeredUsers = model.registeredUsers.RegisteredUsers(bot)
# print('users registered')
print(f'GUILD_IDS_TO_IGNORE: {GUILD_IDS_TO_IGNORE}')
guildConfigs = model.guildConfigs.GuildConfigs()
roleManagement = rm.RoleManagement(guildConfigs)
memberNotifications = mn.MemberNotifications(bot, registeredChannels, guildConfigs, roleManagement)

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    global registeredChannels
    registeredChannels.initialize()
    guildConfigs.initialize()
    # registeredUsers.initialize()
    
# send message if a member's activity state has changed
@bot.event
async def on_member_update(before, after):
    if before.guild.id not in GUILD_IDS_TO_IGNORE:
        # print(f'Received on_member_update for {before.id}')
        await memberNotifications.notifyIfGamingStateChanged(before, after)

# update registered channels when one is removed
@bot.event
async def on_guild_channel_delete(channel):
    print(f"channel removed with channeldId: {channel.id}")
    if channel.id in registeredChannels:
        print(f"A channel that's registered was removed. channeldId: {channel.id}")
        registeredChannels.remove(channel.id)

# register a new channel
@bot.command(name='reg', help='Register this text channel to receive notifications of members starting/stopping gaming sessions.')
async def registerChannel(ctx):
    await registration.registerChannel(ctx, registeredChannels)

# unregister an existing channel
@bot.command(name='unreg', help='Unregister a previously registered channel.')
async def unregisterChannel(ctx):
    await registration.unregisterChannel(ctx, registeredChannels)

@bot.command(name='config', help='''
Customize notification/bot management of the server. Configurations you can make:

    ~config createRoleForPlayersOfGame true/false: For any game played by members of this server, Winnie will generate a role for players of that game for easier communication of like-minded people
''')
async def config(ctx, key: str, value: bool):
    global guildConfigs
    if key in guildConfigs.supportedConfigKeys:
        guildConfigs.setConfig(ctx.guild.id, key, value)
    else:
        await ctx.send("Invalid key given. Please see '~help config' for available configs.")

@bot.event
async def on_command_error(ctx, error):
    await ctx.send(error)
    print(f'Command error: {error}')

bot.run(TOKEN)