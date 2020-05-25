import discord

class RoleUpdate:
    def __init__(self, created_role: discord.Role):
        self.created_role = created_role

class RoleManagement:
    async def updateRoleForGame(self, member: discord.Member, gameName: str, channels_to_notify: [discord.TextChannel]):
        # I can also do role.id, might be good to remember which roles I've created and compare against that instead?
        roleName = self._roleNameForGame(gameName)
        role = next((role for role in member.guild.roles if role.name == roleName), None)

        # todo: find a better way to create roles. Check if Winnie has ever created a role and knows about it. 
        # Only then should I create a role. Or at least setup permissions for that new role correctly
        # saying that someone else is managing the role (Winnie)
        if not role:
            print(f'no role with name: {roleName} found')
            role = await self._createRole(roleName, member.guild, channels_to_notify)
            if role:
                for text_channel in channels_to_notify:
                    await text_channel.send(f'Created new role: {role.mention}')
            
        # check if this person needs to be added to role
        if role and role not in member.roles:
            print('player not found in role, adding them')
            try:
                await member.add_roles(role)
            except discord.errors.Forbidden as e:
                await self._notify_permissions_failure(channels_to_notify) 

    def _roleNameForGame(self, gameName: str) -> str:
        return gameName + ' Players'

    async def _createRole(self, roleName: str, guild: discord.Guild, channels_to_notify: [discord.TextChannel]) -> discord.Role:
        role = None
        try:
            role = await guild.create_role(name=roleName, mentionable=True)
            print(f'Created role {roleName}')
        except discord.InvalidArgument:
            print('Invalid argument passed in to create_role API')
        except discord.Forbidden as e:
            await self._notify_permissions_failure(channels_to_notify)
        except discord.HTTPException as e:
            print(e.text)
        return role

    async def _notify_permissions_failure(self, channels_to_notify: [discord.TextChannel]):
        for text_channel in channels_to_notify:
            await text_channel.send(f'Winnie was unable to make changes to roles. Please make sure Winnie has the "Manage Roles" permission enabled in Server Settings -> Roles -> Winnie -> Manage Roles. Alternatively, turn off the "createRoleForPlayersOfGame" config via set_config.')