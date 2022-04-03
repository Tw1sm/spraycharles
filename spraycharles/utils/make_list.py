#!/usr/bin/env python
import argparse
import json
from collections import OrderedDict


def arg():
    parser = argparse.ArgumentParser(
        description="Creates a spray list based on the configs in list_elements.json",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    return parser.parse_args()


# append word to list given it meets length req
def append(wordlist, word, min_length):
    if len(word) >= min_length:
        wordlist.append(word)
    return wordlist


def main():
    args = arg()

    # load configs from json file
    with open("list_elements.json") as f:
        data = json.load(f)

    words = data["base_words"]
    num_ranges = data["number_ranges"]
    spec_chars = data["special_characters"]
    min_length = data["minimum_length"]

    ranges = []

    """
    Append the following combinations to the final list:
        1. Word + number
        2. Word + 0 + number (if 0 < number < 9 to get 01, 02, etc..)
        3. Word + number + special char
        4. Word + 0 + number + special char (if 0 < number < 9)
        5. Word + special char
    """

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

    # remove duplicates and preserve order
    spray_list = list(OrderedDict.fromkeys(spray_list))

    with open("custom_passwords.txt", "w") as f:
        f.write("\n".join(spray_list))


if __name__ == "__main__":
    main()
