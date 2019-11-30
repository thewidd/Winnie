import discord

async def notifyIfChangedPlayingState(bot, registeredChannels, possibleInGameMember, possibleOutOfGameMember, notificationTextFormat):
    for activity in possibleInGameMember.activities:
        if isinstance(activity, discord.Activity) or isinstance(activity, discord.activity.Game):
            if activity.type == discord.ActivityType.playing:
                if not any(a.type == discord.ActivityType.playing and a.application_id == activity.application_id for a in possibleOutOfGameMember.activities if isinstance(activity, discord.Activity)):
                    print('found a change between in-game and out-of-game member updates')
                    sendText = notificationTextFormat.format(possibleInGameMember.name, activity.name)
                    for guild in bot.guilds:
                        for textChannel in guild.text_channels:
                            if textChannel.id in registeredChannels.getIds():
                                print(f'Sending notification to channelId: {textChannel.id}')
                                await textChannel.send(sendText)

async def checkGameSessionStarted(bot, registeredChannels, before, after):
    await notifyIfChangedPlayingState(bot, registeredChannels, after, before, '{} has started playing {}.')

async def checkGameSessionEnded(bot, registeredChannels, before, after):
    await notifyIfChangedPlayingState(bot, registeredChannels, before, after, '{} has stopped playing {}.')
