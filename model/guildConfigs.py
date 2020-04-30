import json

class GuildConfigs:
    def initialize(self):
        self.__configs = self.read()
        self.supportedConfigKeys = {'createRoleForPlayersOfGame'}

    def read(self):
        configs = {}
        with open('guildConfigs.json') as file:
            try:
                data = json.load(file)
                configs = data['guildConfigs']
            except Exception:
                configs = {}

        print(configs)
        return configs

    def write(self, guildConfigs):
        with open('guildConfigs.json', 'w') as file:
            dataToSave = {'guildConfigs': guildConfigs}
            json.dump(dataToSave, file)

    def setConfig(self, guildId: int, key: str, val: bool):
        self.__configs.setdefault(str(guildId), {})[key] = val
        self.write(self.__configs) # update DB
    
    def getConfig(self, guildId: int, key: str) -> bool:
        try:
            return self.__configs[str(guildId)][key]
        except KeyError:
            return False