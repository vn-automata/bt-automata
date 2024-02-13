
<p align="center">
      <img width="500" alt="bt automata - subnet + repo logo" src="https://i.imgur.com/RrPk0yg.png"
    </a>
    
</p>

<div align='center'>


[![Discord Chat](https://img.shields.io/discord/308323056592486420.svg)](https://discord.gg/bittensor)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# Cellular Automata - A Bittensor Subnet
<div align = 'left'>

## Bittensor Resources

[Discord](https://discord.gg/bittensor) • [Network](https://taostats.io/) • [Research](https://bittensor.com/whitepaper)

## Table of Contents

1. [Introduction](#introduction)
2. [Features](#features)
3. [Prerequisites](#prerequisites)
   - [Validator Hardware](#validator-hardware)
   - [Miner Hardware](#miner-hardware)
4. [Installation](#installation)
5. [Running a Validator](#running-a-validator)
6. [Running a Miner](#running-a-miner)
   - [Restarting your Miner](#restarting-your-miner)
7. [FAQ](#faq)
8. [Contributing](#contributing)
9. [License](#license)

---

## Introduction
IMPORTANT: If you are brandnew to the Bittensor ecosystem, checkout the [Bittensor Website](https://bittensor.com/) before proceeding here!

This repository contains the code for the Cellular Automata Subnet. The primary focus of this subnet is to run, analyze, and store cellular automata to serve as a reasearch and science accellerator. The network itself will serve as a conduit between cellular automata reserachers in the scientific community and the computational resources available through the Bittensor community of miners and validators.

The significance of cellular automata lies in their ability to demonstrate how simple rules can evolve into complex patterns and behaviors over time, which can resemble processes observed in nature. This has profound implications in understanding complex systems and emergent behavior because it suggests that complexity may be emergent rather than inherent, arising from the interaction of simple components governed by simple rules, rather than from complexity embedded within the components themselves. Cellular automata have been applied in such diverse fields as, cryptography, physics, and biology, fluid dynamics, and social systems, and art. 

As the size or dimensionality of the automaton increases, so does the computational cost, usually exponentially, making extensive exploration and experimentation computationally prohibitive for many teams. Additionally, analyzing the results of CA simulations can be challenging, particularly when dealing with emergent behaviors that are complex, unpredictable, and sometimes difficult to quantify or interpret within the context of real-world phenomena. Bittensor addresses some key challenges in the field, including resource allocation, incentive alignment, and scalability. Its decentralized design enables a peer-to-peer network where nodes are driven to contribute computational results and continually scored by machine learning models to further increase the accuracy, depth and speed of response. 

## Features

- 1-D Cellular Automata simulated with [CellPyLib](https://cellpylib.org/index.html)
- Miner scoring on simulation accuracy and processing time
### Upcoming Features
- 2-D Cellular automata simulated with [CellPyLib](https://cellpylib.org/index.html)
- Searchable database of simulation results
- [Wolfram Alpha](https://products.wolframalpha.com/api) integration

## Prerequisites

- Requires **Python 3.8 or higher.**
- [Bittensor](https://github.com/opentensor/bittensor#install)

### Validator Hardware

    - Recommend 16 vCPU + 16 GB memory
    - 100 GB balanced persistent disk

### Miner Hardware
**Miners are incentivized based on the accuracy of their simulation, and the processing time required to respond to the validator. Here is the minimum, but we recommend you run CA simulations on your server before registering on the mainnet.**

    - Reommend 16 vCPU + 16 GB memory
    - Run the miner using CPU

## Installation

To install this subnet, first clone and install the dependencies:

```bash
# clone repo
git clone https://github.com/vn-automata/bt-automata.git

# change directory
cd bt-automata

# create virtual environment
python3 -m venv venv

# activate the virtual environment
. venv/bin/activate

# disable pip cache
export PIP_NO_CACHE_DIR=1

# install dependencies
pip install -r requirements.txt

# create a local and editable installation
python3 -m pip install -e .
```

## Running a Validator

The validator will generate simulation parameters, run the siumulation locally, send the parameters to the miner group, and then score the miners based on simulation acciuracy and processing time.

```bash
# Replace MYWALLET, MYHOTKEY with your wallet details
python neurons/validator.py --netuid XX --wallet.name MYWALLET --wallet.hotkey MYHOTYKEY
```

## Running a Miner

We recommend that you run your miner using PM2. PM2 is a production process manager for Node.js applications. It allows you to keep applications alive forever and reload them without downtime.

```bash
sudo apt update && sudo apt upgrade -y
```

```bash
sudo apt install npm -y && sudo npm install pm2@latest -g && pm2 update
```

Register your miner keys to the network

```bash
# Replace MYWALLET, MYHOTKEY, and MYPORTNUMBER with your wallet details 
btcli subnet register --netuid XX --wallet.name MYWALLET --wallet.hotkey MYHOTKEY --axon.port MYPORTNUMBER
```

You can start miner with the following commands, replacing placeholders with your wallet information, subtensor netowrk (assumes you are running a local [subtensor](https://github.com/opentensor/subtensor) ) and port number:

```bash
# Replace MYWALLET, MYHOTKEY, and MYPORTNUMBER with your wallet details and port number
pm2 start neurons/miner.py --interpreter python3 -- --netuid XX --subtensor.network local --wallet.name MYWALLET --wallet.hotkey MYHOTKEY --axon.port MYPORTNUMBER
```
### Restarting your miner

After pulling and updates from the repository, don't forget to restart your miner:

```bash
pm2 restart all --update-env
```

## FAQ
Q: How can I participate in the network?
A: You can participate as a miner or a validator. Examples to get started are included in the "Running a Miner" and "Running a Validator" sections. 

Q: I am a CA researcher. How can I access the completed simulations?
A: Stay tuned. Once we have completed out proof-of-concept phase, we will open up a database of completed simulations from top miners for reserachers to access and study.

Q: Can I mine on this subnet with CPU?
A: Yes!

## Contributing

For instructions on how to contribute to this subnet, see CONTRIBUTING.md.

## License

This repository is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
