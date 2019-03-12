#!/usr/bin/python3
# -*- coding: utf-8 -*
__author__ = "gisly"

import sys

"""
drovoseq: please specify is_to_check_prev_num = False, is_to_use_original_sentences = False
SPUMorph: please specify is_to_check_prev_num = False, is_to_use_original_sentences = True
DeepPavlov: please specify is_to_check_prev_num = True, is_to_use_original_sentences = True
"""
def evaluate_ud(filename_standard, filename_test, is_to_check_prev_num = False,
                is_to_use_original_sentences = False):
    result = compare_files_ud(filename_standard, filename_test, is_to_check_prev_num, is_to_use_original_sentences)
    filename_result = filename_test + '_result_ud.txt'
    with open(filename_result, 'w', encoding='utf', newline='') as fout:
        if 'fatal' in result:
            fout.write(result['fatal'] + '\n')
        else:
            fout.write('Share of words with correct pos: %s\n' % result['words_correct_pos'])
            fout.write('Share of words with correct lemma: %s\n' % result['words_correct_lemma'])
            fout.write('Share of sentences with correct pos: %s\n' % result['sentences_correct_pos'])
            fout.write('Share of sentences with correct lemma: %s\n' % result['sentences_correct_lemma'])
            fout.write('Feature precision: %s\n' % result['precision'])
            fout.write('Feature recall: %s\n' % result['recall'])
            fout.write('Feature F2: %s\n' % result['f2'])
            fout.write('Errors: ' + ','.join(result['errors']) + '\n')
    print('written results to %s' % filename_result)

