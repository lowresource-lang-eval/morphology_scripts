#!/usr/bin/python
# -*- coding: utf-8 -*
from re import match
import sys

COLCOUNT = 10
ID,FORM,LEMMA,UPOS,XPOS,FEATS,HEAD,DEPREL,DEPS,MISC = range(COLCOUNT)
COLNAMES = 'ID,FORM,LEMMA,UPOS,XPOS,FEATS,HEAD,DEPREL,DEPS,MISC'.split(',')

POS = ['ADJ', 'ADP', 'ADV', 'AUX', 'CCONJ', 'DET', 'INTJ', 'NOUN', 'NUM', 'PART', 'PRON', 'PROPN', 'PUNCT', 'SCONJ', 'SYM', 'VERB', 'X', 'PREP', 'POSTP', 'UNKN']


def validate(filename_in, filename_out):

    is_new_sentence = True
    common_result = True
    line_number = 0
    errors = []

    def new_error(line_number, col_name, field_value, message):
        global common_result
        common_result = False
        errors.append('{}; invalid field: {}: {}: {}'.format(line_number, col_name, field_value, message))

    with open(filename_in, 'r', encoding='utf-8') as f:
        for line in f:
            line_number += 1
            if line[0] == '#':
                continue
            elif line == '\n':
                is_new_sentence = True
                continue
            else:
                fields = line.split('\t')
                if not len(fields) == 10:
                    errors.append(str(line_number) + '; wrong number of fields')
                    common_result = False
                else:
                    if not match(r'((\d+)|((\d+)-\d+)|((\d+).\d+))', fields[ID]):
                        new_error(line_number, 'ID', fields[ID], 'wrong format')
                    if (is_new_sentence == True and int(fields[ID].split('-')[0]) != 1) or (is_new_sentence == False and int(fields[ID].split('-')[0]) != prev_id + 1 and int(fields[ID].split('-')[0]) != prev_id) or (len(fields[ID].split('-')) > 1 and int(fields[ID].split('-')[1]) <= int(fields[ID].split('-')[0])):
                        new_error(line_number, 'ID', fields[ID], 'incorrect value')
                    if fields[FORM] == '':
                        new_error(line_number, 'FORM', fields[FORM], 'empty')
                    if fields[LEMMA] == '':
                        new_error(line_number, 'LEMMA', fields[LEMMA], 'empty')
                    if fields[UPOS] != '_' and fields[UPOS] not in POS:
                        new_error(line_number, 'UPOS', fields[UPOS], 'wrong format')
                    if fields[XPOS] == '':
                        new_error(line_number, 'XPOS', fields[XPOS], 'empty')
                    if fields[FEATS] != '_' and not match(r'(([A-Z0-9][A-Z0-9a-z]*=[A-Z0-9][a-zA-Z0-9]*)(\u007c([A-Z0-9][A-Z0-9a-z]*=[A-Z0-9][a-zA-Z0-9]*))*(#(([A-Z0-9][A-Z0-9a-z]*=[A-Z0-9][a-zA-Z0-9]*)(\u007c([A-Z0-9][A-Z0-9a-z]*=[A-Z0-9][a-zA-Z0-9]*))*)))*', fields[FEATS]):
                    #or (match(r'\w+=\w+\u007c\w+=\w+#\w+=\w+\u007c\w+=\w+', fields[FEATS]) and (fields[FEATS].split('#')[0].split('|')[0].split('=')[0] != fields[FEATS].split('#')[1].split('|')[0].split('=')[0] or fields[FEATS].split('#')[0].split('|')[1].split('=')[0] != fields[FEATS].split('#')[1].split('|')[1].split('=')[0]))):
                        new_error(line_number, 'FEATS', fields[FEATS], 'wrong format')
                    if fields[HEAD] == '':
                        new_error(line_number, 'HEAD', fields[HEAD], 'empty')
                    if fields[DEPREL] == '':
                        new_error(line_number, 'DEPREL', fields[DEPREL], 'empty')
                    if fields[DEPS] == '':
                        new_error(line_number, 'DEPS', fields[DEPS], 'empty')
                    if fields[MISC] in ('', '\n'):
                        new_error(line_number, 'MISC', fields[MISC], 'empty')

                    prev_id = int(fields[ID].split('-')[0])
                    is_new_sentence = False

    with open(filename_out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(errors))


def main():
    if len(sys.argv) < 2:
        print("usage: corpora_validation.py filename")
        return
    filename = sys.argv[1]
    filename_out = filename + '_errors.txt'
    validate(filename, filename_out)

if __name__ == '__main__':
    main()