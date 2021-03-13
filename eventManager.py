
class EventManager: 
    def __init__(self, bot):
        self.bot = bot
        self.initialized = False

    async def on_ready(self):
        print('We have logged in as {0.user}'.format(self.bot))
        if not self.initialized:
            self.initialized = True
            self.bot.registeredChannels.initialize()
            self.bot.guildConfigs.initialize()
            # registeredUsers.initialize()
        
    # send message if a member's activity state has changed
    async def on_member_update(self, before, after):
        if before.guild.id not in self.bot.GUILD_IDS_TO_IGNORE:
            print(f'Received on_member_update for {before.id}')
            await self.bot.memberNotifications.notifyIfGamingStateChanged(before, after)

    # update registered channels when one is removed
    async def on_guild_channel_delete(self, channel):
        print(f"channel removed with channeldId: {channel.id}")
        if channel.id in self.bot.registeredChannels:
            print(f"A channel that's registered was removed. channeldId: {channel.id}")
            self.bot.registeredChannels.remove(channel.id)

    async def on_command_error(self, ctx, error):
        await ctx.send(error)
        print(f'Command error: {error}')