def compare_files_ud(filename_standard, filename_test, is_to_check_prev_num, is_to_use_original_sentences):
    standard_lines = read_lines(filename_standard)
    test_lines = read_lines(filename_test)
    i = 0
    j = 0
    errors = []
    num_words_correct_pos = 0
    num_sentences_correct_pos = 0
    num_words_correct_lemma = 0
    num_sentences_correct_lemma = 0
    is_sentence_pos_correct = False
    is_sentence_lemma_correct = False

    num_retr_relevant = 0
    num_retr = 0
    num_relevant = 0

    total_words = 0
    total_sentences = 0

    result = dict()

    from_num = -1
    to_num = -1
    prev_test_line_number = ''

    alternative_lemma = None
    alternative_pos = None
    while i < len (standard_lines):
        if j >= len(test_lines):
            print("ERROR: test file not fully used")
            break
        while j < len(test_lines):



            current_test_line = test_lines[j].strip()
            if i >= len(standard_lines):
                break
            current_standard_line = standard_lines[i].strip()



            if current_standard_line.startswith('#'):
                i += 1
                continue
            if current_test_line.startswith('#'):
                j += 1
                continue

            if current_test_line.strip() == "_	_	_	_":
                current_test_line = ''
                prev_test_line_number = ''

            #new sentence border
            if current_test_line == '' and current_standard_line == '':
                i += 1
                j += 1
                continue
            if current_test_line == '':
                j += 1
                continue

            if current_standard_line == '':
                i += 1
                continue


            if '@' in current_standard_line:
                alternative_lemma_pos = current_standard_line.split('@')[-1].split('\t')
                current_standard_line = current_standard_line.split('@')[0]
                alternative_lemma = alternative_lemma_pos[0]
                alternative_pos = alternative_lemma_pos[1]

            current_test_line_parts = current_test_line.split('\t')
            current_standard_line_parts = current_standard_line.split('\t')


            current_test_line_number = current_test_line_parts[0]
            current_standard_line_number = current_standard_line_parts[0]

            if '-' in current_standard_line_number and '-' in current_test_line_number:
                j += 1
                i += 1
                continue
            #TODO!
            if '-' in current_standard_line_number:
                num_parts = current_standard_line_number.split("-")
                from_num = int(num_parts[0])
                to_num = int(num_parts[1])
            elif int(current_standard_line_number) >= from_num  and int(current_standard_line_number) <= to_num:
                i += 1
                if int(current_standard_line_number) == to_num:
                    from_num = -1
                    to_num = -1
                continue

            if is_to_check_prev_num and (current_test_line_number == prev_test_line_number):
                j += 1
                continue


            if current_test_line_number == '1' and ((not is_to_check_prev_num) or (prev_test_line_number != '1')):
                if is_sentence_lemma_correct:
                    num_sentences_correct_lemma += 1
                if is_sentence_pos_correct:
                    num_sentences_correct_pos += 1
                total_sentences += 1
                is_sentence_lemma_correct = True
                is_sentence_pos_correct = True
                alternative_lemma = None
                alternative_pos = None

            if is_to_use_original_sentences and current_standard_line_number == '1':
                if is_sentence_lemma_correct:
                    num_sentences_correct_lemma += 1
                if is_sentence_pos_correct:
                    num_sentences_correct_pos += 1
                total_sentences += 1
                is_sentence_lemma_correct = True
                is_sentence_pos_correct = True
                alternative_lemma = None
                alternative_pos = None

            prev_test_line_number = current_test_line_number

            total_words += 1

            current_test_line_wordform = current_test_line_parts[1]
            current_standard_line_wordform = current_standard_line_parts[1]


            if(current_standard_line_wordform != current_test_line_wordform):
                print(current_standard_line_wordform, current_test_line_wordform)


            current_test_line_lemma = current_test_line_parts[2]
            current_standard_line_lemma = current_standard_line_parts[2]
            current_test_line_pos = current_test_line_parts[3]
            current_standard_line_pos = current_standard_line_parts[3]
            current_standard_line_features = current_standard_line_parts[5]

            if len(current_test_line_parts) > 5:
                current_test_line_features = current_test_line_parts[5]
            else:
                current_test_line_features = []


            if current_test_line_wordform != current_standard_line_wordform:

                errors.append('Error: bad line #%s: expected different wordform' % j)
            else:
                #comparing lemma
                if is_lemma_equal(current_standard_line_lemma, current_test_line_lemma)\
                        or (alternative_lemma is not None and
                                is_lemma_equal(alternative_lemma, current_test_line_lemma)):
                    num_words_correct_lemma += 1
                else:
                    is_sentence_lemma_correct = False
                #comparing pos
                if is_pos_equal(current_standard_line_pos, current_test_line_pos) \
                        or (alternative_pos is not None and is_pos_equal(alternative_pos, current_test_line_pos)):
                    num_words_correct_pos += 1
                else:
                    is_sentence_pos_correct = False
                #comparing features
                if current_test_line_features:
                    current_num_retr_relevant, current_num_retr, current_num_relevant = \
                                compare_features(current_test_line_features, current_standard_line_features)
                    num_retr_relevant += current_num_retr_relevant
                    num_retr += current_num_retr
                    num_relevant += current_num_relevant
            i += 1
            j += 1
    result['errors'] = errors
    result['words_correct_pos'] = float(num_words_correct_pos) / float(total_words)
    result['sentences_correct_pos'] = float(num_sentences_correct_pos) / float(total_sentences)
    result['words_correct_lemma'] = float(num_words_correct_lemma) / float(total_words)
    result['sentences_correct_lemma'] = float(num_sentences_correct_lemma) / float(total_sentences)
    if num_retr == 0:
        precision = 0
    else:
        precision = float(num_retr_relevant) / float(num_retr)
    recall = float(num_retr_relevant) / float(num_relevant)
    f2 = 2 * precision * recall / (precision + recall)
    result['precision'] = precision
    result['recall'] = recall
    result['f2'] = f2

    return result


def is_pos_equal(pos_standard, pos_test):
    if pos_standard == '_':
        return True
    if pos_standard == 'X':
        return True
    if pos_standard == pos_test:
        return True
    if pos_standard == 'NOUN' and pos_test == 'PROPN':
        return True
    if pos_test == 'NOUN' and pos_standard == 'PROPN':
        return True
    return False

def is_lemma_equal(lemma_standard, lemma_test):
    if lemma_standard == 'UNKN':
        return True
    return lemma_standard.lower() == lemma_test.lower()

def compare_features(features_standard, features_test):
    features_standard_set = set(features_standard.split('|'))
    features_test_set = set(features_test.split('|'))
    num_retr_relevant = len(features_standard_set.intersection(features_test_set))
    num_retr = len(features_test_set)
    num_relevant = len(features_standard_set)
    return num_retr_relevant, num_retr, num_relevant


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
    if len(sys.argv) < 5:
        print('usage: evaluation_ud.py <gold.standard.filename> <predict.filename> <is_check_prev_num> <is_to_use_original_sentences>')
        return
    filename_standard = sys.argv[1]
    filename_predict = sys.argv[2]
    is_check_prev_num = (sys.argv[3] == '1')
    is_to_use_original_sentences = (sys.argv[4] == '1')

    evaluate_ud(filename_standard, filename_predict, is_check_prev_num, is_to_use_original_sentences)

if __name__ == '__main__':
    main()


