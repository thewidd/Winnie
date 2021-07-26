import discord
import model.guildConfigs as gf
import roleManagement as rm
import logging

import datetime

class MemberNotifications:
    def __init__(self, bot):
        self.__bot = bot
        self.__registeredChannels = bot.registeredChannels
        self.__guildConfigs = bot.guildConfigs
        self.__roleManagement = bot.roleManagement

    async def notifyIfGamingStateChanged(self, before, after):
        await self.__checkGameSessionStarted(before, after)
        notifyIfStopped = self.__guildConfigs.getConfig(before.guild.id, 'notifyStoppedPlaying')
        if notifyIfStopped == None or notifyIfStopped:
            await self.__checkGameSessionEnded(before, after)

    async def __checkGameSessionStarted(self, before, after):
        await self.__notifyIfChangedPlayingState(after, before, '{} has started playing {}.', logAction='Started')

    async def __checkGameSessionEnded(self, before, after):
        await self.__notifyIfChangedPlayingState(before, after, '{} has stopped playing {}.', logAction='Stopped')

    async def __notifyIfChangedPlayingState(self, possibleInGameMember, possibleOutOfGameMember, notificationTextFormat, logAction: str):
        '''
        Send a notification to all registered channels if a user has gone from in-game to out-of-game or vice
        '''    
        possibleInGameIsInGame, inGameActivity = self.__isPlaying(possibleInGameMember)
        possibleOutOfGameIsOutOfGame = not self.__isPlaying(possibleOutOfGameMember)[0]
        # print(f'possibleInGameIsInGame: {possibleInGameIsInGame}, possibleOutOfGameIsOutOfGame: {possibleOutOfGameIsOutOfGame}')

        channelsToNotify = []
        if possibleInGameIsInGame and possibleOutOfGameIsOutOfGame:
            activityForMessage = inGameActivity
            channelsToNotify = [channel for channel in possibleInGameMember.guild.text_channels if channel.id in self.__registeredChannels.getIds()]

        if channelsToNotify:
            # print(f'processing guildId: {possibleInGameMember.guild.id}')
            if self.__guildConfigs.getConfig(possibleInGameMember.guild.id, 'createRoleForPlayersOfGame'):
                await self.__roleManagement.update_role_for_game(possibleInGameMember, activityForMessage.name, channelsToNotify)

            print(f"{datetime.datetime.now()} - [{logAction} playing. GuildId: [{possibleInGameMember.guild.id}]MemberId: [{possibleInGameMember.id}]. Notifying channelIds: [{ ', '.join([str(channel.id) for channel in channelsToNotify]) }]")
            for channelToNotify in channelsToNotify:
                await channelToNotify.send(self.__text_to_send(notificationTextFormat, possibleInGameMember, activityForMessage))

    def __text_to_send(self, notificationTextFormat: str, member: discord.Member, activity: discord.Activity) -> str:
        send_text = notificationTextFormat.format(member.name, activity.name)
        if self.__guildConfigs.getConfig(guildId=member.guild.id, key='tagRolesInNotification'):
            game_role = self.__roleManagement.get_role(guild=member.guild, game_name=activity.name)
            if game_role:
                send_text += f' ({game_role.mention})'
        return send_text

    def __isPlaying(self, member):
        '''
        Return: tuple of (isPlaying, member.activity object of the playing activity)
        '''
        gameActivities = []
        for activity in member.activities:
            if member.status == discord.Status.online and self.__isPlayingGameActivity(activity):
                gameActivities.append(activity)
        # gameActivities = [activity for activity in member.activities if self.__isPlayingGameActivity(activity)]
        return (len(gameActivities) != 0, next(iter(gameActivities), None))

    def __isPlayingGameActivity(self, activity):
        return hasattr(activity, 'type') and activity.type == discord.ActivityType.playing

    
