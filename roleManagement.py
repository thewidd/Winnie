import discord
import discord.member

class RoleManagement:
    def __init__(self, guildConfigs):
        self.__guildConfigs = guildConfigs

    async def updateRoleForGame(self, member: discord.Member, gameName: str):
        # I can also do role.id, might be good to remember which roles I've created and compare against that instead?
        roleName = self.__roleNameForGame(gameName)
        role = None

        # todo: find a better way to create roles. Check if Winnie has ever created a role and knows about it. Only then should I create a role. Or at least setup permissions for that new role correctly
        # saying that someone else is managing the role (Winnie)
        if roleName not in [guildRole.name for guildRole in member.guild.roles]:
            print(f'no role with name: {roleName} found')
            role = await self.__createRole(roleName, member.guild)
        # check if this person needs to be added to role
        if role and role not in member.roles:
            print('player not found in role, adding them')
            await member.add_roles(role)

    def __roleNameForGame(self, gameName: str) -> str:
        return gameName + ' Players'

    async def __createRole(self, roleName: str, guild: discord.Guild):
        
        try:
            role = await guild.create_role(name=roleName, mentionable=True)
            print(f'Created role {roleName}')
        except discord.InvalidArgument:
            print('Invalid argument passed in to create_role API')
        except discord.Forbidden as e:
            print(e.text)
        except discord.HTTPException:
            print(e.text)
        return role