# game.py
#
# Code that runs the Wumpus World as a game.
#
# run this on its own using:
# python game.py
#
# but better is to invoke this through wumpus.py
#
# Written by: Simon Parsons
# Last Modified: 17/12/24

from world import World
from link  import Link
from dungeon import Dungeon
import random
import config
import utils
import time

# We explicitly define the main function to allow this to both be run
# from the command line on its own, or invoked (from wumpus.py)
def main(algorithmType, headless=False, iterations=1):
    for _ in range(iterations):
        steps = 0

        # Set up the game world and player
        gameWorld = World()
        player = Link(gameWorld, algorithmType)
        
        # Initialize display only if not headless
        if not headless:
            display = Dungeon(gameWorld)
            display.update()
            time.sleep(1)
        
        # Run the game
        while not gameWorld.isEnded():
            gameWorld.updateLink(player.makeMove())
            gameWorld.updateWumpus()
            if not headless:
                display.update()
                time.sleep(1)
        
        # Display result
        if gameWorld.status == utils.State.WON:
            print("You won!")
        else:
            print("You lost!")
        
        # Close display if it was created
        if not headless:
            display.close()

# Since we explicitly named the main function
if __name__ == "__main__":
    main()
