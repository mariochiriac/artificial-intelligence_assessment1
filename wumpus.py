# wumpus.py
# Invokes game and puzzle versions of Wumpus World.
# Written by: Simon Parsons
# Last Modified: 06/01/24

import sys
import game
import puzzle
import random
import config

# Display help message to console
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

    # Displays help message to console if -h detected
    if "-h" in sys.argv:
        displayHelp()
        return

    # Set defaults
    algorithm_type = 1  # Default to DFS
    headless = "-d" in sys.argv # Checks for input: -d
    iterations = 1
    mode = None
    
    # Algorithm dictionary
    algorithm_names = {
        1: "Depth-First Search",
        2: "Breadth-First Search", 
        3: "Uniform Cost Search",
        4: "Greedy Search",
        5: "A* Search"
    }

    # Parses and checks user console input
    for i, arg in enumerate(sys.argv):
        # If -g is found, run in game mode with the specified algorithm
        if arg == "-g" and i + 1 < len(sys.argv):
            try:
                algorithm_type = int(sys.argv[i + 1])
                mode = "game"
            except ValueError:
                print("Invalid algorithm type for game. Using DFS (1).")
        #If -p is found, run in puzzle mode with the specified algorithm
        elif arg == "-p" and i + 1 < len(sys.argv):
            try:
                algorithm_type = int(sys.argv[i + 1])
                mode = "puzzle"
            except ValueError:
                print("Invalid algorithm type for puzzle. Using DFS (1).")
        # If -n is found, set the number of iterations
        elif arg == "-n" and i + 1 < len(sys.argv):
            try:
                iterations = int(sys.argv[i + 1])
            except ValueError:
                print("Invalid number of iterations. Using 1.")

    # Ensure algorithm type is valid (1 to 5)
    if algorithm_type not in range(1, 6):
        print(f"Algorithm type {algorithm_type} not supported. Using DFS (1).")
        algorithm_type = 1

    # Display selected algorithm
    print(f"Running with {algorithm_names.get(algorithm_type, 'Unknown')} algorithm")
    
     # Execute the game or puzzle mode based on user input
    if mode == "game":
        status, total_steps = game.main(algorithm_type, headless, iterations)
        print(f"Game completed with {total_steps} total steps across {iterations} run(s)")
    elif mode == "puzzle":
        status, total_steps = puzzle.main(algorithm_type, headless, iterations)
        print(f"Puzzle completed with {total_steps} steps")
    else:
        print("Please specify -g or -p to select game or puzzle mode.")
        displayHelp()

if __name__ == "__main__":
    main()