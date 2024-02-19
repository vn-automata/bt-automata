import numpy as np
import torch
import torch.nn.functional as TF
import matplotlib.pyplot as plt

def compute_proc_time_scores(
    process_times,
    temp = 10.,
    comp_max = 1.5,
):
    if not isinstance(process_times, torch.Tensor):
        process_times = torch.tensor(process_times)
    pt_0 = TF.normalize(process_times, dim=0)
    pt_1 = torch.hstack((pt_0, torch.tensor([comp_max])))
    pt_2 = pt_1.mean() - pt_1
    pt_3 = pt_2 / pt_2.max()
    pt_4 = temp * pt_3
    pt_5 = TF.sigmoid(pt_4)
    pt_res = pt_5[:-1]
    return pt_res

# Generate a random set of 100 process times between .0001 and .0002 seconds
process_times = np.random.uniform(low=0.00001, high=0.00002, size=(100,))

# Test the function
scores = compute_proc_time_scores(process_times)

# Plot the scores
plt.plot(process_times, scores.numpy(), 'o')
plt.xlabel('Process Times')
plt.ylabel('Scores')
plt.title('Process Times vs Scores')
plt.show()