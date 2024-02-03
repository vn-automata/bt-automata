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


from typing import Any, Callable
import numpy as np
from numpy.typing import NDArray
import cellpylib as cpl
import bittensor as bt
from abc import ABC, abstractmethod


class ApplyRule(ABC):
    """Abstract class for application of cellular automata rules"""

    @abstractmethod
    def rule_function(self, n, c, t):
        pass


class InitialConditions:
    def __init__(self, size: int, percentage: float):
        self.size = size
        self.percentage = percentage

    def init_random_1d(self):
        # Calculate the number of cells to be activated
        num_cells = int(self.size * self.percentage)
        # Create a flat array with the desired number of 1s and 0s
        initial_state = np.array([1] * num_cells + [0] * (self.size - num_cells))
        # Reshape the array to the desired structure
        initial_state = initial_state.reshape(1, -1)
        return initial_state

    def init_simple_1d(self):
        # Use cpl library as a shortcut
        return cpl.init_simple(self.size)

    def init_random_2d(self, rows: int, cols: int):
        # Calculate the number of cells to be activated
        num_cells = int(rows * cols * self.percentage)
        # Create a flat array with the desired number of 1s and 0s
        cells = np.array([1]*num_cells + [0]*(rows*cols - num_cells))
        # Randomly shuffle the array
        np.random.shuffle(cells)
        # Reshape the array to the size of the grid
        initial_state = cells.reshape(1, rows, cols)
        return initial_state

    def init_simple_2d(self):
        # use cpl library as a shortcut
        return cpl.init_simple2d(rows, cols)


class ConwayRule(ApplyRule):
    """Implementation of Conway's Game of Life:
    a cellular automaton where a cell is "born" if it has exactly three neighbors,
    and a cell "survives" if it has exactly two or three neighbors. Otherwise,
    the cell dies or remains dead."""

    def rule_function(self, n, c, t):
        sum_n = np.sum(n)
        return int(c and 2 <= sum_n <= 3 or sum_n == 3)


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


class Rule30(ApplyRule):
    """Class 3. Implementation of a one-dimensional cellular automaton rule introduced by Stephen Wolfram, dubbed rule number 30 based on binary.
    known for its chaotic behavior."""

    def rule_function(self, n: NDArray, c: int, t: int) -> int:
        return cpl.nks_rule(n, 30)


class Rule54(ApplyRule):
    """Class 3. Implementation of a 1D CA rule with rule number 54.
    This rule is known for its complex and chaotic behavior, making it an interesting choice for simulating complex systems and generating intricate patterns."""

    def rule_function(self, n: NDArray, c: int, t: int) -> int:
        return cpl.nks_rule(n, 54)

class Rule62(ApplyRule):
    """Class 4. Implementation of a 1D CA rule with rule number 62.
    Rule 62 exhibits unique behavior, can be used to study the emergence of complex patterns and structures in cellular automata simulations."""

    def rule_function(self, n: NDArray, c: int, t: int) -> int:
        return cpl.nks_rule(n, 62)


class Rule110(ApplyRule):
    """Class 3/4. Implementation of a 1D CA rule with rule number 110.
    Rule 110 noteably has the ability to simulate a universal Turing machine, making it a fundamental rule in the study of computational universality."""

    def rule_function(self, n: NDArray, c: int, t: int) -> int:
        return cpl.nks_rule(n, 110)


class Rule124(ApplyRule):
    """Class 4. Implementation of a 1D CA rule with rule number 124.
    Rule 124 is known for its interesting and intricate behavior, often used to explore the emergence of complex patterns. Often used for CA art-generation"""

    def rule_function(self, n: NDArray, c: int, t: int) -> int:
        return cpl.nks_rule(n, 124)

class Rule126(ApplyRule):
    """Class 4. Implementation of a 1D CA rule with rule number 126.
    Rule 126 is recognized for its unique emergent generation propoerties."""

    def rule_function(self, n: NDArray, c: int, t: int) -> int:
        return cpl.nks_rule(n, 126)


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


class ByteTransfer(bt.Synapse):
    """A synapse that verifies the integrity of a simulation"""

    @staticmethod
    def deserialize(bytes: bytes) -> [NDArray[np.float64]]:
        """
        Deserialize the simulation output. This method retrieves the result of
        the CA simulation from the miner in the form of simulation_output,
        deserializes it and returns it as the output of the dendrite.query() call.
        This should be more efficient for numerical ops than a list

        Returns:
        - np.ndarray: The deserialized response, which in this case is the value of simulation_output.
        """
        # Check if the data is not None and deserialize it
        if not isinstance(bytes):
            raise ValueError("Data must be bytes")
        if bytes is not None:
            deserialized = np.frombuffer(bytes, dtype=np.int).reshape(-1, 100)
            data = deserialized.astype(np.float64)

            # Validate the deserialized data (if necessary)

            return data
        return None

    @staticmethod
    def serialize(data: NDArray[np.float64]) -> bytes:
        """
        Serialize the simulation output. This method serializes the result of
        the CA simulation and returns it as the output of the dendrite.query() call.

        Returns:
        - bytes: The serialized response, which in this case is the value of simulation_output.
        """
        # Check if the data is not None and serialize it
        if not isinstance(data, np.ndarray):
            raise ValueError("Data must be np.ndarray")
        if data is not None:
            serialized = data.tobytes()

            # Validate the serialized data (if necessary)

        return serialized
    
class Simulate:
    """Main simulation runner for CA used in miner and validator routines"""

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

        cpl.plot2d_animate(ca)
        return ca


class Simulate1D:
    """Main simulation runner for 1D CA used in miner and validator routines"""

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
        try:
            ca = cpl.evolve(
                cellular_automaton=self.ca,
                timesteps=self.timesteps,
                apply_rule=self.rule_instance.rule_function,
                r=self.r,
            )
        except Exception as e:
            raise RuntimeError(f"Error running simulation.") from e

        cpl.plot(ca)
        return ca


# Test rules with Simulate class
if __name__ == "__main__":  #
    initial_state = init_random_2d(60, 60, 0.1)
    # Rules
    rule_instance = ConwayRule()
    # rule_instance = HighLifeRule()
    # rule_instance = DayAndNightRule()
    # rule_instance = Rule30()
    # rule_instance = Rule110()
    # rule_instance = FredkinRule() 
    # rule_instance = BriansBrainRule()
    #rule_instance = SeedsRule() 
    #
    sim = Simulate(
        initial_state,
        timesteps=100,
        rule_instance=rule_instance,
        neighbourhood_type="Moore",
        r=1,
    )
    result = sim.run()
    print(result)


# Test rules with Simulate1D class
if __name__ == "__main__":
    initial_state = cpl.init_simple(100)
    rule_instance = Rule30()
    sim = Simulate1D(
        initial_state,
        timesteps=100,
        rule_instance=rule_instance,
        r=1,
    )
    result = sim.run()
    print(result)
