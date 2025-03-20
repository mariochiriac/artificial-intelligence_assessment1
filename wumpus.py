# wumpus.py
# Invokes game and puzzle versions of Wumpus World.
# Written by: Simon Parsons
# Last Modified: 06/01/24

import sys
import game
import puzzle
import random
import config

def displayHelp():
    print("wumpus.py accepts the following arguments:")
    print("-h : generates this message")
    print("-g <number> : runs the game version with algorithm type:")
    print("\t1 - Depth-First Search\n\t2 - Breadth-First Search\n\t3 - Uniform Cost Search")
    print("\t4 - Greedy Search\n\t5 - A* Search")
    print("-p <number> : runs the puzzle version with algorithm type:")
    print("\t1 - Depth-First Search\n\t2 - Breadth-First Search\n\t3 - Uniform Cost Search")
    print("\t4 - Greedy Search\n\t5 - A* Search")
    print("-d : run headless (no graphics)")
    print("-n <number> : runs the selected version <number> times")

def main():
    # Seed the random number generator.
    random.seed(config.myId)

    if "-h" in sys.argv:
        displayHelp()
        return

    algorithm_type = 1  # Default to DFS
    headless = "-d" in sys.argv
    iterations = 1
    mode = None

    for i, arg in enumerate(sys.argv):
        if arg == "-g" and i + 1 < len(sys.argv):
            try:
                algorithm_type = int(sys.argv[i + 1])
                mode = "game"
            except ValueError:
                print("Invalid algorithm type for game. Using DFS (1).")
        elif arg == "-p" and i + 1 < len(sys.argv):
            try:
                algorithm_type = int(sys.argv[i + 1])
                mode = "puzzle"
            except ValueError:
                print("Invalid algorithm type for puzzle. Using DFS (1).")
        elif arg == "-n" and i + 1 < len(sys.argv):
            try:
                iterations = int(sys.argv[i + 1])
            except ValueError:
                print("Invalid number of iterations. Using 1.")

    if algorithm_type not in range(1, 6):
        print(f"Algorithm type {algorithm_type} not supported. Using DFS (1).")
        algorithm_type = 1

    total_steps = 0 # holds number of steps
    if mode == "game":
       game.main(algorithm_type, headless, 1)      # returns status of game (lost / won), and number of steps taken by algorithm
    elif mode == "puzzle":
        status, steps = puzzle.main(algorithm_type, headless, 1)    # returns status of game (lost / won), and number of steps taken by algorithm
    else:
        print("Please specify -g or -p to select game or puzzle mode.")
        displayHelp()

if __name__ == "__main__":
    main()