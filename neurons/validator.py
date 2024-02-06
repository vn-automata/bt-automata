# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
# TODO(developer): Set your name
# Copyright © 2023 <your name>

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

# Bittensor
import bittensor as bt

# Bittensor Validator Template:
import template
from template.validator import forward

# import base validator class which takes care of most of the boilerplate
from template.base.validator import BaseValidatorNeuron

#Internal modules
from template.utils import rulesets
from template.utils.rulesets import rule_classes


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
        # Generate a random initial state as a 1D numpy array from cpl

        # size defines the dimensionn of the 1-D array. Between 100-1000
        size = random.randint(100, 1000)

        # Generate the initial state using the ruelsets module
        initial_state = rulesets.InitialConditions(size)

        # Choose a random number of time-steps, between 100 and 1000
        steps = random.randint(1000, 5000)

        # Choose a random rule function. Limit to Class 3/4 rules in 1D. Covert it to a rule function using the rule_classes dictionary.
        rule_name = random.choice(["Rule30", "Rule54", "Rule62", "Rule110", "Rule124", "Rule126"])
        rule_func = rule_classes.get(rule_name)

        if rule_func is not None:
        # Rule name found, proceed!
        else:
            # Rule name not found. Sound the alarm
            raise ValueError(f"Rule '{rule_name}' not found in rule_classes dictionary.")

        # Log and return the parameters.
        if initial_state is not None and steps is not None and rule_func is not None:
            bt.logging.info(
                f"Generated cellular automata parameters: {initial_state}, {steps}, {rule_name}"
            )
        return initial_state, steps, rule_func


    async def forward(self):
        """
        Validator forward pass. Consists of:
        - Generating the query
        initial_state, steps, rule_func = self.get_random_params()
        - Running the simulation
        rulesets.Simulate1D(initial_state, steps, rule_func, r=1).run()
        - Querying the miners
        - Getting the responses
        - Rewarding the miners
        - Updating the scores
        """

        sample_size = min(self.config.neuron.sample_size, self.metagraph.n.item())
        miner_uids = template.utils.uids.get_random_uids(
            self,
            k=sample_size,
        )

        initial_state, timesteps, rule_func = self.get_random_params()
        synapse = template.protocol.CAsynapse(
            initial_state=initial_state,
            timesteps=timesteps,
            rule_func=rule_func,
        )

        # The dendrite client queries the network.
        responses = self.dendrite.query(
            # Send the query to selected miner axons in the network.
            axons=[self.metagraph.axons[uid] for uid in miner_uids],
            # Pass the synapse to the miner.
            synapse=synapse,
            # Do not deserialize the response so that we have access to the raw response.
            deserialize=False,
        )

        # Log the results for monitoring purposes.
        bt.logging.info(f"Received responses: {responses}")

        rewards = template.validator.reward.get_rewards(
            self,
            query_synapse=synapse,
            responses=responses,
        )

        bt.logging.info(f"Scored responses: {rewards}")

        # Update the scores based on the rewards. You may want to define your own update_scores function for custom behavior.
        self.update_scores(rewards, miner_uids)


# The main function parses the configuration and runs the validator.
if __name__ == "__main__":
    with Validator() as validator:
        while True:
            bt.logging.info("Validator running...", time.time())
            time.sleep(5)
