#!/usr/bin/python3
# -*- coding: utf-8 -*
__author__ = "gisly"

import sys

def evaluate_ud(filename_standard, filename_test):
    result = compare_files_ud(filename_standard, filename_test)
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

def compare_files_ud(filename_standard, filename_test):
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

    alternative_lemma = None
    alternative_pos = None
    while i < len (standard_lines):
        if j >= len(test_lines):
            print("ERROR: test file not fully used")
            break
        while j < len(test_lines):



            current_test_line = test_lines[j].strip()
            current_standard_line = standard_lines[i].strip()


            if current_standard_line.startswith('#'):
                i += 1
                continue
            if current_test_line.startswith('#'):
                j += 1
                continue

            if current_test_line == '' and current_standard_line != '':
                result['fatal'] = 'Fatal error: bad line #%s: expected non-empty line' % j
                return result
            if current_standard_line == '' and current_test_line != '':
                result['fatal'] = 'Fatal error: bad line #%s: expected empty line' % j
                return result
            #new sentence border
            if current_test_line == '':
                i += 1
                j += 1

                continue


            #print(i, j, current_standard_line, current_test_line)
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

            if current_standard_line_number.startswith('1'):
                total_sentences += 1
                is_sentence_lemma_correct = False
                is_sentence_pos_correct = False
                alternative_lemma = None
                alternative_pos = None

            total_words += 1

            current_test_line_wordform = current_test_line_parts[1]
            current_standard_line_wordform = current_standard_line_parts[1]
            current_test_line_lemma = current_test_line_parts[2]
            current_standard_line_lemma = current_standard_line_parts[2]
            current_test_line_pos = current_test_line_parts[3]
            current_standard_line_pos = current_standard_line_parts[3]
            current_test_line_features = current_test_line_parts[5]
            current_standard_line_features = current_standard_line_parts[5]


            if current_test_line_wordform != current_standard_line_wordform:
                errors.append('Error: bad line #%s: expected different wordform' % j)
            else:
                #comparing lemma
                if is_lemma_equal(current_standard_line_lemma, current_test_line_lemma)\
                        or (alternative_lemma is not None and
                                is_lemma_equal(alternative_lemma, current_test_line_lemma)):
                    num_words_correct_lemma += 1
                    if not is_sentence_lemma_correct:
                        is_sentence_lemma_correct = True
                        num_sentences_correct_lemma += 1
                #comparing pos
                if is_pos_equal(current_standard_line_pos, current_test_line_pos) \
                        or (alternative_pos is not None and is_pos_equal(alternative_pos, current_test_line_pos)):
                    num_words_correct_pos += 1
                    if not is_sentence_pos_correct:
                        is_sentence_pos_correct = True
                        num_sentences_correct_pos += 1
                else:
                    print(current_standard_line_pos, alternative_pos, current_test_line_pos)
                #comparing features
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
    if len(sys.argv) < 3:
        print('usage: evaluation_ud.py <gold.standard.filename> <predict.filename>')
        return
    filename_standard = sys.argv[1]
    filename_predict = sys.argv[2]
    evaluate_ud(filename_standard, filename_predict)

if __name__ == '__main__':
    main()
