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
import torch.nn.functional as TF
from typing import Any, List

import numpy as np
from numpy.typing import NDArray

import bittensor as bt

from bt_automata.protocol import CAsynapse
from bt_automata.utils import rulesets
from bt_automata.utils.misc import decompress_and_deserialize


def get_accuracy(
    ground_truth_array: NDArray[Any],
    response: CAsynapse,
) -> float:
    """
    Returns the accuracy value (0,1) for the miner based on the comparison of the ground truth array and the response array.

    Args:
    - ground_truth_array (NDArray[Any]): The ground truth array for the cellular automata.
    - response (CAsynapse): The response from the miner.

    Returns:
    - float: The (binary) accuracy value for the miner.
    """

    try:
        pred_array = decompress_and_deserialize(response.array_data)

        if pred_array is None:
            bt.logging.debug("Failed to decompress and deserialize the response array.")
            return 0.0

        if not isinstance(pred_array, np.ndarray):
            bt.logging.debug("Response array is not a numpy array.")
            return 0.0

        accuracy = 1.0 if np.array_equal(ground_truth_array, pred_array) else 0.0

    except ValueError as e:
        bt.logging.debug(f"Error in get_accuracy: {e}")
        accuracy = 0.0

    ground_truth_str = np.array2string(ground_truth_array, threshold=10, edgeitems=2)
    pred_array_str = np.array2string(pred_array, threshold=10, edgeitems=2)

    # Log comparison
    bt.logging.info(
        f"Comparison | \nGround Truth: \n{ground_truth_str} | \nResponse: \n{pred_array_str} | \nAccuracy: {accuracy}"
    )

    return accuracy


def compute_rewards_sigmoid(
    process_times,
    accuracies,
    temp = 5.0,
    scale_mean = 1.0,
):
    if not isinstance(process_times, torch.Tensor):
        process_times = torch.tensor(process_times)
    if not isinstance(accuracies, torch.Tensor):
        accuracies = torch.tensor(accuracies)

    pt_0 = TF.normalize(process_times, dim=0)
    comp_max = (1. + pt_0.max()) / 2.
    bad_pred_ids = (accuracies != 1.).nonzero().squeeze()
    pt_0[bad_pred_ids] = comp_max

    pt_1 = torch.hstack((pt_0, torch.tensor([comp_max])))
    pt_2 = pt_1.mean() * scale_mean - pt_1
    pt_3 = pt_2 / pt_2.max()
    pt_4 = temp * pt_3
    pt_5 = TF.sigmoid(pt_4)
    pt_res = pt_5[:-1]

    bt.logging.debug(f"\nsigmoid\n{comp_max=}\n{temp=}\n{scale_mean=}\n{pt_res=}")
    return pt_res


def compute_rewards_log(
    process_times,
    accuracies,
    temp = 20.0,
    scale_mean = 0.5,
):
    if not isinstance(process_times, torch.Tensor):
        process_times = torch.tensor(process_times)
    if not isinstance(accuracies, torch.Tensor):
        accuracies = torch.tensor(accuracies)

    pt_0 = TF.normalize(process_times, dim=0)
    comp_max = (1. + pt_0.max()) / 2.
    bad_pred_ids = (accuracies != 1.).nonzero().squeeze()
    pt_0[bad_pred_ids] = comp_max

#    pt_1 = torch.hstack((pt_0, torch.tensor([comp_max])))
    pt_1 = pt_0
    pt_2 = pt_1.mean() * scale_mean - pt_1
    pt_3 = pt_2 / pt_2.max()
    pt_4 = temp * pt_3
    pt_5 = 1. - pt_4.min() + pt_4
    pt_6 = torch.log(pt_5)
#    pt_6 = pt_5
    pt_7 = pt_6
    pt_8 = pt_7 - pt_7.min()
    pt_9 = pt_8 / pt_8.max()
    pt_res = pt_9

    bt.logging.debug(f"\nlog\n{comp_max=}\n{temp=}\n{scale_mean=}\n{pt_res=}")
    return pt_res


def get_rewards(
    self,
    query_synapse: CAsynapse,
    responses: List[CAsynapse],
    rewards_scale="log",
) -> torch.FloatTensor:
    if len(responses) == 0:
        bt.logging.info("Got no responses. Returning reward tensor of zeros.")
        return [], torch.zeros_like(0).to(self.device)  # Fallback strategy: Log and return 0.

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

        # Calculate accuracies for each response
        accuracies = [get_accuracy(gt_array, response) for uid, response in responses]

        # Pull the process times from the synapse responses
        process_times = [response.dendrite.process_time for _, response in responses]
        resp_uids = [uid.item() for uid, _ in responses]
        bt.logging.debug(f"\n{resp_uids=}\n{process_times=}\n{accuracies=}")
        if rewards_scale == "log":
            compute_rewards_func = compute_rewards_log
        else:
            compute_rewards_func = compute_rewards_sigmoid
        bt.logging.debug(f"\n{rewards_scale=}\n{compute_rewards_func=}")
        rewards_for_responses = compute_rewards_func(
            process_times,
            accuracies,
        )
        bt.logging.debug(f"\n{rewards_for_responses=}")

    except Exception as e:
        bt.logging.debug(f"Error in get_rewards: {e}")
        resp_uids = []
        rewards_for_responses = torch.zeros_like(0).to(self.device)  # Fallback strategy: Log and return 0.

    return resp_uids, rewards_for_responses

