#!/usr/bin/python
# -*- coding: utf-8 -*
__author__ = "gisly"

import re
import pymorphy2
morph = pymorphy2.MorphAnalyzer()

DUMMIES = ['aŋi']

RUSSIAN_NUMS = ['один', 'два', 'три', 'четыре', 'пять',
                'шесть', 'семь', 'восемь', 'девять', 'десять',
                'двадцать', 'тридцать', 'сорок', 'пятьдесят', 'шестьдесят',
                'семьдесят', 'восемьдесят', 'девяносто', 'сто', 'сотня',
                'тысяча',
                'один(о.человеке)', 'один(о.людях)']

RUSSIAN_PRONOUNS = ['1SG', '2SG',
                    '3SG',
                    '1PL(EXCL)', '1PL(INCL)',
                    '1PL(INCL).DUAL',
                    '2PL', '3PL',
                    '1SG.ACC', '2SG.ACC', '3SG.ACC',
                    '1PL(EXCL).ACC', '2PL.ACC',
                    'кто',
                    'что', 'это',
                    'друг.друга']

RUSSIAN_DETERMINERS = ['тот', 'тот.ACC', 'этот', 'какой', 'весь']

RUSSIAN_ADVERBS = ['один.раз', 'на.улице', 'на.улицу',
                   'против.течения', 'по.течению',
                   'вверх.по.течению', 'вниз.по.течению',
                   'вниз.по.склону', 'в.ту.сторону',
                   'против', 'по.склону.горы',
                   'в.лес', 'в.лесу',
                   'из.леса',
                   'до.сих.пор', 'на.другой.берег',
                   'в.прошлом.году',
                   'сколько']

RUSSIAN_CCONJ = ['и']

RUSSIAN_SCONJ = ['чтоб', 'чтобы', 'если', 'когда', 'как']



GLOSSES_VERBAL = ['IPFV', 'NFUT', 'FUT', 'FUTCNT',
                  'PST', 'PSTITER',
                  '1SG', '2SG', '3SG',
                  '1PL(EXCL)', '1PL(INCL)', '2PL', '3PL',
                  'PRGRN',
                  'QA',
                  'INF',
                  'INCEP',
                  'HABPROB',
                  'COND',
                  'PROB',
                  'INCH',
                  'DUR',
                  'PANT', 'PPOST', 'PSIM', 'PSIMN',
                  'PHAB', 'PNEG', 'PIMMFUT',
                  'PFICT', 'PIMPDEB', 'PPF',

                  ]

GLOSSES_VERBAL_PREFIXES = ['VBLZ', 'CV', 'IMPER']
GLOSSES_ADJ_PREFIXES = ['ADJ', 'ATR', 'EQT',
                        'сильный(о.проявлении.качества)']
GLOSSES_ADV_PREFIXES = ['ADVZ', 'EVERY']
GLOSSES_NOUN_PREFIXES = ['NMLZ', 'DATLOC', 'LOCALL', 'ACC', 'ACCIN', 'ABL', 'ALL',
                         'INSTR','COM','VOC','COM.FAM','LOCDIR', 'ELAT',
                         'PROL',
                         'COLL', 'FAM',
                         'INDPS',
                         'DEADREL',
                         ]

GLOSSES_PROPER_PREFIXES = ['HYDR.NAME', 'GEOGR']
GLOSSES_SLIP = ['SLIP', 'hes', 'HES', '?', 'нрзб']

NEGATIVE_ROOTS = ['āči', 'āčin', 'ači', 'ačin',
                          'āśi', 'āśin', 'aśi', 'aśin']


BAD_CHARACTERS = '[ˀ∅Øø…\?\-\.,\*]'

REGEX_ADDITIONAL_INFO = '(.)((\[|\(|{).+?(\]|\)|}))'
REGEX_NOT_LAST_CHARACTER = '=(.)'

FON_REPLACEMENTS = {
                    BAD_CHARACTERS : '',
                    REGEX_ADDITIONAL_INFO : (lambda x: x.group(1)),
                    REGEX_NOT_LAST_CHARACTER : (lambda x: x.group(1)),
                    'ɒ' : 'o',
                    'ɔ' : 'o',
                    'ε' : 'e',
                    'č' : 't͡ʃ',
                    'd\'': 'ď',
                    'd’' : 'd',
                    '\u01EF' : 'ď',
                    't\'' : 'ť',
                    't’' : 'ť',
                    'ń' : 'ɲ',
                    'n\u0301': 'ɲ',
                    'n\'' : 'ɲ',
                    'n’' : 'ɲ',
                    'l’' : 'l',
                    'ĺ' : 'l',
                    'ľ' : 'l',
                    'ŕ' : 'r',
                    's’' : 'ś',
                    's\'' : 'ś',
                    'š' : 'ʃ',
                    'ž' : 'ʒ',
                    'ɣ' : 'γ',
                    'χ' : 'x',
                    'ʍ' : 'f',
                    '{*}' : '',
                    '\/.+': '',
                    '[:̄̅]' : 'ː',

                    'ā' : 'aː',
                    'ă' : 'a',
                    'ē' : 'eː',
                    'í' : 'iː',
                    'ī' : 'iː',
                    'ō' : 'oː',
                    'ū' : 'uː',
                    'y' : 'i',
                    'ɨ' : 'i',
                    'ǝ' : 'ə',
                    'ɵ' : 'ə',
                    'ә' : 'ə',
                    }

