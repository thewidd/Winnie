import asyncio
import discord
import unittest
import builtins
from unittest.mock import AsyncMock, MagicMock
from ddt import ddt, data, unpack

import roleManagement as rm

@ddt
class TestGuildConfigs(unittest.TestCase):
    def setUp(self):
        self.roleMgr = rm.RoleManagement()

    def test_add_role_and_assign(self):        
        member = MagicMock(spec=discord.Member)
        member.add_roles = AsyncMock()
        member.guild.roles = []
        member.guild.roles = self.make_roles(names=('Role1', 'Role2', 'Role3'))
        member.roles = self.make_roles(names=('Everyone'))
        
        created_role = MagicMock(spec=discord.Role)
        member.guild.create_role = AsyncMock()
        member.guild.create_role.return_value = created_role
        game_name = 'Overwatch'

        asyncio.run(self.roleMgr.updateRoleForGame(member, gameName=game_name))

        member.guild.create_role.assert_called_with(name=game_name + ' Players', mentionable=True)
        member.add_roles.assert_called_with(created_role)

    def test_add_existing_role(self):        
        member = MagicMock(spec=discord.Member)
        member.add_roles = AsyncMock()
        game_name = 'Overwatch'
        role_name = game_name + ' Players'

        member.guild.roles = self.make_roles(names=('Role1', 'Role2', role_name))
        member.roles = self.make_roles(names=('Everyone'))

        asyncio.run(self.roleMgr.updateRoleForGame(member, gameName=game_name))

        self.assertFalse(member.guild.create_role.called)
        member.add_roles.assert_called_with(member.guild.roles[2])

    def test_dont_add_existing_role(self):
        member = MagicMock(spec=discord.Member)
        member.add_roles = AsyncMock()
        game_name = 'Overwatch'
        role_name = game_name + ' Players'
        
        member.guild.roles = self.make_roles(names=('Role1', 'Role2', role_name))
        member.roles = [member.guild.roles[2]] # the Overwatch Players role

        asyncio.run(self.roleMgr.updateRoleForGame(member, gameName=game_name))

        self.assertFalse(member.guild.create_role.called)
        self.assertFalse(member.add_roles.called)

    def make_roles(self, names: [str]) -> [discord.Role]:
        roles = []
        for role_name in names:
            role = MagicMock(spec=discord.Role)
            role.name = role_name
            roles.append(role)
        return roles
