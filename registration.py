import dataStore

async def registerChannel(ctx, registeredChannelIds):
    print(f'Register channel cmd. ChannelId: {ctx.channel.id}')
    if ctx.channel.id in registeredChannelIds:
        print('This channel has already been registered for notifications.')
        await ctx.channel.send('This channel has already been registerd for notifications.')
    else:
        registeredChannelIds.add(ctx.channel.id)
        await ctx.channel.send('I will now notify you when members of this server enter/exist game sessions! Happy gaming!')
    dataStore.write(registeredChannelIds)

async def unregisterChannel(ctx, registeredChannelIds):
    print(f'Unegister channel cmd: {ctx.channel.id}')
    print('current number of registered channels: ', len(registeredChannelIds), 'has channel with id: ', ctx.channel.id)
    try:
        registeredChannelIds.remove(ctx.channel.id)
        await ctx.channel.send('I will no longer tell you about gaming sessions. Sorry to bother...')
    except KeyError:
        print('No channel has been registerd before.')
        await ctx.channel.send('This channel has not been registerd yet.')

    print('new number of registered channels: ', len(registeredChannelIds))
    dataStore.write(registeredChannelIds)