import discord

async def notifyIfChangedPlayingState(bot, registeredChannels, possibleInGameMember, possibleOutOfGameMember, notificationTextFormat):

    shouldNotifyGuild = False
    for activity in possibleInGameMember.activities:
        print('activity name: ', activity.type)
        if isinstance(activity, discord.Activity) or isinstance(activity, discord.activity.Game):
            if activity.type == discord.ActivityType.playing:
                if not any(a.type == discord.ActivityType.playing and a.application_id == activity.application_id for a in possibleOutOfGameMember.activities if isinstance(activity, discord.Activity)):
                    print('found a change between in-game and out-of-game member updates')
                    activityForMessage = activity
                    shouldNotifyGuild = True
                    break

    if shouldNotifyGuild and not activityForMessage.name.startswith('Halo: The Master Chief') :
        print(f'processing guildId: {possibleInGameMember.guild.id}')
        channelsToNotify = [channel for channel in possibleInGameMember.guild.text_channels if channel.id in registeredChannels.getIds()]
        
        print(f"notifying channelIds: [{ ', '.join([str(channel.id) for channel in channelsToNotify]) }]")
        sendText = notificationTextFormat.format(possibleInGameMember.name, activityForMessage.name)
        for channelToNotify in channelsToNotify:
            await channelToNotify.send(sendText)

async def checkGameSessionStarted(bot, registeredChannels, before, after):
    print('\nchecking game session STARTED')
    await notifyIfChangedPlayingState(bot, registeredChannels, after, before, '{} has started playing {}.')

async def checkGameSessionEnded(bot, registeredChannels, before, after):
    print('\nchecking game session ENDED')
    await notifyIfChangedPlayingState(bot, registeredChannels, before, after, '{} has stopped playing {}.')
