import discord

class MemberNotifications:
    def __init__(self):
        self.subscriptions = {}

    def subscribe(self, requestingUser, members):
        for member in members:
            self.subscriptions[member.id] = requestingUser.id

    async def notifySubscribedMembers(self, updatedMember, notificationText):
        print(f'Sending notification about memberId: {updatedMember.id}')
        # await updatedMember.create_dm()
        # await updatedMember.dm_channel_send(notificationText)