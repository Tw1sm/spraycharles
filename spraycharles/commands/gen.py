import typer
import json
from collections import OrderedDict

from spraycharles.lib.logger import init_logger, logger

app = typer.Typer()
COMMAND_NAME = 'gen'
HELP =  'Generate custom password lists from JSON file'


@app.callback(no_args_is_help=True, invoke_without_command=True)
def main(
    infile:     str = typer.Argument(..., exists=True, help="Filepath of the JSON file (example in repo's extras folder)"),
    outfile:    str = typer.Argument(..., writable=True, help="Name and path of the output file")):
    
    init_logger(False)
    
    logger.info(f"Reading {infile} ...")
    try:
        with open(infile) as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"Error reading {infile}: {e}")
        exit(1)

    words = data["base_words"]
    num_ranges = data["number_ranges"]
    spec_chars = data["special_characters"]
    min_length = data["minimum_length"]

    ranges = []

    
    # Append the following combinations to the final list:
    #     1. Word + number
    #     2. Word + 0 + number (if 0 < number < 9 to get 01, 02, etc..)
    #     3. Word + number + special char
    #     4. Word + 0 + number + special char (if 0 < number < 9)
    #     5. Word + special char
    

    for r in num_ranges:
        min_max = r.split(",")
        ranges.append(range(int(min_max[0]), int(min_max[1])))

    spray_list = []

    for word in words:
        for rng in ranges:
            for num in rng:
                spray_list = append(spray_list, word + str(num), min_length)
                if num in range(1, 10):
                    spray_list = append(spray_list, word + "0" + str(num), min_length)
                for char in spec_chars:
                    spray_list = append(spray_list, word + str(num) + char, min_length)
                    if num in range(1, 10):
                        spray_list = append(
                            spray_list, word + "0" + str(num) + char, min_length
                        )
            for char in spec_chars:
                spray_list = append(spray_list, word + char, min_length)

    # 
    # Remove duplicates and preserve order
    #
    spray_list = list(OrderedDict.fromkeys(spray_list))

    with open(outfile, "w") as f:
        f.write("\n".join(spray_list))
    logger.info(f"Password list written to {outfile}")


#
# Append if word meets min length
#
def append(wordlist, word, min_length):
    if len(word) >= min_length:
        wordlist.append(word)
    return wordlist
