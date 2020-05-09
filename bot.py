# bot.py
import os
import csv
import discord
import model.registeredChannels
import model.guildConfigs
import memberNotifications as mn
import roleManagement as rm
import registration
import eventManager as em

from dotenv import load_dotenv
from discord.ext import commands
from typing import Union

if __name__ == '__main__':
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')
    bot.GUILD_IDS_TO_IGNORE = ''.split() # os.getenv('GUILD_IDS_TO_IGNORE').split()

    bot = commands.Bot(command_prefix='~')
    print('bot created')
    bot.registeredChannels = model.registeredChannels.RegisteredChannels(bot)
    print('channels registered')
    # registeredUsers = model.registeredUsers.RegisteredUsers(bot)
    # print('users registered')
    print(f'GUILD_IDS_TO_IGNORE: {bot.GUILD_IDS_TO_IGNORE}')
    bot.guildConfigs = model.guildConfigs.GuildConfigs()
    bot.roleManagement = rm.RoleManagement()
    bot.memberNotifications = mn.MemberNotifications(bot)
    eventManager = em.EventManager(bot)

@bot.event
async def on_ready():
    await eventManager.on_ready()
    
# send message if a member's activity state has changed
@bot.event
async def on_member_update(before, after):
    await eventManager.on_member_update(before, after)

# update registered channels when one is removed
@bot.event
async def on_guild_channel_delete(channel):
    await eventManager.on_guild_channel_delete(channel)

# register a new channel
@bot.command(name='reg', help='Register this text channel to receive notifications of members starting/stopping gaming sessions.')
async def registerChannel(ctx):
    await registration.registerChannel(ctx, bot.registeredChannels)

# unregister an existing channel
@bot.command(name='unreg', help='Unregister a previously registered channel.')
async def unregisterChannel(ctx):
    await registration.unregisterChannel(ctx, bot.registeredChannels)

@bot.command(name='config', help='''
Customize notification/bot management of the server. Configurations you can make:

    ~config createRoleForPlayersOfGame true/false: For any game played by members of this server, Winnie will generate a role for players of that game for easier communication of like-minded people
''')
async def config(ctx, key: str, value: bool):
    if key in bot.guildConfigs.supportedConfigKeys:
        bot.guildConfigs.setConfig(ctx.guild.id, key, value)
    else:
        await ctx.send("Invalid key given. Please see '~help config' for available configs.")

@bot.event
async def on_command_error(ctx, error):
    await ctx.send(error)
    print(f'Command error: {error}')

if __name__ == '__main__':
    bot.run(TOKEN)