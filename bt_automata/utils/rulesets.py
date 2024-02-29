# The MIT License (MIT)

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from abc import ABC, abstractmethod
import cellpylib as cpl
import numpy as np
from numpy.typing import NDArray
from typing import Any, Callable


class ApplyRule(ABC):
    """Abstract class for application of cellular automata rules"""

    @abstractmethod
    def rule_function(self, n, c, t):
        pass

# def get_initial_state(size, simple=False):
#     """
#     Get the initial state of the cellular automaton.
#     Can be either a simple or random initial state.
#     Random 1-D params:
#         init_random(size, k=2, n_randomized=None, empty_value=0, dtype=<class 'numpy.int32'>)
#     """
#     if simple:
#         return cpl.init_simple(size)
#     else:
#         return cpl.init_random(size, k=2, empty_value=0, dtype=np.int32)


class InitialConditions:
    def __init__(self, size: int, percentage: float, simple: bool):
        self.size = size
        self.percentage = percentage
        self.simple = False

    def init_1d(self):
        if self.simple:
            return cpl.init_simple(size)
        else:
            return cpl.init_random(size, k=2, empty_value=0, dtype=np.int32)

    def init_2d(self):
        if self.simple:
            cpl.init_simple2d(self.size, self.size)
        else:
            # Calculate the number of cells to be activated
            num_cells = int(self.size * self.size * self.percentage)
            # Create a flat array with the desired number of 1s and 0s
            cells = np.array([1]*num_cells + [0]*(self.size^2 - num_cells))
            # Randomly shuffle the array
            np.random.shuffle(cells)
            # Reshape the array to the size of the grid
            initial_state = cells.reshape(1, rows, cols)
            return initial_state


#--------------1-D--------------#
class Rule30(ApplyRule):
    """Class 3. Implementation of a one-dimensional cellular automaton rule,
    introduced by Stephen Wolfram, dubbed rule number 30 based on binary.
    Known for its chaotic behavior."""

    def rule_function(self, n: NDArray, c: int, t: int) -> int:
        return cpl.nks_rule(n, 30)


class Rule54(ApplyRule):
    """Class 3. Implementation of a 1D CA rule with rule number 54.
    This rule is known for its complex and chaotic behavior,
    making it an interesting choice for simulating complex systems
    and generating intricate patterns.
    """

    def rule_function(self, n: NDArray, c: int, t: int) -> int:
        return cpl.nks_rule(n, 54)


class Rule62(ApplyRule):
    """Class 4. Implementation of a 1D CA rule with rule number 62.
    Rule 62 exhibits unique behavior, can be used to study the emergence
    of complex patterns and structures in cellular automata simulations.
    """

    def rule_function(self, n: NDArray, c: int, t: int) -> int:
        return cpl.nks_rule(n, 62)


class Rule110(ApplyRule):
    """Class 3/4. Implementation of a 1D CA rule with rule number 110.
    Rule 110 noteably has the ability to simulate a universal Turing machine,
    making it a fundamental rule in the study of computational universality.
    """

    def rule_function(self, n: NDArray, c: int, t: int) -> int:
        return cpl.nks_rule(n, 110)


class Rule124(ApplyRule):
    """Class 4. Implementation of a 1D CA rule with rule number 124.
    Rule 124 is known for its interesting and intricate behavior,
    often used to explore the emergence of complex patterns.
    Often used for CA art-generation.
    """

    def rule_function(self, n: NDArray, c: int, t: int) -> int:
        return cpl.nks_rule(n, 124)


class Rule126(ApplyRule):
    """Class 4. Implementation of a 1D CA rule with rule number 126.
    Rule 126 is recognized for its unique emergent generation propoerties."""

    def rule_function(self, n: NDArray, c: int, t: int) -> int:
        return cpl.nks_rule(n, 126)


# ----------------- 2-D ------------------- #
class GameOfLifeRule(ApplyRule):
    """Implementation of Conway's Game of Life."""

    def rule_function(self, n: NDArray, c: int, t: int) -> int:
        # Count the number of live neighbors
        live_neighbors = np.sum(n) - c

        # Apply Conway's rules
        if c == 1 and 2 <= live_neighbors <= 3:
            return 1
        elif c == 0 and live_neighbors == 3:
            return 1
        else:
            return 0

class HighLifeRule(ApplyRule):
    """Implementation of Game of Life HighLife:
    a variant of Conway's Game of Life that also gives birth to a cell if there are 6 neighbors.
    """

    def rule_function(self, n, c, t):
        sum_n = np.sum(n)
        return int(c and 2 <= sum_n <= 3 or sum_n == 6)


class DayAndNightRule(ApplyRule):
    """Implementation of Day & Night: a variant of Conway's Game of Life
    that also gives birth to a cell if there are 3, 6, 7, or 8 neighbors."""

    def rule_function(self, n, c, t):
        sum_n = np.sum(n)
        return sum_n in (3, 6, 7, 8) or c and sum_n in (4, 6, 7, 8)
    

