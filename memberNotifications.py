import discord

async def notifyIfChangedPlayingState(bot, registeredChannelIds, possibleInGameMember, possibleOutOfGameMember, notificationTextFormat):
    for activity in possibleInGameMember.activities:
        if isinstance(activity, discord.Activity):
            if activity.type == discord.ActivityType.playing:
                if not any(a.type == discord.ActivityType.playing and a.application_id == activity.application_id for a in possibleOutOfGameMember.activities if isinstance(activity, discord.Activity)):
                    sendText = notificationTextFormat.format(possibleInGameMember.name, activity.name)
                    for guild in bot.guilds:
                        for textChannel in guild.text_channels:
                            if textChannel.id in registeredChannelIds:
                                print(f'Sending notification to channelId: {textChannel.id}')
                                await textChannel.send(sendText)                            
                            
                    
                    

async def checkGameSessionStarted(bot, registeredChannelIds, before, after):
    await notifyIfChangedPlayingState(bot, registeredChannelIds, after, before, '{} has started playing {}. Join in on the fun!')

async def checkGameSessionEnded(bot, registeredChannelIds, before, after):
    await notifyIfChangedPlayingState(bot, registeredChannelIds, before, after, '{} has stopped playing {}. :`(')
