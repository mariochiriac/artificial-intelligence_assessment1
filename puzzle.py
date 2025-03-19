# puzzle.py
#
# Code that runs the Wumpus World as a puzzle.
#
# Run this on its own using:
# python puzzle.py
#
# but better is to invoke this through wumpus.py
#
# Written by: Simon Parsons
# Last Modified: 17/12/24

from puzzleWorld import PuzzleWorld
from dungeon import Dungeon
import random
import config
import utils
import time

# We explicitly define the main function to allow this to both be run
# from the command line on its own, or invoked (from wumpus.py)
def main(algorithm_type=1):  # Default to DFS
    found_chars = [0, 0, 0]
    puzzle = PuzzleWorld()
    endState = PuzzleWorld()
    if not config.headless:
        display = Dungeon(puzzle)
        show = Dungeon(endState)

    if not config.headless:
        display.update()
        show.update()
        time.sleep(1)

    # Initial plan for Link
    if algorithm_type == 2:
        print("Puzzle will be completed with A* Search algorithm.")
    else:
        print("Puzzle will be completed with Depth First Search algorithm.")

    puzzle.buildPlan(0, endState, algorithm_type)

    while not puzzle.isSolved(endState):
        if utils.sameLink(puzzle, endState) and found_chars[0] == 0:
            print("Link aligned")
            found_chars[0] = 1
            puzzle.buildPlan(1, endState, algorithm_type)  # Wumpus 1

        for i in range(len(puzzle.wLoc)):
            if utils.sameLocation(puzzle.wLoc[i], endState.wLoc[i]) and found_chars[i + 1] == 0:
                print(f"Wumpus {i} aligned")
                found_chars[i + 1] = 1
                if i + 1 < len(puzzle.wLoc):
                    puzzle.buildPlan(i + 2, endState, algorithm_type)  # Next Wumpus

        puzzle.makeAMove(endState)
        if not config.headless:
            display.update()
            time.sleep(1)

    if puzzle.status == utils.State.WON:
        print("You succeeded!")
    else:
        print("You failed!")

    if not config.headless:
        display.close()

if __name__ == "__main__":
    main()