import unittest
from unittest.mock import patch
import eventManager

class Mock:
    pass

class TestBot(unittest.TestCase):

    def setUp(self):
        self.eventManager = eventManager.EventManager('Winnie')

    async def test_on_ready(self):
        with patch('model.registeredChannels.RegisteredChannels.initialize') as mock_reg_chnl_initialize:
            with patch('model.guildConfigs.GuildConfigs.initialize') as mock_guild_cfg_initialize:
                await self.eventManager.on_ready()
                mock_reg_chnl_initialize.assert_called_with(1)
                mock_guild_cfg_initialize.assert_called_with(2)

    async def test_on_member_update(self):
        with patch('memberNotifications.MemberNotifications.notifyIfGamingStateChanged') as mock_notify:
            before = Mock()
            after = Mock()
            await self.eventManager.on_member_update(before, after)
            mock_notify.assert_called_with(before, after)

            # these tests are not working. I need unittest to await the test_* methods since most of my methods are async responses

    async def test_on_guild_channel_delete(self):
        # def __contains__(self, key):
        #     return key in self.__registeredChannelIds
        channel = Mock()
        channel.id = 123

        with patch('model.registeredChannels.RegisteredChannels.remove') as mock_remove:
            with patch('model.registeredChannels.RegisteredChannels.__contains__') as mock_contains:
                mock_contains.return_value = True
                self.eventManager.test_on_guild_channel_delete(channel)
                mock_remove.assert_called_with(channel.id)
            
        with patch('model.registeredChannels.RegisteredChannels.remove') as mock_remove:
            with patch('model.registeredChannels.RegisteredChannels.__contains__') as mock_contains:
                mock_contains.return_value = False
                self.eventManager.test_on_guild_channel_delete(channel)
                self.assertFalse(mock_remove.called)