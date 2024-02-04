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
    def __init__(self, size: int):
        self.size = size
        #self.percentage = percentage

    def init_simple_1d(self):
        # Use cpl library as a shortcut
        return cpl.init_simple(self.size)


#----------------- 1D Cellular Automata Rules -----------------#
# Create a mapping of rule names to classes
rule_classes = {
    "ConwayRule": ConwayRule,
    "HighLifeRule": HighLifeRule,
    "DayAndNightRule": DayAndNightRule,
    "Rule30": Rule30,
    "Rule54": Rule54,
    "Rule62": Rule62,
    "Rule110": Rule110,
    "Rule124": Rule124,
    "Rule126": Rule126,
    "FredkinRule": FredkinRule,
    "BriansBrainRule": BriansBrainRule,
    "SeedsRule": SeedsRule
}

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