FON_REPLACEMENTS_STAGE_2 = {
                        "'" : '',
                        '’' : '',
                        "\u0301" : '',
                        "[\[\]]": ''
                            }
DERIVATIVE_GLOSSES = ['ATTEN',
                      'DIM',
                      'CHILD', 'COVER', 'DAY', 'DEADREL', 'DER', 'DEST.FAG',
                       'EQT', 'EVERY', 'FAG', 'FAKE', 'GEOGR', 'INDEF',
                      'ONOM', 'PEJOR', 'PELT', 'PEOPLE',
                      'PREDEST', 'PRGRN', 'QUANT', 'REDIS', 'RESID',
                      'ROOM', 'RYTHM', 'SIDE'
                      ]
DERIVATIVE_GLOSS_PREFIXES = ['ADVZ', 'ADBLZ', 'ADJ', 'ATR', 'ADVR', 'AUG', 'INTER', 'NDEF',
                             'NMLZ', 'NMNLZ', 'VBLZ', 'VERB']

GLOSSES_TO_REPLACE = dict()

def get_russian_pos_set(russian_word):
    return set([p.tag.POS for p in morph.parse(russian_word)])

def is_proper_noun_translation(translation):
    return translation != 'NEG' and translation[0].isupper()

def is_interjection_translation(translation):
    return translation in ['INTJ', 'FOC']

def is_adjective_translation(possible_pos_set):
    return 'ADJF' in possible_pos_set or \
            'PRTF' in possible_pos_set

def is_numeric_translation(translation):
    return translation in RUSSIAN_NUMS

def is_pronoun_translation(fon, translation):
    return fon not in DUMMIES and translation in RUSSIAN_PRONOUNS

def is_c_conjunction_translation(translation):
    return translation in RUSSIAN_CCONJ

def is_s_conjunction_translation(translation):
    return translation in RUSSIAN_SCONJ

def is_adverb_translation(translation, possible_pos_set):
    return (translation in RUSSIAN_ADVERBS) or \
            'ADVB' in possible_pos_set or \
            'COMP' in possible_pos_set



def is_determiner_translation(translation, analysis):
    if translation in RUSSIAN_DETERMINERS:
        return True
    return translation in RUSSIAN_PRONOUNS \
            and len(analysis) > 1 \
            and analysis[1] == 'PROPR'

def is_slip(gloss):
    return 'SLIP' in gloss


def is_verb_gloss(gloss):
    return gloss in GLOSSES_VERBAL or has_prefix(gloss, GLOSSES_VERBAL_PREFIXES)


def is_adjective_gloss(gloss):
    return has_prefix(gloss, GLOSSES_ADJ_PREFIXES)


def is_adverb_gloss(gloss):
    return has_prefix(gloss, GLOSSES_ADV_PREFIXES)


def is_noun_gloss(gloss):
    return has_prefix(gloss, GLOSSES_NOUN_PREFIXES)


def is_proper_noun_gloss(gloss):
    return has_prefix(gloss, GLOSSES_PROPER_PREFIXES)


def is_noun_negation(first_fon, first_gloss):
    return first_gloss == 'NEG' and \
            first_fon in NEGATIVE_ROOTS

def is_slip_unknown(gloss):
    return has_prefix(gloss.strip('<').strip('['), GLOSSES_SLIP)

def has_prefix(gloss, PREFIX_LIST):
    for gloss_prefix in PREFIX_LIST:
        if gloss.startswith(gloss_prefix):
            return True
    return False

def is_cyrillic(token):
    return re.findall(r'[ЁёА-Яа-я]', token) != []

def is_cyrillic_only(token):
    return re.match(r'[ЁёА-Яа-я]+$', token) is not None

def normalize_glosses(analysis):
    normalized_glosses = [analysis[0]['gloss']]
    for analysis_part in analysis[1:]:
        gloss = analysis_part['gloss'].strip('-')
        normalized_glosses.append(normalize_gloss(gloss))
    return normalized_glosses

def normalize_gloss(gloss):
    if is_cyrillic_only(gloss):
        return gloss
    gloss = gloss.upper()
    gloss = gloss.replace('[SLIP]', '.SLIP')
    gloss = re.sub('\(([ЁёА-Яа-я]+).+?\)', '', gloss)
    gloss = re.sub('\[([ЁёА-Яа-я]+).+?\]', '', gloss)
    gloss = re.sub('[\[\]\-=\?\\\]', '', gloss)
    gloss = re.sub('{(\*)+}', '', gloss)


    if gloss in GLOSSES_TO_REPLACE:
        return GLOSSES_TO_REPLACE[gloss]
    return gloss

def normalize_token(token):
    token = token.lower()
    token = make_replacements(token, FON_REPLACEMENTS)
    token = make_replacements(token, FON_REPLACEMENTS_STAGE_2)
    return token

def make_replacements(token, replacement_dict):
    for replacement_pair in replacement_dict.items():
        token = re.sub(replacement_pair[0], replacement_pair[1], token)
    return token

def is_derivative(gloss):
    normalized_gloss = normalize_gloss(gloss)
    return normalized_gloss in DERIVATIVE_GLOSSES or \
           has_prefix(normalized_gloss, DERIVATIVE_GLOSS_PREFIXES)


def main():
    print(normalize_gloss('PNEG[SLIP]'))


if __name__ == '__main__':
    main()
