# puzzle.py
# Runs the Wumpus World as a puzzle.
# Written by: Simon Parsons
# Last Modified: 17/12/24

from puzzleWorld import PuzzleWorld
from dungeon import Dungeon
import random
import config
import utils
import time

def main(algorithm_type=1):
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

    print(f"Puzzle will be completed with {'A* Search' if algorithm_type == 2 else 'Depth First Search'} algorithm.")
    puzzle.buildPlan(0, endState, algorithm_type)

    while not puzzle.isSolved(endState):
        if utils.sameLink(puzzle, endState) and found_chars[0] == 0:
            print("Link aligned")
            found_chars[0] = 1
            puzzle.buildPlan(1, endState, algorithm_type)
        for i in range(len(puzzle.wLoc)):
            if utils.sameLocation(puzzle.wLoc[i], endState.wLoc[i]) and found_chars[i + 1] == 0:
                print(f"Wumpus {i} aligned")
                found_chars[i + 1] = 1
                if i + 1 < len(puzzle.wLoc):
                    puzzle.buildPlan(i + 2, endState, algorithm_type)
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