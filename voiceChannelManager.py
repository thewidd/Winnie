import discord
from model.guildConfigs import GuildConfigs

class VoiceChannelManager:
    def __init__(self, bot):
        self.guild_configs = bot.guildConfigs

    async def on_guild_configs_updated(self, guild: discord.Guild):
        # category_exists = False
        voice_channel_creator_name = 'Create For Current Game'
        creator_voice_channel = next((voice_channel for voice_channel in guild.voice_channels if voice_channel.name == voice_channel_creator_name), None)

        if self.guild_configs.getConfig(guild.id, key=self.guild_configs.onDemandVoiceChannelPerGame):
            if not creator_voice_channel:
                await guild.create_voice_channel(name=voice_channel_creator_name)
        else:
            if creator_voice_channel:
                await creator_voice_channel.delete()