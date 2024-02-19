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


import random
import time

# Bittensor
import bittensor as bt

# Bittensor Validator Template:
import bt_automata

# import base validator class which takes care of most of the boilerplate
from bt_automata.base.validator import BaseValidatorNeuron

# Internal modules
from bt_automata.utils import rulesets
from bt_automata.utils.rulesets import rule_classes
from bt_automata.utils.misc import serialize_and_compress


class Validator(BaseValidatorNeuron):
    """
    Validator class for cellular automata protocol. This class will generate a random cellular automata rule and initial state,
    and then query the miners for their responses. It will then reward the miners based on the quality of their responses.
    1-diimensional cellular automata are supported through the cpl library. The rule is chosen from a set of class 3/4 rules,
    and the initial state is a random 1D numpy array, such that the store of all agent states will be a 2-D numpy array indexed on time (steps).

    Default: This class inherits from the BaseValidatorNeuron class, which in turn inherits from BaseNeuron. The BaseNeuron class takes care of routine tasks such as setting up wallet, subtensor, metagraph, logging directory, parsing config, etc. You can override any of the methods in BaseNeuron if you need to customize the behavior.

    Default: This class provides reasonable default behavior for a validator such as keeping a moving average of the scores of the miners and using them to set weights at the end of each epoch. Additionally, the scores are reset for new hotkeys at the end of each epoch.
    """

    def __init__(self, config=None):
        super(Validator, self).__init__(config=config)

        bt.logging.info("load_state()")
        self.load_state()

    def get_random_params(self):
        """Generate random parameters for the cellular automata.

        Returns:
        - initial_state (str): The initial state of the cellular automata.
        - timesteps (int): The number of time-steps to run the cellular automata for.
        - rule_name (str): The name of the rule function to use for the cellular automata.
        """

        # size defines the dimensionn of the 1-D array. Between 100-1000
        size = random.randint(250, 500)

        # Generate the initial state using the ruelsets module
        initial_state_raw = rulesets.get_initial_state(size)

        # Choose a random number of time-steps, between 100 and 1000
        steps = random.randint(250, 500)

        # Choose a random rule function. Limit to Class 3/4 rules in 1D. Covert it to a rule function using the rule_classes dictionary.
        rule_name = random.choice(
            ["Rule30", "Rule54", "Rule62", "Rule110", "Rule124", "Rule126"]
        )

        if rule_name not in rule_classes:
            # Rule name not found. Sound the alarm
            raise bt.logging.debug(
                f"Rule '{rule_name}' not found in rule_classes dictionary."
            )

        # Log and return the parameters.
        if (
            initial_state_raw is not None
            and steps is not None
            and rule_name is not None
        ):
            bt.logging.info(
                f"Generated cellular automata parameters: {initial_state_raw}, {steps}, {rule_name}"
            )

        initial_state = serialize_and_compress(initial_state_raw)
        return initial_state, steps, rule_name

    async def forward(self):
        """
        Validator forward pass. Consists of:
        - Generating the query
        initial_state, steps, rule_name = self.get_random_params()
        - Running the simulation
        rulesets.Simulate1D(initial_state, steps, rule_name, r=1).run()
        - Querying the miners
        - Getting the responses
        - Rewarding the miners
        - Updating the scores
        """

        # Get the UID of the validator
        my_uid = self.metagraph.hotkeys.index(self.wallet.hotkey.ss58_address)
        bt.logging.info(f"Validator {my_uid} running forward pass.")

        # Get the UIDs of the miners
        miner_uids = bt_automata.utils.uids.get_random_uids(
            self,
            k=min(self.config.neuron.sample_size, self.metagraph.n.item()),
            exclude=[my_uid],
        )

        # Generate the parameters for the cellular automata
        initial_state, timesteps, rule_name = self.get_random_params()

        # Instantiate synapse object and populate it with the parameters
        synapse = bt_automata.protocol.CAsynapse(
            initial_state=initial_state,
            timesteps=timesteps,
            rule_name=rule_name,
        )

        bt.logging.info(f"Querying miners: {miner_uids}")

        # Query the miners
        responses = self.dendrite.query(
            axons=[self.metagraph.axons[uid] for uid in miner_uids],
            synapse=synapse,
            deserialize=False,
        )
        uid_response_pairs = zip(miner_uids, responses)
        valid_uid_response_pairs = [(uid, response) for uid, response in uid_response_pairs if response.array_data is not None]

        if len(valid_uid_response_pairs) < len(responses):
            bt.logging.warning(
                f"Skipped {len(responses) - len(valid_uid_response_pairs)} responses due to None array data"
            )

        bt.logging.info(f"Received {len(valid_uid_response_pairs)} responses.")

        try:
            # Score the responses
            reward_uids, rewards = bt_automata.validator.get_rewards(
                self,
                query_synapse=synapse,
                responses=valid_uid_response_pairs,
            )

            bt.logging.info(f"Scored responses: {rewards}")

            self.update_scores(rewards, reward_uids)
        except Exception as e:
            bt.logging.error(f"Error scoring responses: {e}")

        # Wait for next round
        time.sleep(10)


if __name__ == "__main__":
    with Validator() as validator:
        while True:
            bt.logging.info("Validator running...", time.time())
            time.sleep(5)
