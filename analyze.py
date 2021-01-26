#!/usr/bin/env python3

import numpy 
import csv
import argparse
from texttable import Texttable

class Color:
    green = '\033[92m'
    yellow = '\033[93m'
    blue = '\033[94m'
    red = '\033[91m'
    grey = '\033[37m'
    end = '\033[0m'


    def color_print(self, string, color, end='\n'):
        print(color + string + self.end, end=end)


class Analyzer:

    def __init__(self, resultsfile):
        self.resultsfile = resultsfile
        self.colors = Color()


    def analyze(self):
        #response_codes = []
        response_lengths = []

        try:
            with open(self.resultsfile, newline='') as resultsfile:
                print()
                print('[*] Reading spray data from CSV...')
                reader = csv.reader(resultsfile, delimiter=',',)
                responses = list(reader)
        except Exception as e:
            self.colors.color_print('[!] Error reading from file: %s' % (self.resultsfile), self.colors.red)
            print(e)
            exit()


        # Get the columns we need for analysis
        code_col_index = -1
        length_col_index = -1
        user_col_index = -1
        pass_col_index = -1


        for idx, header in enumerate(responses[0]):
            # if output from smb spray, just pull successes then exit
            if header.lower() == 'smb login':
                self.smb_analyze(responses)
                exit()
            elif header.lower() == 'response code':
                code_col_index = idx
            elif header.lower() == 'response length':
                length_col_index = idx
            elif header.lower() == 'username':
                user_col_index = idx
            elif header.lower() == 'password':
                pass_col_index = idx


        # Make sure each of our needed columns exist
        if code_col_index < 0   :   print('[!] CSV is missing column with header \'Response Code\'')
        if length_col_index < 0 :   print('[!] CSV is missing column with header \'Response Length\'')
        if user_col_index < 0   :   print('[!] CSV is missing column with header \'Username\'')
        if pass_col_index < 0   :   print('[!] CSV is missing column with header \'Password\'')

        # remove header row from list
        del responses[0]
        
        len_with_timeouts = len(responses)
        # remove lines with timeouts
        responses = [line for line in responses if line[length_col_index] != 'TIMEOUT']
        timeouts = len_with_timeouts - len(responses)

        # Get the response length column for analysis
        for indx, line in enumerate(responses):
            response_lengths.append(int(line[length_col_index]))
            #response_codes.append(int(line[code_col_index]))

        print('[*] Calculating mean and standard deviation of response lengths...')

        # find outlying response lengths
        length_elements = numpy.array(response_lengths)
        length_mean = numpy.mean(length_elements, axis=0)
        length_sd = numpy.std(length_elements, axis=0)
        print('[*] Checking for outliers...')
        length_outliers = [x for x in length_elements if(x > length_mean + 2 * length_sd or x < length_mean - 2 * length_sd)]

        length_outliers = list(set(length_outliers))
        len_indicies = []

        # find username / password combos with matching response lengths
        for hit in length_outliers:
            len_indicies += [i for i,x in enumerate(responses) if x[length_col_index] == str(hit)]
        
        # print out logins with outlying response lengths
        if len(len_indicies) > 0:
            self.colors.color_print('[+] Identified potential sussessful logins!\n', self.colors.green)
            table = Texttable()
            table.header(['Username', 'Password'])
            for x in len_indicies:
                table.add_row([responses[x][user_col_index], responses[x][pass_col_index]])
            print(table.draw())
        else:
            self.colors.color_print('[-] No outliers found or not enough data to find statistical significance', self.colors.red)

        print()


    # check for smb success not HTTP
    def smb_analyze(self, responses):
        successes = []
        for line in responses[1:]:
            if line[2] != 'STATUS_LOGON_FAILURE':
                successes.append(line)

        if len(successes) > 0:
            self.colors.color_print('[+] Identified sussessful SMB logins!\n', self.colors.green)
            table = Texttable()
            table.header(['Username', 'Password'])
            for x in successes:
                table.add_row([x[0], x[1]])
            print(table.draw())
        else:
            self.colors.color_print('[-] No successful SMB logins', self.colors.red)
        print()

def main():
    parser = argparse.ArgumentParser(description='Reads output file from script and analyzes reponse lengths for successful login attempts')
    parser.add_argument('input', type=str, help='script output file to analyze')
    args = parser.parse_args()

    analyzer = Analyzer(args.input)
    analyzer.analyze()


if __name__ == '__main__':
    main()