import argparse
import time
import subprocess
import bt_automata
from bt_automata.utils.helpers import get_version

default_chain_endpoint = "wss://bittensor-finney.api.onfinality.io/public-ws"


def start_validator(
    pm2_name, wallet_name, wallet_hotkey, address, network, netuid, axon_port, sample_size = 12
):
    print("Deleting previous PM2 process...")
    result = subprocess.run(["pm2", "delete", pm2_name])
    print(result.stdout)

    print("Pulling the latest code...")
    result = subprocess.run(["git", "pull"])
    print(result.stdout)

    print("Installing dependencies...")
    result = subprocess.run(["pip", "install", "-r", "requirements.txt"])
    print(result.stdout)

    print("Installing package...")
    result = subprocess.run(["pip", "install", "-e", "."])
    print(result.stdout)

    print("Running validator code using PM2...")
    result = subprocess.run(
        [
            "pm2",
            "start",
            "neurons/validator.py",
            "--interpreter",
            "python3",
            "--name",
            pm2_name,
            "--",
            "--wallet.name",
            wallet_name,
            "--wallet.hotkey",
            wallet_hotkey,
            "--netuid",
            netuid,
            "--subtensor.network",
            network,
            "--subtensor.chain_endpoint",
            address,
            "--axon.port",
            axon_port,
            "--logging.debug",
            "--logging.trace",
            "--neuron.sample_size",
            str(sample_size),
        ]
    )
    print(result.stdout)


def update_and_restart(
    pm2_name, wallet_name, wallet_hotkey, address, network, netuid, axon_port, sample_size = 12
):
    while True:
        current_version = bt_automata.__version__
        latest_version = get_version()
        print(f"Current version: {current_version}")
        print(f"Latest version: {latest_version}")

        if current_version != latest_version:
            print("Updating to the latest version...")
            subprocess.run(["pm2", "delete", pm2_name])
            subprocess.run(["git", "pull"])
            subprocess.run(["pip", "install", "-r", "requirements.txt"])
            subprocess.run(["pip", "install", "-e", "."])
            subprocess.run(
                [
                    "pm2",
                    "start",
                    "neurons/validator.py",
                    "--interpreter",
                    "python3",
                    "--name",
                    pm2_name,
                    "--",
                    "--wallet.name",
                    wallet_name,
                    "--wallet.hotkey",
                    wallet_hotkey,
                    "--netuid",
                    netuid,
                    "--subtensor.network",
                    network,
                    "--subtensor.chain_endpoint",
                    address,
                    "--axon.port",
                    axon_port,
                    "--logging.debug",
                    "--logging.trace",
                    "--neuron.sample_size",
                    str(sample_size),
                ]
            )
        time.sleep(900)  # sleep for 15 mins


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Automatically update and restart the validator process when a new version is released.",
        epilog="Example usage: python start_validator.py --pm2_name 'ca-validator' --wallet_name 'wallet1' --wallet_hotkey 'key123' [--address 'wss://...']",
    )

    parser.add_argument("--pm2_name", required=True, help="Name of the PM2 process.")
    parser.add_argument("--wallet_name", required=True, help="Name of the wallet.")
    parser.add_argument("--wallet_hotkey", required=True, help="Hotkey for the wallet.")
    parser.add_argument(
        "--subtensor_chain_endpoint",
        default=default_chain_endpoint,
        help="Subtensor chain_endpoint, defaults to 'wss://bittensor-finney.api.onfinality.io/public-ws' if not provided.",
    )
    parser.add_argument(
        "--subtensor_network",
        default="local",
        help="Network type, defaults to 'local' if not provided.",
    )
    parser.add_argument(
        "--netuid", default=24, help="Subnet uid, defaults to 24 if not provided."
    )
    parser.add_argument(
        "--axon_port", default=8091, help="Axon port, defaults to 8091 if not provided."
    )

    args = parser.parse_args()

    print(args)

    try:
        # update_and_restart(
        #     args.pm2_name,
        #     args.wallet_name,
        #     args.wallet_hotkey,
        #     args.subtensor_chain_endpoint,
        #     args.subtensor_network,
        #     args.netuid,
        #     args.axon_port,
        # )
        start_validator(
            args.pm2_name,
            args.wallet_name,
            args.wallet_hotkey,
            args.subtensor_chain_endpoint,
            args.subtensor_network,
            args.netuid,
            args.axon_port,
        )
    except Exception as e:
        parser.error(f"An error occurred: {e}")
