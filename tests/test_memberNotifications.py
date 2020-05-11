import unittest
from unittest import mock
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
import discord
from ddt import ddt, data, unpack

# code to mock/test
import model.registeredChannels as rc
import memberNotifications as mn
import model.guildConfigs as gc
import roleManagement as rm

started_playing_format = '{} has started playing {}.'
stopped_playing_format = '{} has stopped playing {}.'

def make_member_playing_activity(game_name: str) -> discord.Activity:
    return make_member_activity(activity_type=discord.ActivityType.playing, spec=discord.Activity, activity_name=game_name)

def make_member_spotify_activity() -> discord.Activity:
    return make_member_activity(activity_type=discord.ActivityType.listening, spec=discord.Spotify, activity_name='Spotify')

def make_member_activity(activity_type: discord.ActivityType, spec, activity_name: str) -> discord.Activity:
    playingActivity = MagicMock(**{
        'type': activity_type
    }, spec=spec)
    playingActivity.name = activity_name # issue with constructor also accepting param called 'name'
    return playingActivity

@ddt
class TestMemberNotifications(unittest.TestCase):

    def setUp(self):
        self.bot = MagicMock()
        self.bot.user = 'Winnie'

        # multiple text channels (id == 100 not in the registered channels given from registeredChannels.getIds() above)
        self.member_text_channel_id = 2
        self.bot.registeredChannels = MagicMock(**{'getIds.return_value': [1, self.member_text_channel_id, 3]}, spec=rc.RegisteredChannels) # kept on making NonCallableMagicMock, so doing it this way actually works!
        self.guildConfigs = MagicMock(spec=gc.GuildConfigs)
        self.bot.guildConfigs = self.guildConfigs
        self.roleManagement = MagicMock(spec=rm.RoleManagement)
        self.bot.roleManagement = self.roleManagement

        self.memberNots = mn.MemberNotifications(self.bot)

    @mock.patch('memberNotifications.MemberNotifications._MemberNotifications__checkGameSessionStarted')
    @mock.patch('memberNotifications.MemberNotifications._MemberNotifications__checkGameSessionEnded')
    def test_notify_if_gaming_state_changed(self, checkSessionStarted, checkSessionEnded):
        before = MagicMock()
        after = MagicMock()
        asyncio.run(self.memberNots.notifyIfGamingStateChanged(before, after))
        checkSessionStarted.assert_called_with(before, after)
        checkSessionEnded.assert_called_with(before, after)

    @mock.patch('memberNotifications.MemberNotifications._MemberNotifications__notifyIfChangedPlayingState')
    def test_check_game_session_changed_methods(self, notify):
        before = MagicMock()
        after = MagicMock()
        asyncio.run(self.memberNots._MemberNotifications__checkGameSessionStarted(before, after))
        notify.assert_called_with(after, before, '{} has started playing {}.')
    
        asyncio.run(notify.mock_reset())
        asyncio.run(self.memberNots._MemberNotifications__checkGameSessionEnded(before, after))
        notify.assert_called_with(before, after, '{} has stopped playing {}.')

    @data(None, make_member_spotify_activity())
    def test_notify_started_playing(self, additional_activity):
        # out-of-game to in-game (should notify)
        out_of_game_member, in_game_member = self.make_member_before_after(in_game_before=False, in_game_after=True, additional_activity=additional_activity)
        asyncio.run(self.memberNots._MemberNotifications__notifyIfChangedPlayingState(possibleInGameMember=in_game_member, possibleOutOfGameMember=out_of_game_member, notificationTextFormat=started_playing_format))
        in_game_member.guild.text_channels[0].send.assert_called_with(started_playing_format.format('Daxter', 'Overwatch'))
        self.assertEqual(in_game_member.guild.text_channels[0].send.call_count, 1)
        self.assertFalse(in_game_member.guild.text_channels[1].send.called)

        # both possibilties get invoked to check if either happened. So pass out_of_game as a possible in_game as well
        for channel in in_game_member.guild.text_channels:
            channel.reset_mock()
        asyncio.run(self.memberNots._MemberNotifications__notifyIfChangedPlayingState(possibleInGameMember=out_of_game_member, possibleOutOfGameMember=in_game_member, notificationTextFormat=stopped_playing_format))
        for channel in in_game_member.guild.text_channels:
            self.assertFalse(channel.send.called) 

    @data(None, make_member_spotify_activity())
    def test_notify_stopped_playing(self, additional_activity):
        # in-game to out-of-game (should notify)
        in_game_member, out_of_game_member = self.make_member_before_after(in_game_before=True, in_game_after=False, additional_activity=additional_activity)
        asyncio.run(self.memberNots._MemberNotifications__notifyIfChangedPlayingState(possibleInGameMember=in_game_member, possibleOutOfGameMember=out_of_game_member, notificationTextFormat=stopped_playing_format))
        in_game_member.guild.text_channels[0].send.assert_called_with(stopped_playing_format.format('Daxter', 'Overwatch'))
        self.assertEqual(in_game_member.guild.text_channels[0].send.call_count, 1)
        self.assertFalse(in_game_member.guild.text_channels[1].send.called) # this channel is not registered, so it was not notified

        # both possibilties get invoked to check if either happened. So pass out_of_game as a possible in_game as well
        for channel in in_game_member.guild.text_channels:
            channel.reset_mock()
        asyncio.run(self.memberNots._MemberNotifications__notifyIfChangedPlayingState(possibleInGameMember=out_of_game_member, possibleOutOfGameMember=in_game_member, notificationTextFormat=stopped_playing_format))
        for channel in in_game_member.guild.text_channels:
            self.assertFalse(channel.send.called) 

    def test_activity_update_still_playing(self):
        # one playing activity to another playing activity (should not notify).
        # a good example of this is with Modern Warfare: Warzone, application_id would change inbetween lobby vs game vs loading, etc. If still playing, don't notify
        before, after = self.make_member_before_after(in_game_before=True, in_game_after=True)
        after.activities[0].name = before.activities[0].name + '- In Lobby'
        after.activities[0].id = before.activities[0].application_id + 1
        # the above changes should have no effect. Only the "playing" activity type should matter

        asyncio.run(self.memberNots._MemberNotifications__notifyIfChangedPlayingState(possibleInGameMember=after, possibleOutOfGameMember=before, notificationTextFormat=stopped_playing_format))
        for channel in after.guild.text_channels:
            self.assertFalse(channel.send.called) 

    @data((False, False), (False, True), (True, False), (True, True))
    @unpack
    def test_music_activity_change(self, music_started, playing_game):
        before, after = self.make_member_before_after(in_game_before=True, in_game_after=True)
        # before and after both will have the game activity, now we add music, shoud be no notification
        if music_started:
            after.activities.append(make_member_spotify_activity())
        else: # music stopped
            before.activities.append(make_member_spotify_activity())
        
        asyncio.run(self.memberNots._MemberNotifications__notifyIfChangedPlayingState(possibleInGameMember=after, possibleOutOfGameMember=before, notificationTextFormat=stopped_playing_format))
        for channel in after.guild.text_channels:
            self.assertFalse(channel.send.called)

    def test_create_role_for_players_of_game_config(self):
        self.roleManagement.updateRoleForGame = AsyncMock()
        # config disabled, player started gaming --> don't update role
        self.guildConfigs.getConfig.return_value = False
        out_of_game_member, in_game_member = self.make_member_before_after(in_game_before=False, in_game_after=True)
        asyncio.run(self.memberNots._MemberNotifications__notifyIfChangedPlayingState(possibleInGameMember=in_game_member, possibleOutOfGameMember=out_of_game_member, notificationTextFormat=started_playing_format))
        self.assertFalse(self.roleManagement.updateRoleForGame.called) 

        # config enabled, no play state change --> don't update role
        self.guildConfigs.getConfig.return_value = True
        out_of_game_member, in_game_member = self.make_member_before_after(in_game_before=True, in_game_after=True)
        asyncio.run(self.memberNots._MemberNotifications__notifyIfChangedPlayingState(possibleInGameMember=in_game_member, possibleOutOfGameMember=out_of_game_member, notificationTextFormat=started_playing_format))
        self.assertFalse(self.roleManagement.updateRoleForGame.called) 

        # config enabled, started playing --> update role
        out_of_game_member, in_game_member = self.make_member_before_after(in_game_before=False, in_game_after=True)
        asyncio.run(self.memberNots._MemberNotifications__notifyIfChangedPlayingState(possibleInGameMember=in_game_member, possibleOutOfGameMember=out_of_game_member, notificationTextFormat=started_playing_format))
        self.roleManagement.updateRoleForGame.assert_called_with(in_game_member, 'Overwatch', [out_of_game_member.guild.text_channels[0]])

        # config enabled, play state change, but no registered channels --> don't update role
        self.roleManagement.updateRoleForGame = AsyncMock()
        out_of_game_member, in_game_member = self.make_member_before_after(in_game_before=False, in_game_after=True)
        self.bot.registeredChannels.getIds.return_value = [1, 3] # remove the text channel that this user is in that is normally registered
        asyncio.run(self.memberNots._MemberNotifications__notifyIfChangedPlayingState(possibleInGameMember=in_game_member, possibleOutOfGameMember=out_of_game_member, notificationTextFormat=started_playing_format))
        self.assertTrue(self.member_text_channel_id not in self.bot.registeredChannels.getIds.return_value)
        self.assertFalse(self.roleManagement.updateRoleForGame.called) 

    def make_member_before_after(self, in_game_before: bool, in_game_after: bool, additional_activity: discord.Activity = None) -> (discord.Member, discord.Member):
        member_name = 'Daxter'
        text_channels = [
            MagicMock(**{'id': self.member_text_channel_id}, spec=discord.TextChannel),
            MagicMock(**{'id': 100}, spec=discord.TextChannel) # id 100 is not in the registered ids (1, 2 3)
        ]
        for text_channel in text_channels:
            text_channel.send = AsyncMock()
        shared_member_info = { 'guild.text_channels': text_channels }

        before = MagicMock(**shared_member_info, spec=discord.Member)
        before.name = member_name # issue with constructor also accepting param called 'name'
        after = MagicMock(**shared_member_info, spec=discord.Member)
        after.name = member_name

        playingActivity = make_member_playing_activity('Overwatch')

        before.activities = [playingActivity] if in_game_before else []
        after.activities = [playingActivity] if in_game_after else []
        
        if additional_activity:
            before.activities.append(additional_activity)
            after.activities.append(additional_activity)

        return before, after
