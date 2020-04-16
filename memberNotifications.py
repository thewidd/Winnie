import discord

async def notifyIfChangedPlayingState(bot, registeredChannels, possibleInGameMember, possibleOutOfGameMember, notificationTextFormat):
    print(f'possibleInGameMemberActivity: {possibleInGameMember.activity}, \npossibleOutOfGameMemberActivity: {possibleOutOfGameMember.activity}')
    shouldNotifyGuild = False
    
    possibleInGameIsInGame = isPlaying(possibleInGameMember)
    possibleOutOfGameIsOutOfGame = not isPlaying(possibleOutOfGameMember)
    print(f'possibleInGameIsInGame: {possibleInGameIsInGame}, possibleOutOfGameIsOutOfGame: {possibleOutOfGameIsOutOfGame}')

    if possibleInGameIsInGame and possibleOutOfGameIsOutOfGame:
        print('found a change between in-game and out-of-game member updates')
        activityForMessage = possibleInGameMember.activity
        shouldNotifyGuild = True

    if shouldNotifyGuild: # and not activityForMessage.name.startswith('Halo: The Master Chief') :
        print(f'processing guildId: {possibleInGameMember.guild.id}')
        channelsToNotify = [channel for channel in possibleInGameMember.guild.text_channels if channel.id in registeredChannels.getIds()]
        
        print(f"notifying channelIds: [{ ', '.join([str(channel.id) for channel in channelsToNotify]) }]")
        sendText = notificationTextFormat.format(possibleInGameMember.name, activityForMessage.name)
        for channelToNotify in channelsToNotify:
            await channelToNotify.send(sendText)

def isPlaying(member):
    activity = member.activity
    return (isinstance(activity, discord.Activity) and activity.type == discord.ActivityType.playing) or (isinstance(activity, discord.activity.Game))

async def checkGameSessionStarted(bot, registeredChannels, before, after):
    print('\nchecking game session STARTED')
    await notifyIfChangedPlayingState(bot, registeredChannels, after, before, '{} has started playing {}.')

async def checkGameSessionEnded(bot, registeredChannels, before, after):
    print('\nchecking game session ENDED')
    await notifyIfChangedPlayingState(bot, registeredChannels, before, after, '{} has stopped playing {}.')
