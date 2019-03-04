#!/usr/bin/python3
# -*- coding: utf-8 -*
__author__ = "gisly"
import sys
# pip install python-Levenshtein
from Levenshtein import distance

VARIANT_DELIMITER = '|'


def evaluate_syn(filename_standard, filename_test):
    """
    compares two files and writes the comparison result into a third one
    :param filename_standard: full path to the gold standard file (utf-8)
    :param filename_test: full path to the file being tested (utf-8)
    """
    result = compare_files_syn(filename_standard, filename_test)
    filename_result = filename_test + '_result_syn.txt'
    with open(filename_result, 'w', encoding='utf', newline='') as fout:
        fout.write(result + '\n')
    print('written results to %s' % filename_result)


def compare_files_syn(filename_standard, filename_test):
    standard_lines = read_lines(filename_standard)
    test_lines = read_lines(filename_test)
    total_number = len(standard_lines)
    if total_number != len(test_lines):
        return 'Error: wrong number of lines: received %s, expected %s' % (len(test_lines), total_number)
    num_totally_equal = 0
    levenshtein_dist_sum = 0
    for line_standard, line_test in zip(standard_lines, test_lines):
        # there may be several answers separated by a delimiter, and we choose the closest one
        line_test_variants = line_standard.split(VARIANT_DELIMITER)
        closest_distance = None
        for variant in line_test_variants:
            if variant == line_test:
                num_totally_equal += 1
                closest_distance = 0
                break
            current_distance = distance(variant, line_test)
            if closest_distance:
                closest_distance = min(closest_distance, current_distance)
            else:
                closest_distance = current_distance

        levenshtein_dist_sum += closest_distance
    levenshtein_dist_average = levenshtein_dist_sum / float(total_number)
    return 'Totally correct: %s out of %s; ' \
           'Average Levenshtein distance: %s' % (num_totally_equal, total_number, levenshtein_dist_average)


def read_lines(filename):
    """

    :param filename: filename of a utf-8 encoded file
    :return: an array of non-empty lines with whitespace stripped
    """
    lines = []
    with open(filename, 'r', encoding='utf') as fin:
        for line in fin:
            if line.strip() != '':
                lines.append(line.strip())
    return lines


def main():
    if len(sys.argv) < 3:
        print('usage: evaluation_syn.py <gold.standard.filename> <predict.filename>')
        return
    filename_standard = sys.argv[1]
    filename_predict = sys.argv[2]
    evaluate_syn(filename_standard, filename_predict)


if __name__ == '__main__':
    main()
