import unittest
from unittest import mock
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
import discord

# code to mock/test
import model.registeredChannels as rc
import memberNotifications as mn
import model.guildConfigs as gc
import roleManagement as rm

started_playing_format = '{} has started playing {}.'
stopped_playing_format = '{} has stopped playing {}.'

class TestMemberNotifications(unittest.TestCase):

    def setUp(self):
        self.bot = MagicMock()
        self.bot.user = 'Winnie'

        # multiple text channels (id == 100 not in the registered channels given from registeredChannels.getIds() above)
        self.member_text_channel_id = 1
        self.registered_channel_ids = [self.member_text_channel_id, 2, 3]
        self.bot.registeredChannels = MagicMock(**{'getIds.return_value': [self.member_text_channel_id, 2, 3]}, spec=rc.RegisteredChannels) # kept on making NonCallableMagicMock, so doing it this way actually works!
        self.bot.guildConfigs = MagicMock(spec=gc.GuildConfigs)

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

    @mock.patch('discord.TextChannel.send', new_callable=AsyncMock)
    def test_notify_started_playing(self, send_message):
        # out-of-game to in-game (should notify)
        out_of_game_member, in_game_member = self.make_member_before_after(in_game_before=False, in_game_after=True)
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

    @mock.patch('discord.TextChannel.send', new_callable=AsyncMock)
    def test_notify_stopped_playing(self, send_message):
        # in-game to out-of-game (should notify)
        in_game_member, out_of_game_member = self.make_member_before_after(in_game_before=True, in_game_after=False)
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

    @mock.patch('discord.TextChannel.send', new_callable=AsyncMock)
    def test_activity_update_still_playing(self, send_message):
        # one playing activity to another playing activity (should not notify)
        pass

    @mock.patch('discord.TextChannel.send', new_callable=AsyncMock)
    def test_activity_update_still_not_playing(self, send_message):
        # one non-playing activity to another non-playing activity (should not notify)
        pass

    def test_notify_based_on_channels(self):
        # has channels registered (notify)

        # has no channels registered (don't notify)
        pass

    def test_create_role_for_players_of_game_config(self):
        # config is True (update role)

        # config is False (don't update role)
        pass

    def make_member_before_after(self, in_game_before: bool, in_game_after: bool) -> (discord.Member, discord.Member):
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

        playingActivity = self.make_member_playing_activity('Overwatch')

        before.activities = [playingActivity] if in_game_before else []
        after.activities = [playingActivity] if in_game_after else []

        return before, after

    def make_member_playing_activity(self, game_name: str) -> discord.Activity:
        return self.make_member_activity(activity_type=discord.ActivityType.playing, spec=discord.Activity, activity_name=game_name)

    def make_member_spotify_activity(self) -> discord.Activity:
        return self.make_member_activity(activity_type=discord.ActivityType.listening, spec=discord.Spotify, activity_name='Spotify')

    def make_member_activity(self, activity_type: discord.ActivityType, spec, activity_name: str) -> discord.Activity:
        playingActivity = MagicMock(**{
            'type': activity_type
        }, spec=spec)
        playingActivity.name = activity_name # issue with constructor also accepting param called 'name'
        return playingActivity

