#!/usr/bin/env python3

import numpy 
import csv
import argparse


class Color:
    green = '\033[92m'
    yellow = '\033[93m'
    blue = '\033[94m'
    red = '\033[91m'
    end = '\033[0m'

    def color_print(self, string, color, end='\n'):
        print(color + string + self.end, end=end)


class Analyzer:

    def __init__(self, resultsfile):
        self.resultsfile = resultsfile
        self.colors = Color()


    def analyze(self):
        response_codes = []
        response_lengths = []

        try:
            with open(self.resultsfile, newline='') as resultsfile:
                reader = csv.reader(resultsfile, delimiter=',',)
                responses = list(reader)
        except Exception as e:
            self.colors.color_print('[!] Error reading from file: %s' % (self.resultsfile), self.colors.red)
            print(e)
            exit()


        # remove header row from list
        del responses[0]
        
        len_with_timeouts = len(responses)
        # remove lines with timeouts
        responses = [line for line in responses if line[3] != 'TIMEOUT']
        timeouts = len_with_timeouts - len(responses)

        for indx, line in enumerate(responses):
            response_lengths.append(int(line[3]))
            response_codes.append(int(line[2]))

        # find outlying response lengths
        length_elements = numpy.array(response_lengths)
        length_mean = numpy.mean(length_elements, axis=0)
        length_sd = numpy.std(length_elements, axis=0)
        length_outliers = [x for x in length_elements if(x > length_mean + 2 * length_sd or x < length_mean - 2 * length_sd)]

        len_indicies = []

        # find username / password combos with matching response lengths
        for hit in length_outliers:
            len_indicies += [i for i,x in enumerate(responses) if x[3] == str(hit)]
        
        # print out logins with outlying response lengths
        if len(len_indicies) > 0:
            self.colors.color_print('[+] Possible hits based off response length:', self.colors.green)
        else:
            self.colors.color_print('[-] Not enough data to determine statistical significance of response length or no outliers found', self.colors.red)
            
        for x in len_indicies:
            print('\t%s:%s' % (responses[x][0], responses[x][1]))


def main():
    parser = argparse.ArgumentParser(description='Reads output file from script and analyzes reponse lengths for successful login attempts')
    parser.add_argument('input', type=str, help='script output file to analyze')
    args = parser.parse_args()

    analyzer = Analyzer(args.input)
    analyzer.analyze()


if __name__ == '__main__':
    main()