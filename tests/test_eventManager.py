import unittest
from unittest import mock
from unittest.mock import patch
from unittest.mock import MagicMock
import eventManager as em
from tests.asyncMock import AsyncMock
import asyncio
import model.registeredChannels as rc
import memberNotifications as mn
import model.guildConfigs as gc

class TestBot(unittest.TestCase):

    def setUp(self):
        self.bot = MagicMock()
        self.bot.user = 'Winnie'
        self.eventManager = em.EventManager(self.bot)

    @mock.patch('model.registeredChannels.RegisteredChannels', spec=rc.RegisteredChannels)
    @mock.patch('model.guildConfigs.GuildConfigs', spec=gc.GuildConfigs)
    def test_on_ready(self, RegisteredChannels, GuildConfigs):
        self.bot.registeredChannels = RegisteredChannels()
        self.bot.guildConfigs = GuildConfigs()

        asyncio.run(self.eventManager.on_ready())
        self.bot.registeredChannels.initialize.assert_called_with()
        self.bot.guildConfigs.initialize.assert_called_with()

    @mock.patch('memberNotifications.MemberNotifications', spec=mn.MemberNotifications)
    def test_on_member_update(self, MemberNotifications):
        self.bot.memberNotifications = MemberNotifications(self.bot)
        self.bot.GUILD_IDS_TO_IGNORE = [456, 789]

        before = MagicMock(**{'guild.id': 123})
        after = MagicMock()
        asyncio.run(self.eventManager.on_member_update(before, after))
        self.bot.memberNotifications.notifyIfGamingStateChanged.assert_called_with(before, after)

    @mock.patch('model.registeredChannels.RegisteredChannels', spec=rc.RegisteredChannels)
    def test_on_guild_channel_delete(self, RegisteredChannels):
        channel = MagicMock(**{'channel.id': 123})
        self.bot.registeredChannels = RegisteredChannels()

        # does contain channel
        self.bot.registeredChannels.__contains__.return_value = True
        asyncio.run(self.eventManager.on_guild_channel_delete(channel))
        self.bot.registeredChannels.remove.assert_called_with(channel.id)

        self.bot.registeredChannels.reset_mock()
        # does not contain channel
        self.bot.registeredChannels.__contains__.return_value = False
        asyncio.run(self.eventManager.on_guild_channel_delete(channel))
        self.assertFalse(self.bot.registeredChannels.remove.called)