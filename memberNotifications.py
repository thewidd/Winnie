import discord

async def notifyIfChangedPlayingState(bot, registeredChannels, possibleInGameMember, possibleOutOfGameMember, notificationTextFormat):
    '''
    Send a notification to all registered channels if a user has gone from in-game to out-of-game or vice
    '''    
    possibleInGameIsInGame, inGameActivity = isPlaying(possibleInGameMember)
    possibleOutOfGameIsOutOfGame = not isPlaying(possibleOutOfGameMember)[0]
    # print(f'possibleInGameIsInGame: {possibleInGameIsInGame}, possibleOutOfGameIsOutOfGame: {possibleOutOfGameIsOutOfGame}')

    channelsToNotify = []
    if possibleInGameIsInGame and possibleOutOfGameIsOutOfGame:
        activityForMessage = inGameActivity
        channelsToNotify = [channel for channel in possibleInGameMember.guild.text_channels if channel.id in registeredChannels.getIds()]

    if channelsToNotify:
        # print(f'processing guildId: {possibleInGameMember.guild.id}')
        print(f"Found a change between in-game and out-of-game member updates. Notifying channelIds: [{ ', '.join([str(channel.id) for channel in channelsToNotify]) }]")
        sendText = notificationTextFormat.format(possibleInGameMember.name, activityForMessage.name)
        for channelToNotify in channelsToNotify:
            await channelToNotify.send(sendText)

def isPlaying(member):
    '''
    Return: tuple of (isPlaying, member.activity object of the playing activity)
    '''
    gameActivities = [activity for activity in member.activities if isPlayingGameActivity(activity)]
    return (len(gameActivities) != 0, next(iter(gameActivities), None))

def isPlayingGameActivity(activity):
    return (isinstance(activity, discord.Activity) and activity.type == discord.ActivityType.playing) or isinstance(activity, discord.activity.Game)

async def checkGameSessionStarted(bot, registeredChannels, before, after):
    await notifyIfChangedPlayingState(bot, registeredChannels, after, before, '{} has started playing {}.')

async def checkGameSessionEnded(bot, registeredChannels, before, after):
    await notifyIfChangedPlayingState(bot, registeredChannels, before, after, '{} has stopped playing {}.')
