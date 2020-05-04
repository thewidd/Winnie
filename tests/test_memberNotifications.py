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

# test utils
# from tests.asyncMock import AsyncMock

class TestMemberNotifications(unittest.TestCase):

    def setUp(self):
        self.bot = MagicMock()
        self.bot.user = 'Winnie'
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

    @mock.patch('model.guildConfigs.GuildConfigs', spec=gc.GuildConfigs)
    @mock.patch('discord.TextChannel.send', new_callable=AsyncMock)
    def test_notify_if_changed_playing_state(self, send_message, GuildConfigs):
        text_channel_id = 1
        self.bot.registeredChannels = MagicMock(**{'getIds.return_value': [text_channel_id, 2, 3]}, spec=rc.RegisteredChannels) # kept on making NonCallableMagicMock, so doing it this way actually works!
        # self.bot.registeredChannels. 
        self.bot.guildConfigs = GuildConfigs()
        self.memberNots = mn.MemberNotifications(self.bot)

        # multiple text channels (id == 100 not in the registered channels given from registeredChannels.getIds() above)
        member_name = 'Daxter'
        text_channels = [
            MagicMock(**{'id': text_channel_id}, spec=discord.TextChannel),
            MagicMock(**{'id': 100}, spec=discord.TextChannel) # id 100 is not in the registered ids (1, 2 3)
        ]
        for text_channel in text_channels:
            text_channel.send = AsyncMock()
        shared_member_info = { 'guild.text_channels': text_channels }

        before = MagicMock(**shared_member_info, spec=discord.Member)
        before.name = member_name # issue with constructor also accepting param called 'name'
        after = MagicMock(**shared_member_info, spec=discord.Member)
        after.name = member_name

        # musicActivity = MagicMock(spec=discord.Spotify)
        game_name = 'Overwatch'
        playingActivity = MagicMock(**{
            'type': discord.ActivityType.playing
        }, spec=discord.Activity)
        playingActivity.name = 'Overwatch' # issue with constructor also accepting param called 'name'

        # out-of-game to in-game (should notify)
        before.activities = []
        after.activities = [playingActivity]

        started_playing_format = '{} has started playing {}.'
        # stopped_playing_format = '{} has stopped playing {}.'

        asyncio.run(self.memberNots._MemberNotifications__notifyIfChangedPlayingState(possibleInGameMember=after, possibleOutOfGameMember=before, notificationTextFormat=started_playing_format))
        
        text_channels[0].send.assert_called_with(started_playing_format.format(member_name, game_name))
        self.assertEqual(text_channels[0].send.call_count, 1)
        self.assertFalse(text_channels[1].send.called)

        # in-game to out-of-game (should notify)
        # one playing activity to another playing activity (should not notify)
        # one non-playing activity to another non-playing activity (should not notify)

    def test_notify_based_on_channels(self):
        # has channels registered (notify)

        # has no channels registered (don't notify)
        pass

    def test_create_role_for_players_of_game_config(self):
        # config is True (update role)

        # config is False (don't update role)
        pass