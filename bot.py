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

    bot = commands.Bot(command_prefix='~')
    print('bot created')
    bot.registeredChannels = model.registeredChannels.RegisteredChannels(bot)
    print('channels registered')
    # registeredUsers = model.registeredUsers.RegisteredUsers(bot)
    # print('users registered')
    bot.GUILD_IDS_TO_IGNORE = ''.split() # os.getenv('GUILD_IDS_TO_IGNORE').split()
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

@bot.command(name='set_config', help='''
Customize notification/bot management of the server. Configurations you can make:

    ~set_config createRoleForPlayersOfGame true/false: For any game played by members of this server, Winnie will generate a role for players of that game for easier communication of like-minded people
''')
async def set_config(ctx, key: str, value: bool):
    key_value_message_format = '{}: {}'
    if key in bot.guildConfigs.supportedConfigKeys:
        try:
            set_val = bot.guildConfigs.setConfig(ctx.guild.id, key, value)
            await ctx.send(f'Successfully set config:\n\n{key_value_message_format.format(key, set_val)}')
        except:
            await ctx.send('Sorry, there was a problem :(')
    else:
        await ctx.send("Invalid key given. Please see '~help set_config' for usage.")

@bot.command(name='get_config', help='''
Get custom configurations of the server. Configurations you can get:

    ~get_config (Lists all configs)
    ~get_config createRoleForPlayersOfGame (For any game played by members of this server, Winnie will generate a role for players of that game for easier communication of like-minded people)
''')
async def get_config(ctx, key: str=None):
    key_value_message_format = '{}: {}'
    if key == None:
        config_values = bot.guildConfigs.get_all_configs(ctx.guild.id)
        message = '\n'.join([key_value_message_format.format(k, bool(v)) for v, k in enumerate(config_values)])
        await ctx.send(f'Currently set config values:\n\n{message}')
    elif key in bot.guildConfigs.supportedConfigKeys:
        config_value = bot.guildConfigs.getConfig(ctx.guild.id, key)
        await ctx.send(f'Current config:\n\n{key_value_message_format.format(key, config_value)}')
    else:
        await ctx.send("Invalid key given. Please see '~help get_config' for usage.")

@bot.event
async def on_command_error(ctx, error):
    await ctx.send(error)
    print(f'Command error: {error}')

if __name__ == '__main__':
    bot.run(TOKEN)