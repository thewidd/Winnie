from mongoengine import Document, StringField, BooleanField, ListField

class GuildSettings(Document):
    guild_id = StringField(required=True, max_length=100)
    notification_channels = ListField(StringField(max_length=100))
    create_role_for_game_players = BooleanField()
