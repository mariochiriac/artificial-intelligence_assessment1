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
    total_steps = 0
    wins = 0
    
    for iteration in range(iterations):
        steps = 0  # Reset step counter for each iteration

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
            steps += 1  # Increment step counter
            
            if not headless:
                display.update()
                time.sleep(1)
        
        # Display result
        if gameWorld.status == utils.State.WON:
            print(f"You won in {steps} steps!")
            wins += 1
        else:
            print(f"You lost after {steps} steps.")
        
        total_steps += steps
        
        # NEW: Display total nodes expanded across all replans in this game
        print(f"Total nodes expanded during search: {player.total_nodes}")
        
        # Close display if it was created
        if not headless:
            display.close()
    
    # Print summary after all iterations
    if iterations > 1:
        print(f"Summary: {wins}/{iterations} games won")
        print(f"Total steps across all games: {total_steps}")
        print(f"Average steps per game: {total_steps/iterations:.2f}")
    
    return gameWorld.status, total_steps

# Since we explicitly named the main function
if __name__ == "__main__":
    main(1)  # Default to DFS