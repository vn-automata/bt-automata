# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
# Copyright © 2023 bt-automata

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
    # The initial state of the automata, encoded as string.
    initial_state: str

    # The number of timesteps to evolve the automata.
    timesteps: int

    # The rule function to apply to the automata.
    rule_func: str

    # The transformed array to be returned, encoded as string.
    array_data: typing.Optional[str] = None

    # def evolve_example(self, synapse: protocol.CAsynapse) -> str:
    #     return synapse.array_data

    required_hash_fields: typing.List[str] = pydantic.Field(
        ["initial_state", "timesteps", "rule_func", "array_data"],
        title="Required Hash Fields",
        description="A list of required fields for the hash.",
        allow_mutation=False,
    )

    # Returns a hash of the fields in the exchange, verifying transaction integrity.
    # hash_value = synapse.body_hash

    def __str__(self):
        return (
            f"CAsynapse(initial_state={self.initial_state[:12]}, "
            f"timesteps={self.timesteps}, "
            f"rule_func={self.rule_func}, "
            f"array_data={self.array_data[:12]}",
            f"axon={self.axon.dict()}",
            f"dendrite={self.dendrite.dict()}",
        )

    # Simply return as string, more complex serialization,
    # encoding and compression will be added into miner/validator
    # shared library.

    def deserialize(self) -> str:
        return self.array_data
