import asyncio
import discord
import unittest
import builtins
from unittest.mock import AsyncMock, MagicMock, patch
from ddt import ddt, data, unpack
from datetime import timedelta

import model.guildConfigs as gc

@ddt
class TestGuildConfigs(unittest.TestCase):
    def setUp(self):
        self.configs = gc.GuildConfigs()

    @patch('builtins.open')
    @patch('json.dump')
    @patch('json.load')
    def test_get_set_config(self, load, dump, file_open):
        # set some keys for guild1
        guild1_id = 123
        config = 'config'
        other_config = 'other_config'
        self.assertFalse(self.configs.getConfig(guildId=guild1_id, key=config))
        self.assertFalse(self.configs.getConfig(guildId=guild1_id, key=other_config))

        self.configs.setConfig(guild1_id, config, True)
        self.assertTrue(self.configs.getConfig(guildId=guild1_id, key=config))
        self.assertFalse(self.configs.getConfig(guildId=guild1_id, key=other_config))

        self.configs.setConfig(guild1_id, config, False)
        self.configs.setConfig(guild1_id, other_config, True)
        self.assertFalse(self.configs.getConfig(guildId=guild1_id, key=config))
        self.assertTrue(self.configs.getConfig(guildId=guild1_id, key=other_config))

        # set some keys for guild2
        guild2_id = 456
        self.configs.setConfig(guild2_id, config, True)
        self.configs.setConfig(guild2_id, other_config, False)

        # assert guild2 is setup correctly
        self.assertTrue(self.configs.getConfig(guildId=guild2_id, key=config))
        self.assertFalse(self.configs.getConfig(guildId=guild2_id, key=other_config))
        # assert guild1 has not been changed by making changes to guild2 (these are inverse from guild2)
        self.assertFalse(self.configs.getConfig(guildId=guild1_id, key=config))
        self.assertTrue(self.configs.getConfig(guildId=guild1_id, key=other_config))

    @patch('builtins.open')
    @patch('json.dump')
    @data(True, False)
    def test_set_config_writes(self, is_config_enabled, dump, file_open):
        configs_dict = { 
            '456': { 'some_config': True, 'other_config': False },
            '789': {}
        }
        self.configs._configs = configs_dict
        guild_id = 123
        config_key = 'config_key'

        self.assertFalse(str(guild_id) in configs_dict)
        self.assertEqual(len(configs_dict), 2)
        self.configs.setConfig(guild_id, config_key, val=is_config_enabled)
        self.assertTrue(str(guild_id) in configs_dict)
        self.assertEqual(len(configs_dict), 3)

        file_open.assert_called_with('guildConfigs.json', 'w')
        self.assertEqual(dump.call_args.args[0], {'guildConfigs': configs_dict})
        self.assertEqual(dump.call_count, 1)

    def test_supported_config_keys(self):
        self.assertEqual(self.configs.supportedConfigKeys, {'createRoleForPlayersOfGame'})

    @patch('builtins.open')
    @patch('json.dump')
    @patch('json.load')
    def test_initialize(self, load, dump, file_open):
        guild_id = '456'
        config_key1 = 'other_config'
        config_key2 = 'key'
        load.return_value = {
            'guildConfigs': { 
                guild_id: { 'some_config': True, config_key1: False, config_key2: True },
                '789': {}
            }
        }
        self.configs.initialize()
        self.assertEqual(dump.called, 0) # nothing should do any writing/dump here
        self.assertEqual(load.call_args.args[0], file_open().__enter__())
        self.assertFalse(self.configs.getConfig(guild_id, config_key1))
        self.assertTrue(self.configs.getConfig(guild_id, config_key2))