class FredkinRule(ApplyRule):
    """Implementation of Fredkin's is a cellular automaton rule where a cell is "born" if it has exactly one neighbor,
    and a cell "survives" if it has exactly two neighbors. Otherwise, the cell dies or remains dead.
    """

    def rule_function(self, n, c, t):
        sum_n = np.sum(n)
        return sum_n == 1 or c and sum_n == 2


class BriansBrainRule(ApplyRule):
    """Implementation of Brian's Brain: a three-state simulation.
    A cell is "born" if it was dead and has exactly two neighbors.
    A live cell dies in the next generation, and a dead cell remains dead."""

    def rule_function(self, n, c, t):
        sum_n = np.sum(n)
        if c == 0 and sum_n == 2:
            return 1
        elif c == 1:
            return 2
        elif c == 2:
            return 0
        else:
            return 0  # or any other default value


class SeedsRule(ApplyRule):
    """Implementation of Seeds is a cellular automaton where a cell is "born" if it has exactly two neighbors,
    and a cell "dies" otherwise."""

    def rule_function(self, n, c, t):
        sum_n = np.sum(n)
        return int(sum_n == 2)
    

class LambdaRule(ApplyRule):
    """Implementation of the Lambda rule for cellular automata. A cell is "born" if the number of its neighbors is greater than or equal to a parameter λ, and a cell "survives" if the number of its neighbors is less than or equal to λ."""

    def __init__(self, lambda_value: int):
        self.lambda_value = 0.37 #hard coded for now

    def rule_function(self, n: NDArray, c: int, t: int) -> int:
        sum_n = np.sum(n)
        if c == 0 and sum_n >= self.lambda_value:
            return 1
        elif c == 1 and sum_n <= self.lambda_value:
            return 1
        else:
            return 0

# ----------------- Cellular Automata Rules -----------------#
# Create mappings of rule names to classes
rule_classes_1D = {
    "Rule30": Rule30,
    "Rule54": Rule54,
    "Rule62": Rule62,
    "Rule110": Rule110,
    "Rule124": Rule124,
    "Rule126": Rule126
}
rule_classes_2D = {
    "GameOfLifeRule":GameOfLifeRule,
    "HighLifeRule":HighLifeRule,
    "DayAndNightRule":DayAndNightRule,
    "FredkinRule":FredkinRule,
    "BriansBrainRule":BriansBrainRule,
    "SeedsRule":SeedsRule,
    "LambdaRule":LambdaRule

}

class Simulate1D:
    """Simulation for evolution of one-dimensional cellular automata.
    Args:
    - ca (NDArray[np.float32]): The initial state of the cellular automaton.
    - timesteps (int): The number of timesteps to simulate.
    - rule_instance (Callable): An instance of the rule to apply.
    - r (int, optional): The neighborhood radius. Defaults to 1.
    """

    def __init__(
        self,
        ca: NDArray[np.float32],
        timesteps: int,
        rule_instance: ApplyRule,
        r: int = 1,
    ):
        self.ca = ca
        self.timesteps = timesteps
        self.rule_instance = rule_instance
        self.r = r

    def run(self) -> NDArray[Any]:
        """
        Runs the simulation and plots the result.
        Returns:
                NDArray[Any]: The final state of the cellular automaton after simulation.
        """
        try:
            ca = cpl.evolve(
                cellular_automaton=self.ca,
                timesteps=self.timesteps,
                apply_rule=self.rule_instance.rule_function,
                r=self.r,
            )

        except Exception as e:
            raise RuntimeError("Error running simulation.") from e

#        cpl.plot(ca)
        return ca


    
class Simulate2D:
    """Main simulation runner for 2D CA used in miner and validator routines"""

    def __init__(
        self,
        ca: NDArray[np.float32],
        timesteps: int,
        rule_instance: ApplyRule,
        r: int = 1,
        neighbourhood_type: str = "Moore",
    ):

        if neighbourhood_type not in ["Moore", "von Neumann"]:
            neighbourhood_type = "Moore"  # default to "Moore" if input is not valid

        self.ca = ca
        self.timesteps = timesteps
        self.rule_instance = rule_instance
        self.r = r
        self.neighborhood_type = neighbourhood_type

    def run(self) -> NDArray[Any]:
        try:
            ca = cpl.evolve2d(
                cellular_automaton=self.ca,
                timesteps=self.timesteps,
                apply_rule=self.rule_instance.rule_function,
                r=self.r,
                neighbourhood=self.neighborhood_type,
            )
        except Exception as e:
            raise RuntimeError(f"Error running simulation.") from e

        #cpl.plot2d_animate(ca)
        return ca