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

import typing
import pydantic
import bittensor as bt


class CAsynapse(bt.Synapse):
    """Synapse for type checking and serialization of the cellular automata transaction."""

    initial_state: str = pydantic.Field(
        "",
        title="Initial State",
        description="The initial state of the cellular automata, encoded as a string.",
    )

    timesteps: int = pydantic.Field(
        0,
        title="Timesteps",
        description="The number of timesteps to evolve the cellular automata.",
    )

    rule_func: str = pydantic.Field(
        "",
        title="Rule Function",
        description="The rule function to apply to the cellular automata.",
    )

    array_data: typing.Optional[str] = pydantic.Field(
        None,
        title="Array Data",
        description="The transformed array to be returned, encoded as a string.",
    )

    required_hash_fields: typing.List[str] = pydantic.Field(
        ["initial_state", "timesteps", "rule_func", "array_data"],
        title="Required Hash Fields",
        description="A list of required fields for the hash.",
        allow_mutation=False,
    )

    def __str__(self):
        return (
            f"CAsynapse(initial_state={self.initial_state[:12]}, "
            f"timesteps={self.timesteps}, "
            f"rule_func={self.rule_func}, "
            f"array_data={self.array_data[:12]}",
            f"axon={self.axon.dict()}",
            f"dendrite={self.dendrite.dict()}",
        )

    def deserialize(self) -> str:
        return self.array_data
