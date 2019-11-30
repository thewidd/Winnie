import dataStore

async def registerChannel(ctx, registeredChannels):
    print(f'Register channel cmd. ChannelId: {ctx.channel.id}')
    if ctx.channel.id in registeredChannels.getIds():
        print('This channel has already been registered for notifications.')
        await ctx.channel.send('This channel has already been registerd for notifications.')
    else:
        registeredChannels.add(ctx.channel.id)
        await ctx.channel.send('I will now notify you when members of this server enter/exit game sessions! Happy gaming!')

async def unregisterChannel(ctx, registeredChannels):
    print(f'Unegister channel cmd: {ctx.channel.id}')
    print('current number of registered channels: ', len(registeredChannels), 'has channel with id: ', ctx.channel.id)
    try:
        registeredChannels.remove(ctx.channel.id)
        await ctx.channel.send('I will no longer tell you about gaming sessions. Sorry to bother...')
    except KeyError:
        print('No channel has been registerd before.')
        await ctx.channel.send('This channel has not been registerd yet.')
    print('new number of registered channels: ', len(registeredChannels))

async def registerUser(ctx, registeredUsers, user):
    print(f'Register user cmd. userId: {user.id}')
    if user.id in registeredUsers.getUserIds():
        if registeredUsers.isListeningToUser(user, ctx.message.author):
            print("You're already being notified about this user")
            # await user.m.send("You're already being notified about this user")
        else:
            registeredUsers.add(user, ctx.message.author)
            print('Added new user')
            sendDM(ctx.message.author, f'You will now receive notifications for {user.name}')
    else:
        registeredUsers.add(user, ctx.message.author)
        print('Added new user')
        await sendDM(ctx.message.author, f'You will now receive notifications for {user.name}')

# async def unregisterUser(ctx, registeredUsers, user):
#     print(f'Unegister user cmd: {ctx.channel.id}')
#     print('current number of registered channels: ', len(registeredUsers), 'has channel with id: ', ctx.channel.id)
#     try:
#         registeredUsers.remove(ctx.channel.id)
#         await ctx.channel.send('I will no longer tell you about gaming sessions. Sorry to bother...')
#     except KeyError:
#         print('No channel has been registerd before.')
#         await ctx.channel.send('This channel has not been registerd yet.')
#     print('new number of registered channels: ', len(registeredUsers))

async def sendDM(user, text):
    if user.dm_channel == None:
        await user.create_dm()
    await user.dm_channel.send(text)