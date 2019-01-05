#!/usr/bin/python
# -*- coding: utf-8 -*
__author__ = "gisly"

import pymorphy2
morph = pymorphy2.MorphAnalyzer()

RUSSIAN_NUMS = ['один', 'два', 'три', 'четыре', 'пять',
                'шесть', 'семь', 'восемь', 'девять', 'десять',
                'двадцать', 'тридцать', 'сорок', 'пятьдесят', 'шестьдесят',
                'семьдесят', 'восемьдесят', 'девяносто', 'сто',
                'тысяча',
                'один(о.человеке)']

RUSSIAN_PRONOUNS = ['1SG', '2SG', '3SG',
                    '1PL(EXCL)', '1PL(INCL)',
                    '1PL(INCL).DUAL',
                    '2PL',
                    '1SG.ACC', '2SG.ACC',
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
                   'в.лес',
                   'до.сих.пор', 'на.другой.берег',
                   'в.прошлом.году']

RUSSIAN_CCONJ = ['и']

RUSSIAN_SCONJ = ['чтоб', 'чтобы', 'если', 'когда']



GLOSSES_VERBAL = ['IPFV', 'NFUT', 'FUT', 'PST',
                  '1SG', '2SG', '3SG',
                  '1PL(EXCL)', '1PL(INCL)', '2PL', '3PL',
                  'QA',
                  'INF',
                  'INCEP',
                  'HABPROB',
                  'COND',
                  'INCH',
                  'DUR'
                  ]

GLOSSES_VERBAL_PREFIXES = ['VBLZ', 'CV', 'P', 'IMPER']
GLOSSES_ADJ_PREFIXES = ['ADJ', 'ATR', 'EQT',
                        'сильный(о.проявлении.качества)']
GLOSSES_ADV_PREFIXES = ['ADVZ']
GLOSSES_NOUN_PREFIXES = ['NMLZ', 'DATLOC', 'LOCALL', 'ACC', 'ACCIN', 'ABL', 'ALL',
                         'INSTR','COM','VOC','COM.FAM','LOCDIR', 'ELAT',
                         'COLL', 'FAM',
                         'INDPS',
                         'DEADREL'
                         ]

GLOSSES_PROPER_PREFIXES = ['HYDR.NAME']

def get_russian_pos_set(russian_word):
    return set([p.tag.POS for p in morph.parse(russian_word)])

def is_proper_noun_translation(translation):
    return translation[0].isupper()

def is_adjective_translation(possible_pos_set):
    return 'ADJF' in possible_pos_set or \
            'PRTF' in possible_pos_set

def is_numeric_translation(translation):
    return translation in RUSSIAN_NUMS

def is_pronoun_translation(translation):
    return translation in RUSSIAN_PRONOUNS

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
    return has_prefix(gloss, GLOSSES_VERBAL)


def is_adjective_gloss(gloss):
    return has_prefix(gloss, GLOSSES_ADJ_PREFIXES)


def is_adverb_gloss(gloss):
    return has_prefix(gloss, GLOSSES_ADV_PREFIXES)


def is_noun_gloss(gloss):
    return has_prefix(gloss, GLOSSES_NOUN_PREFIXES)


def is_proper_noun_gloss(gloss):
    return has_prefix(gloss, GLOSSES_PROPER_PREFIXES)


def has_prefix(gloss, PREFIX_LIST):
    for gloss_prefix in PREFIX_LIST:
        if gloss.startswith(gloss_prefix):
            return True
    return False


def main():
    print(get_russian_pos_set('отсутствующий'))


if __name__ == '__main__':
    main()
