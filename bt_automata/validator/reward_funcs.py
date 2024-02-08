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

import torch
from typing import Any, List

import numpy as np
from numpy.typing import NDArray

import bittensor as bt

from bt_automata.protocol import CAsynapse
from bt_automata.utils import rulesets
from bt_automata.utils.misc import decompress_and_deserialize


def get_reward(
    ground_truth_array: NDArray[Any],
    response: CAsynapse,
) -> float:
    """
    Returns the reward value for the miner based on the comparison of the ground truth array and the response array.

    Args:
    - ground_truth_array (NDArray[Any]): The ground truth array for the cellular automata.
    - response (CAsynapse): The response from the miner.

    Returns:
    - float: The reward value for the miner.
    """

    try:
        pred_array = decompress_and_deserialize(response.array_data)

        if pred_array is None:
            bt.logging.debug("Failed to decompress and deserialize the response array.")
            return 0.0

        if not isinstance(pred_array, np.ndarray):
            bt.logging.debug("Response array is not a numpy array.")
            return 0.0

        reward = 1.0 if np.array_equal(ground_truth_array, pred_array) else 0.0

    except ValueError as e:
        bt.logging.debug(f"Error in get_reward: {e}")
        reward = 0.0

    ground_truth_str = np.array2string(ground_truth_array, threshold=10, edgeitems=2)
    pred_array_str = np.array2string(pred_array, threshold=10, edgeitems=2)

    # Log comparison
    bt.logging.info(
        f"Comparison | \nGround Truth: \n{ground_truth_str} | \nResponse: \n{pred_array_str} | \nReward: {reward}"
    )

    return reward


def get_rewards(
    self,
    query_synapse: CAsynapse,
    responses: List[CAsynapse],
) -> torch.FloatTensor:
    try:
        initial_state = decompress_and_deserialize(query_synapse.initial_state)
        timesteps = query_synapse.timesteps
        rule_name = query_synapse.rule_name

        if rule_name not in rulesets.rule_classes:
            bt.logging.debug(f"Unknown rule name: {rule_name}")
            return torch.FloatTensor([]).to(self.device)  # Or handle differently

        bt.logging.debug(f"Calculating rewards for {len(responses)} responses.")

        rule_func_class = rulesets.rule_classes[rule_name]
        rule_func_obj = rule_func_class()

        gt_array = rulesets.Simulate1D(
            initial_state, timesteps, rule_func_obj, r=1
        ).run()
        if gt_array is None:
            bt.logging.debug("Simulation failed to produce a result.")
            return torch.FloatTensor([]).to(self.device)  # Or handle differently

        rewards = np.zeros(256)
        for uid, response in responses:
            if response.array_data is None:
                continue
            result_accuracy = get_reward(gt_array, response)
            process_time = response.dendrite.process_time
            rewards[uid] = result_accuracy * 0.7 + process_time * 0.3

    except Exception as e:
        bt.logging.debug(f"Error in get_rewards: {e}")
        rewards = np.zeros(256)  # Decide on a fallback strategy

    return torch.FloatTensor(rewards).to(self.device)
