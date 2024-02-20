import cellpylib as cpl
import pprint

cellular_automaton = cpl.init_simple(50)

cellular_automaton = cpl.evolve(cellular_automaton, timesteps=50, memoize=True,
                                apply_rule=lambda n, c, t: cpl.nks_rule(n, 110))

#cpl.plot(cellular_automaton)

# Define the characters for visualization
char_1 = "\033[92m#\033[0m"  # Green color for 1's
char_0 = "."  # No color for 0's

# Convert the binary array to a string representation
visualization = "\n".join("".join(char_1 if cell == 1 else char_0 for cell in row) for row in cellular_automaton)

# Print the visualization with smooth margins
#pprint.pprint(visualization, width=30)
print(f"echo -e '{visualization}'")