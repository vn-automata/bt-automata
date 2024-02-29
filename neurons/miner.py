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

import time
import typing
import bittensor as bt

import bt_automata

from bt_automata.utils import rulesets
from bt_automata.utils.misc import (
    serialize_and_compress,
    decompress_and_deserialize,
)
from bt_automata.base.miner import BaseMinerNeuron


class Miner(BaseMinerNeuron):
    """
    Your miner neuron class. You should use this class to define your miner's behavior. In particular, you should replace the forward function with your own logic. You may also want to override the blacklist and priority functions according to your needs.

    This class inherits from the BaseMinerNeuron class, which in turn inherits from BaseNeuron. The BaseNeuron class takes care of routine tasks such as setting up wallet, subtensor, metagraph, logging directory, parsing config, etc. You can override any of the methods in BaseNeuron if you need to customize the behavior.

    This class provides reasonable default behavior for a miner such as blacklisting unrecognized hotkeys, prioritizing requests based on stake, and forwarding requests to the forward function. If you need to define custom
    """

    def __init__(self, config=None):
        super(Miner, self).__init__(config=config)


    async def forward(
        self, synapse: bt_automata.protocol.CAsynapse
    ) -> bt_automata.protocol.CAsynapse:
        """
        Processes the incoming 'CAsynapse' synapse by running the specified simulation received from the validator and returning the result

        Args:
            synapse (bt_automata.protocol.CAsynapse): The synapse object containing the initial conditions, steps, and ruleset data.

        Returns:
            bt_automata.protocol.CAsynapse: The synapse object with the 'array_data' that houses the result of the simulation.

        """

        bt.logging.info(
            f"Received simulation request from: {synapse.dendrite.hotkey}. Initializing..."
        )

        try:
            # Validate the received synapse data
            if (
                not synapse.initial_state
                or synapse.timesteps <= 0
                or not synapse.rule_name
            ):
                bt.logging.debug(
                    "Invalid synapse data: Missing or incorrect initial state, timesteps, or rule name."
                )

            initial_state = decompress_and_deserialize(synapse.initial_state)

            if initial_state is None:
                raise bt.logging.debug("Failed to deserialize initial state.")

            bt.logging.info("Initial state deserialized: {}".format(initial_state))

            timesteps = synapse.timesteps
            rule_name = synapse.rule_name

            if rule_name not in rulesets.rule_classes_1D and rule_name not in rulesets.rule_classes_2D:
                bt.logging.debug(f"Unknown rule name: {rule_name}")
                return synapse  # Or handle differently
            
            # Run the simulation using the ruleset module.
            bt.logging.info(
                f"Running simulation for {timesteps} timesteps with: {rule_name}."
            )
            rule_func_class = None
            if rule_name in rulesets.rule_classes_1D:
                rule_func_class = rulesets.rule_classes_1D[rule_name]
                ca_sim = rulesets.Simulate1D(initial_state, timesteps, rule_func_class(), r=1)
            elif rule_name in rulesets.rule_classes_2D:
                rule_func_class = rulesets.rule_classes_2D[rule_name]
                ca_sim = rulesets.Simulate2D(initial_state, timesteps, rule_func_class(), r=1)

            ca_done = ca_sim.run()
            if ca_done is None:
                raise bt.logging.debug("Simulation failed to produce a result.")
            else:
                bt.logging.info(f"Simulation complete. Result: {ca_done}")

            array_data = serialize_and_compress(ca_done)
            if array_data is None:
                raise bt.logging.debug("Failed to serialize simulation result.")

            bt.logging.info(f"Array data serialized, transmitting...")
            synapse.array_data = array_data

        except Exception as e:
            bt.logging.error(f"Error occurred during forward pass: {e}")

        bt.logging.info(f"Succesfully transmitted array data.")
        return synapse


    async def blacklist(
        self, synapse: bt_automata.protocol.CAsynapse
    ) -> typing.Tuple[bool, str]:
        """
        Determines whether an incoming request should be blacklisted and thus ignored. Your implementation should
        define the logic for blacklisting requests based on your needs and desired security parameters.

        Blacklist runs before the synapse data has been deserialized (i.e. before synapse.data is available).
        The synapse is instead contructed via the headers of the request. It is important to blacklist
        requests before they are deserialized to avoid wasting resources on requests that will be ignored.

        Args:
            synapse (bt_automata.protocol.CAsynapse): A synapse object constructed from the headers of the incoming request.

        Returns:
            Tuple[bool, str]: A tuple containing a boolean indicating whether the synapse's hotkey is blacklisted,
                            and a string providing the reason for the decision.

        This function is a security measure to prevent resource wastage on undesired requests. It should be enhanced
        to include checks against the metagraph for entity registration, validator status, and sufficient stake
        before deserialization of synapse data to minimize processing overhead.

        Example blacklist logic:
        - Reject if the hotkey is not a registered entity within the metagraph.
        - Consider blacklisting entities that are not validators or have insufficient stake.

        In practice it would be wise to blacklist requests from entities that are not validators, or do not have
        enough stake. This can be checked via metagraph.S and metagraph.validator_permit. You can always attain
        the uid of the sender via a metagraph.hotkeys.index( synapse.dendrite.hotkey ) call.

        Otherwise, allow the request to be processed further.
        """
        # TODO(developer): Define how miners should blacklist requests.
        if synapse.dendrite.hotkey not in self.metagraph.hotkeys:
            # Ignore requests from unrecognized entities.
            bt.logging.trace(
                f"Blacklisting unrecognized hotkey {synapse.dendrite.hotkey}"
            )
            return True, "Unrecognized hotkey"

        bt.logging.trace(
            f"Not Blacklisting recognized hotkey {synapse.dendrite.hotkey}"
        )
        return False, "Hotkey recognized!"

    async def priority(self, synapse: bt_automata.protocol.CAsynapse) -> float:
        """
        The priority function determines the order in which requests are handled. More valuable or higher-priority
        requests are processed before others. You should design your own priority mechanism with care.

        This implementation assigns priority to incoming requests based on the calling entity's stake in the metagraph.

        Args:
            synapse (bt_automata.protocol.CAsynapse): The synapse object that contains metadata about the incoming request.

        Returns:
            float: A priority score derived from the stake of the calling entity.

        Miners may recieve messages from multiple entities at once. This function determines which request should be
        processed first. Higher values indicate that the request should be processed first. Lower values indicate
        that the request should be processed later.

        Example priority logic:
        - A higher stake results in a higher priority value.
        """
        # TODO(developer): Define how miners should prioritize requests.
        caller_uid = self.metagraph.hotkeys.index(
            synapse.dendrite.hotkey
        )  # Get the caller index.
        prirority = float(
            self.metagraph.S[caller_uid]
        )  # Return the stake as the priority.
        bt.logging.trace(
            f"Prioritizing {synapse.dendrite.hotkey} with value: ", prirority
        )
        return prirority


# This is the main function, which runs the miner.
if __name__ == "__main__":
    with Miner() as miner:
        while True:
            bt.logging.info("Miner running...", time.time())
            time.sleep(5)
