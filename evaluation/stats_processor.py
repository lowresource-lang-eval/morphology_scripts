#!/usr/bin/python
# -*- coding: utf-8 -*
__author__ = "gisly"
import sys
import operator


def check_conll_file(filename):
    bad_line_nums = []
    lemmas_freq = dict()
    unique_letters = set()
    with open(filename, 'r', encoding='utf-8') as fin:
        for index, line in enumerate(fin):
            line = line.strip()
            if line.startswith("#") or line == '':
                continue
            line_parts = line.strip().split("\t")
            if len(line_parts) < 3:
                bad_line_nums.append(index + 1)
                continue

            word_form = line_parts[1]
            word_lemma = line_parts[2]
            for word_char in word_form:
                unique_letters.add(word_char)
            for word_char in word_lemma:
                unique_letters.add(word_char)
            if word_lemma in lemmas_freq:
                lemmas_freq[word_lemma] += 1
            else:
                lemmas_freq[word_lemma] = 1
    return lemmas_freq, unique_letters, bad_line_nums



def count_corpus_stats(filename):
    filename_result = filename + '_analysis.txt'
    lemmas_freq, unique_letters, bad_line_nums = check_conll_file(filename)
    lemmas_freq_sorted = sorted(lemmas_freq.items(), key=operator.itemgetter(1), reverse=True)
    unique_letters_sorted = sorted(list(unique_letters))
    with open(filename_result, 'w', encoding='utf-8') as fout:
        fout.write("==============Unique letters:===============\n")
        for unique_letter in unique_letters_sorted:
            fout.write(unique_letter + '\n')
        fout.write("==============Lemma frequency:===============\n")
        for lemma, count in lemmas_freq_sorted:
            fout.write(lemma + ':' + str(count) + '\n')
        fout.write("===============Bad line numbers:==============\n")
        for bad_line_num in bad_line_nums:
            fout.write(str(bad_line_num) + '\n')
    print('wrote analysis results to %s' % filename_result)


def main():
    if len(sys.argv) < 2:
        print("usage: stats_processor.py filename")
        return
    count_corpus_stats(sys.argv[1])

if __name__ == '__main__':
    main()
