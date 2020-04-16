import discord

class Game:
    def __init__(self, name, applicationId=None):
        self.name = name
        self.applicationId = applicationId

    def __eq__(self, other: Game):
        return (self.name == other.name and (self.applicationId == None or other.applicationId == None)) or \
            (self.name == other.name and self.applicationId == other.applicationId)

class Games:
    def __init__(self):
        self.knownGames = set()

    def addGame(self, activity: discord.Activity):
        try:
            matchingGames = [game for game in self.knownGames if game.name == activity.name or activity.applicationId == activity.applicationId]
        except AttributeError:
            return

        if len(matchingGames) == 0:
            if isinstance(activity, discord.Activity):
                gameToAdd = Game(activity.name, activity.application_id)
            else isinstance(activity, discord.activity.Game):
                gameToAdd = Game(activity.name)

            if gameToAdd is not None:
                self.knownGames.add(gameToAdd)