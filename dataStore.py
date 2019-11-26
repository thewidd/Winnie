import json

def read():
    registeredChannelIds = {}
    with open('guildSettings.json') as file:
        try:
            data = json.load(file)
            registeredChannelIds = data['registeredChannelIds']
        except:
            registeredChannelIds = []

    print (json.dumps(registeredChannelIds))
    return registeredChannelIds

def write(registeredChannelIds):
    with open('guildSettings.json', 'w') as file:
        dataToSave = {'registeredChannelIds': list(registeredChannelIds)}
        json.dump(dataToSave, file)