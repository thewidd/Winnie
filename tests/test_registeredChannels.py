import asyncio
import discord
import unittest
import builtins
from unittest.mock import AsyncMock, MagicMock, patch
from ddt import ddt, data, unpack

import model.registeredChannels as rc

class TestRegisteredChannels(unittest.TestCase):

    def setUp(self):
        self.bot = MagicMock()
        self.reg_channels = rc.RegisteredChannels(self.bot)

    @patch('builtins.open')
    @patch('json.dump')
    def test_add_remove(self, dump, file_open):
        self.assertEqual(self.reg_channels.getIds(), set())

        self.reg_channels.add(1)
        self.assertEqual(self.reg_channels.getIds(), {1})
        self.assertTrue(1 in self.reg_channels)

        self.reg_channels.remove(1)
        self.assertEqual(self.reg_channels.getIds(), set())
        self.assertTrue(1 not in self.reg_channels)

        self.reg_channels.remove(1)
        self.assertEqual(self.reg_channels.getIds(), set())

        self.reg_channels.add(1)
        self.reg_channels.add(1)
        self.reg_channels.add(2)
        self.reg_channels.add(3)
        self.assertEqual(self.reg_channels.getIds(), {1, 2, 3})

        self.reg_channels.remove(2)
        self.assertEqual(self.reg_channels.getIds(), {1, 3})

        self.reg_channels.remove(1)
        self.reg_channels.remove(3)
        self.assertEqual(self.reg_channels.getIds(), set())

    @patch('builtins.open')
    @patch('json.dump')
    def test_add_writes(self, dump, file_open):
        self.reg_channels.add(1)
        file_open.assert_called_with('guildSettings.json', 'w')
        dump.assert_called_with({'registeredChannelIds': [1]}, file_open().__enter__())
        self.assertEqual(dump.call_count, 1)

        self.reg_channels.add(2)
        file_open.assert_called_with('guildSettings.json', 'w')
        self.assertEqual(file_open.call_count, 3) # the third opening comes from 'file_open().__enter__()' above
        dump.assert_called_with({'registeredChannelIds': [1, 2]}, file_open().__enter__())
        self.assertEqual(dump.call_count, 2)

    @patch('builtins.open')
    @patch('json.dump')
    def test_remove_writes(self, dump, file_open):
        self.reg_channels._RegisteredChannels__registeredChannelIds = [1, 2]

        self.reg_channels.remove(1)
        file_open.assert_called_with('guildSettings.json', 'w')
        dump.assert_called_with({'registeredChannelIds': [2]}, file_open().__enter__())
        self.assertEqual(dump.call_count, 1)

        self.reg_channels.remove(2)
        file_open.assert_called_with('guildSettings.json', 'w')
        self.assertEqual(file_open.call_count, 3) # the third opening comes from 'file_open().__enter__()' above
        dump.assert_called_with({'registeredChannelIds': []}, file_open().__enter__())
        self.assertEqual(dump.call_count, 2)

    @patch('json.dump')
    @patch('json.load')
    def test_initialize(self, load, dump):
        pass
        
