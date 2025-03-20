# wumpus.py
# Invokes game and puzzle versions of Wumpus World.
# Written by: Simon Parsons
# Last Modified: 06/01/24

import getopt
import random
import config
import game
import puzzle
import sys

def displayHelp():
    print("wumpus.py accepts the following arguments:")
    print("-h : generates this message")
    print("-g <number> : runs the game version. <number> specifies algorithm:")
    print("\t1 - Depth First Search\n\t2 - Breadth First Search\n\t3 - Uniform Cost Search\n\t4 - Greedy Search")
    print("-p <number> : runs the puzzle version. <number> specifies algorithm:")
    print("\t1 - Depth First Search\n\t2 - A* Search")
    print("-d : run headless (no graphics)")
    print("-n <number> : runs -p or -g version <number> times (integer)")

def main():
    random.seed(config.myId)
    wType = "none"
    count = 1
    argList = sys.argv[1:]
    options = "hg:p:dn:"
    long_options = ["Help", "Game", "Puzzle", "Headless", "Number"]
    algorithm_type = 1

    try:
        arguments, values = getopt.getopt(argList, options, long_options)
        for currentArgument, currentValue in arguments:
            if currentArgument in ("-h", "--Help"):
                displayHelp()
                wType = "none"
            elif currentArgument in ("-g", "--Game"):
                wType = "game"
                if currentValue:
                    try:
                        algorithm_type = int(currentValue)
                        print(f"Game Algorithm Chosen: {algorithm_type}")
                    except ValueError:
                        print("Invalid -g value. Defaulting to 1.")
            elif currentArgument in ("-p", "--Puzzle"):
                wType = "puzzle"
                if currentValue:
                    try:
                        algorithm_type = int(currentValue)
                        print(f"Puzzle Algorithm Chosen: {algorithm_type}")
                    except ValueError:
                        print("Invalid -p value. Defaulting to 1.")
            elif currentArgument in ("-d", "--Headless"):
                config.headless = True
            elif currentArgument in ("-n", "--Number"):
                count = int(currentValue)

    except getopt.GetoptError as err:
        print(str(err))

    if wType != "none":
        if wType == "game":
            for i in range(count):
                print(f"Running game with algorithm {algorithm_type}")
                game.main(algorithm_type)
        elif wType == "puzzle":
            for i in range(count):
                print(f"Running puzzle with algorithm {algorithm_type}")
                puzzle.main(algorithm_type)

if __name__ == "__main__":
    main()