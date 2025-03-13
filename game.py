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
def main():
    # How we set the game up. Create a world, then connect player and
    # display to it.
    gameWorld = World()
    player = Link(gameWorld)
    display = Dungeon(gameWorld)

    # Uncomment this for a printout of world state at the start
    utils.printGameState(gameWorld)

    # Show initial state
    display.update()
    time.sleep(1)
    # Now run...
    while not(gameWorld.isEnded()):
        gameWorld.updateLink(player.makeMove())
        gameWorld.updateWumpus()
        # Uncomment this for a printout of world state every step
        # utils.printGameState(gameWorld)
        display.update()
        time.sleep(1)

    # Display message at end
    if gameWorld.status == utils.State.WON:
        print("You won!")
    else:
        print("You lost!")

    # Close the display --- neded if we are going to have multiple runs.
    display.close()

# Since we explicitly named the main function
if __name__ == "__main__":
    main()
