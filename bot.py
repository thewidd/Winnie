# bot.py
import os
import csv
import discord
import dataStore
import memberNotifications
import registration

from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')
registeredChannelIds = set()

@bot.event
async def on_ready():
    global registeredChannelIds
    registeredChannelIds = set(dataStore.read())
    print(f'Read in {len(registeredChannelIds)} Channels')

@bot.event
async def on_member_update(before, after):
    print(f'Received on_member_update for {before.name}')
    await memberNotifications.checkGameSessionStarted(bot, registeredChannelIds, before, after)
    await memberNotifications.checkGameSessionEnded(bot, registeredChannelIds, before, after)     

@bot.command(name='reg', help='Register this text channel as the channel to receive notificatinos of members entering/existing gaming sessions.')
async def registerChannel(ctx):
    await registration.registerChannel(ctx, registeredChannelIds)

@bot.command(name='unreg', help='Unregister a previously registered channel.')
async def unregisterChannel(ctx):
    await registration.unregisterChannel(ctx, registeredChannelIds)

bot.run(TOKEN)