import requests
import re
import bittensor as bt

def get_version(line_number: int = 54):
    # The raw content URL of the file on GitHub
    raw_url = 'https://raw.githubusercontent.com/vn-automata/bt-automata/main/bt_automata/__init__.py'

    # Send an HTTP GET request to the raw content URL
    response = requests.get(raw_url)

    # Check if the request was successful
    if response.status_code == 200:
        content = response.text.split('\n')  # Split the content by new line
        if len(content) >= line_number:
            version_line = content[line_number - 1]
            version_match = re.search(r'__version__ = "(.*?)"', version_line)

            if not version_match:
                raise Exception("Version information not found in the specified line")
            return version_match.group(1)
        else:
            bt.logging.error(f"The file has only {len(content)} lines.")
    else:
        bt.logging.error(f"Failed to fetch file content. Status code: {response.status_code}")
