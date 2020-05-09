import json

class GuildConfigs:
    supportedConfigKeys = {'createRoleForPlayersOfGame'}

    def __init__(self):
        self._configs = {}

    def initialize(self):
        self._configs = self._read()

    def _read(self) -> dict:
        configs = {}
        with open('guildConfigs.json') as file:
            try:
                data = json.load(file)
                configs = data['guildConfigs']
            except Exception:
                configs = {}

        print(configs)
        return configs

    def _write(self, guildConfigs):
        with open('guildConfigs.json', 'w') as file:
            dataToSave = {'guildConfigs': guildConfigs}
            json.dump(dataToSave, file)

    def setConfig(self, guildId: int, key: str, val: bool):
        self._configs.setdefault(str(guildId), {})[key] = val
        self._write(self._configs) # update DB
    
    def getConfig(self, guildId: int, key: str) -> bool:
        try:
            return self._configs[str(guildId)][key]
        except KeyError:
            return False