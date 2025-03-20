# puzzle.py
#
# Runs the Wumpus World as a puzzle.
#
# Standalone usage: python puzzle.py
# Recommended usage: invoke via wumpus.py
#
# Written by: Simon Parsons
# Last Modified: 17/12/24

from puzzleWorld import PuzzleWorld
from dungeon import Dungeon
import random
import config
import utils
import time

def main(algorithm_type=None, headless=False, iterations=1):
    # Runs the puzzle with parameters from wumpus.py
    # - algorithm_type: Search algorithm (1-5), defaults to DFS (1) if None
    # - headless: Disables display if True, defaults to False
    # - iterations: Number of runs, currently supports 1

    # Initialize the puzzle and goal states
    puzzle = PuzzleWorld()
    endState = PuzzleWorld()
    
    # Set up display if not running headless
    display = None
    show = None
    if not headless:
        display = Dungeon(puzzle)    # Display for current state
        show = Dungeon(endState)     # Display for goal state

    # Optional: print initial and goal states (uncomment to enable)
    # utils.printGameState(puzzle)
    # utils.printGameState(endState)

    # Update display if not headless
    if not headless:
        display.update()    # Show initial state
        show.update()       # Show goal state
        time.sleep(1)       # Pause for visibility

    # Generate movement plan with specified algorithm, defaulting to DFS
    puzzle.buildPlan(algorithm_type if algorithm_type else 1, endState)
    steps_taken = 0 # steps counter

    # Execute moves until the puzzle is solved
    while not isSolved(puzzle, endState):
        puzzle.makeAMove(endState)    # Perform next move
        steps_taken += 1
        if not headless:
            display.update()    # Refresh display
            time.sleep(1)       # Delay for animation

    # Output result based on game status
    if puzzle.status == utils.State.WON:
        print("You succeeded!")
    else:
        print("You failed!")

    print(f"Moves taken: {steps_taken}")
    # Close display if it was used
    if not headless:
        display.close()    # Clean up for multiple runs
        
    return puzzle.status, steps_taken

# Check if the current state matches the goal state
def isSolved(puzzle, goal):
    # Use utils.sameAs to compare positions of Link and Wumpuses
    if utils.sameLink(puzzle, goal) and utils.sameWumpus(puzzle, goal):
        puzzle.status = utils.State.WON   # Mark as won if solved
        print("Puzzle Over!")
        return True
    return False

# Entry point for standalone execution
if __name__ == "__main__":
    # Run with DFS and config-defined headless setting
    main(algorithm_type=1, headless=config.headless)