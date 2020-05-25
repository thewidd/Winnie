import json
import os.path

class GuildConfigs:
    supportedConfigKeys = {'createRoleForPlayersOfGame'}

    def __init__(self):
        self._configs = {}

    def initialize(self):
        self._configs = self._read()

    def _read(self) -> dict:
        configs = {}
        if os.path.exists('guildConfigs.json'):
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

    def setConfig(self, guildId: int, key: str, val: bool) -> bool:
        '''Returns the val that was set on key'''
        val = bool(val)
        try:
            existing_val = self._configs[str(guildId)][key]
        except KeyError:
            existing_val = None
            
        if existing_val != val:
            self._configs.setdefault(str(guildId), {})[key] = val
            self._write(self._configs) # update DB
        return val
    
    def getConfig(self, guildId: int, key: str) -> bool:
        try:
            return self._configs[str(guildId)][key]
        except KeyError:
            return False

    def get_all_configs(self, guildId: int) -> dict:
        try:
            return self._configs[str(guildId)]
        except KeyError:
            return {}