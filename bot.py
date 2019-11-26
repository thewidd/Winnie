# bot.py
import os

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

async def notifyIfChangedPlayingState(possibleInGameMember, possibleOutOfGameMember, notificationTextFormat):
    for activity in possibleInGameMember.activities:
        if isinstance(activity, discord.Activity):
            if activity.type == discord.ActivityType.playing:
                if not any(a.type == discord.ActivityType.playing and a.application_id == activity.application_id for a in possibleOutOfGameMember.activities if isinstance(activity, discord.Activity)):
                    print(f'Sending notification of format {notificationTextFormat}')
                    sendText = notificationTextFormat.format(possibleInGameMember.name, activity.name)
                    await client.guilds[0].channels[0].text_channels[0].send(sendText)

async def checkGameSessionStarted(before, after):
    await notifyIfChangedPlayingState(after, before, '{} has started playing {}.')

async def checkGameSessionEnded(before, after):
    await notifyIfChangedPlayingState(before, after, '{} has stopped playing {}.')

@client.event
async def on_member_update(before, after):
    print(f'Received on_member_update for {before.name}')
    
    await checkGameSessionStarted(before, after)
    await checkGameSessionEnded(before, after)
    
client.run(TOKEN)