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

from bt_automata.protocol import CAsynapse
from bt_automata.utils import rulesets
from bt_automata.utils.misc import decompress_and_deserialize


def get_reward(
    ground_truth_array: NDArray[Any],
    response: CAsynapse,
) -> float:
    """
    Reward the miner response to the dummy request. This method returns a reward
    value for the miner, which is used to update the miner's score.

    Returns:
    - float: The reward value for the miner.
    """

    pred_array = decompress_and_deserialize(response.array_data)
    are_eq = np.array_equal(ground_truth_array, pred_array)
    return 1.0 if are_eq else 0.0


def get_rewards(
    self,
    query_synapse: CAsynapse,
    responses: List[CAsynapse],
) -> torch.FloatTensor:
    """
    Returns a tensor of rewards for the given query and responses.

    Args:
    - query (int): The query sent to the miner.
    - responses (List[float]): A list of responses from the miner.

    Returns:
    - torch.FloatTensor: A tensor of rewards for the given query and responses.
    """

    initial_state = decompress_and_deserialize(query_synapse.initial_state)
    timesteps = query_synapse.timesteps
    rule_name = query_synapse.rule_name
    rule_func_class = rulesets.rule_classes[rule_name]
    rule_func_obj = rule_func_class()
    gt_array = rulesets.Simulate1D(initial_state, timesteps, rule_func_obj, r=1).run()
    # Get all the reward results by iteratively calling your reward() function.
    return torch.FloatTensor(
        [get_reward(gt_array, response) for response in responses]
    ).to(self.device)