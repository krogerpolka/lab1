#MULTIPLE METHOD
class GameLibrary:
    # This class represents a game library
    # It stores and manages a list of games
    def __init__(self, name):
        self.name = name
        self.games = []

    def add_game(self, game):
        # This method adds a new game to the list
        self.games.append(game)
        print(f"Added game: {game}")

    def remove_game(self, game):
        # This method removes a game from the list if it exists
        if game in self.games:
            self.games.remove(game)
            print(f"Removed game: {game}")

    def show_games(self):
        # This method displays all games in the library
        print(f"Game Library '{self.name}':")
        for game in self.games:
            # This loop goes through each game in the list
            print(f"- {game}")


# Creating an object of the GameLibrary class
my_games = GameLibrary("My Games")
my_games.add_game("Minecraft")
my_games.add_game("GTA V")
my_games.add_game("The Witcher 3")

# Showing all games in the library
my_games.show_games()

