#!/usr/bin/python
# -*- coding: utf-8 -*
__author__ = "gisly"

import re
from Levenshtein import distance
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
                   'сколько', 'тоже', 'потом', 'так',
                   'как', 'только', 'век', 'даже', 'может',
                   'вроде', 'зато', 'эвенк']

RUSSIAN_CCONJ = ['и', 'или']

RUSSIAN_SCONJ = ['чтоб', 'чтобы', 'если', 'когда', 'пока']

RUSSIAN_INTERJECTIONS = ['INTJ', 'FOC', 'HORT', 'PROB.ANGI', 'EMPH',
                         'ONOM',
                         'вот', 'ах', 'ай', 'ой', 'ну', 'а', 'ага',
                         'бах.бах']
RUSSIAN_LOANWORDS = ['школа', 'больница', 'документ', 'метрика', 'артист',
                     'вертолет', 'вертолёт', 'интернат', 'колхоз', 'доктор', 'бригадир',
                     'самолет', 'палатка', 'война',
                     'шаман', 'президент', 'январь', 'февраль', 'март',
                     'контора', 'пастух', 'буран', 'эпидемия', 'город',
                     'груз', 'институт', 'комендант', 'километр',
                     'крест', 'комната', 'метр', 'механик',
                     'правительство', 'профессор', 'промхоз',
                     'совхоз', 'суглан', 'техникум', 'терапевт',
                     'ветеран', 'враг', 'зоотехник', 'норма',
                     'инвалид', 'интересный',
                     'казах', 'музей', 'метеорит', 'оперный', 'пенсионер',
                     'план', 'порох', 'проводник', 'сахар',
                     'сельхозтехникум']

GLOSSES_VERBAL = ['COMIT',
                  'IPFV', 'NFUT', 'FUT', 'FUTCNT',
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
GLOSSES_ADV_PREFIXES = ['ADVZ', ]
GLOSSES_NOUN_PREFIXES = ['NMLZ', 'DATLOC', 'LOCALL', 'ACC', 'ACCIN', 'ABL', 'ALL',
                         'INSTR', 'COM', 'VOC', 'COM.FAM', 'LOCDIR', 'ELAT',
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
    BAD_CHARACTERS: '',
    REGEX_ADDITIONAL_INFO: (lambda x: x.group(1)),
    REGEX_NOT_LAST_CHARACTER: (lambda x: x.group(1)),
    'ɒ': 'o',
    'ɔ': 'o',
    'ε': 'e',
    'č': 't͡ʃ',
    'd\'': 'ď',
    'd’': 'd',
    '\u01EF': 'ď',
    't\'': 'ť',
    't’': 'ť',
    'ń': 'ɲ',
    'n\u0301': 'ɲ',
    'n\'': 'ɲ',
    'n’': 'ɲ',
    'l’': 'l',
    'ĺ': 'l',
    'ľ': 'l',
    'ŕ': 'r',
    's’': 'ś',
    's\'': 'ś',
    'š': 'ʃ',
    'ž': 'ʒ',
    'ɣ': 'γ',
    'χ': 'x',
    'ʍ': 'f',
    '{*}': '',
    '\/.+': '',
    '[:̄̅]': 'ː',

    'ā': 'aː',
    'ă': 'a',
    'ē': 'eː',
    'í': 'iː',
    'ī': 'iː',
    'ō': 'oː',
    'ū': 'uː',
    'y': 'i',
    'ɨ': 'i',
    'ǝ': 'ə',
    'ɵ': 'ə',
    'ә': 'ə',
    'ch' : 't͡ʃ',


}

FON_REPLACEMENTS_STAGE_2 = {
    "'": '',
    '’': '',
    "\u0301": '',
    "[\[\]]": '',
    'c': 'ts',
}
DERIVATIVE_GLOSSES = ['APPROX', 'ATTEN',
                      'DIM',
                      'CHILD', 'COVER', 'DAY', 'DEADREL', 'DER', 'DEST.FAG',
                      'EQT', 'EVERY', 'FAG', 'FAKE', 'GEOGR', 'INDEF',
                      'ONOM', 'PEJOR', 'PELT', 'PEOPLE',
                      'PREDEST', 'PRGRN', 'QUANT', 'REDIS', 'RESID',
                      'ROOM', 'RYTHM', 'SIDE',
                      'NUM.TEN'
                      ]
DERIVATIVE_GLOSS_PREFIXES = ['ADVZ', 'ADBLZ', 'ADJ', 'ATR', 'ADVR', 'AUG', 'INTER', 'NDEF',
                             'NMLZ', 'NMNLZ', 'VBLZ', 'VERB']

PRONOUN_GLOSSES = ['1SG', '1PL(EXCL)', '1PL(INCL)', '2SG', '2PL', '3SG', '3PL', 'RFL']

RUSSIAN_SPECIAL_VERBS = ['надо']
RUSSIAN_GLOSS_ADJECTIVES = ['сильный(о.проявлении.качества)', 'сильный(о.проявлении.признака)']

GLOSSES_TO_REPLACE = {'1PL.EXCL' : '1PL(EXCL)'}


EVENKI_FON = "abdefghijklmnoprstuvwxzɲə"
RUS_FON = "абдефгхийклмнопрстуввхзне"
EVENKI_RUS_TAB = str.maketrans(EVENKI_FON, RUS_FON)



def get_russian_pos_set(russian_word):
    """

    :param russian_word:
    :return: a set of possible parts of speech for a russian word
    """
    return set([p.tag.POS for p in morph.parse(russian_word)])


def is_proper_noun_translation(translation):
    """

    :param translation:
    :return: True iff the translation can be treated as a proper noun
    """
    return (translation != 'NEG' and translation[0].isupper()) or \
           (translation.startswith('река.'))


def is_interjection_translation(translation):
    return translation in RUSSIAN_INTERJECTIONS


def is_adjective_translation(possible_pos_set, normalized_glosses):
    #it can be an adverb derived from an adjective
    for gloss in normalized_glosses:
        if is_adverb_gloss(gloss):
            return False

    return normalized_glosses[0] in RUSSIAN_GLOSS_ADJECTIVES or \
            'ADJF' in possible_pos_set or \
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


def is_determiner_translation(translation, normalized_glosses):
    if translation in RUSSIAN_DETERMINERS:
        return True
    return translation in RUSSIAN_PRONOUNS \
           and len(normalized_glosses) > 1 \
           and normalized_glosses[1] == 'PROPR'


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

def is_special_verbal_form(first_gloss):
    return first_gloss in RUSSIAN_SPECIAL_VERBS


def is_slip_unknown(gloss):
    return contains(gloss.strip('<').strip('['), GLOSSES_SLIP)

def is_personal_pronoun(gloss):
    return has_prefix(gloss, PRONOUN_GLOSSES)

def is_special_noun_stem(gloss):
    return gloss.endswith('.PL')\
            or gloss.endswith('.PLSTEM')


def has_prefix(gloss, PREFIX_LIST):
    for gloss_prefix in PREFIX_LIST:
        if gloss.startswith(gloss_prefix):
            return True
    return False

def contains(gloss, PART_LIST):
    for gloss_part in PART_LIST:
        if gloss_part in gloss:
            return True
    return False



def is_cyrillic(token):
    return re.findall(r'[ЁёА-Яа-я]', token) != []


def is_cyrillic_only(token):
    return re.match(r'[ЁёА-Яа-я\(\)\.\[\],/\s]+$', token) is not None


def normalize_gloss(gloss):
    """

    :param gloss:
    :return: gloss with bad characters stripped off,
    and replaced with their unified representation
    """
    gloss = gloss.strip('[]')
    gloss = re.sub('\.RUS$', '', gloss)
    if is_cyrillic_only(gloss):
        return gloss

    gloss = gloss.upper()
    gloss = gloss.replace('[SLIP]', '.SLIP')
    gloss = re.sub('\(([ЁёА-Яа-я]+).+?\)', '', gloss)
    gloss = re.sub('\[([ЁёА-Яа-я]+).+?\]', '', gloss)
    gloss = re.sub('[\[\]\-=\\\]', '', gloss)
    gloss = re.sub('{(\*)+}', '', gloss)
    gloss = gloss.split("/")[0]



    if gloss in GLOSSES_TO_REPLACE:
        return GLOSSES_TO_REPLACE[gloss]
    return gloss


def normalize_tokens(morph_data_token):
    starting_index = 0
    tokens = []
    current_multiword = ''
    current_token = ''
    current_glosses = []
    current_morphemes = []
    for i in range(len(morph_data_token['analysis'])):
        normalized_fon = normalize_token(morph_data_token['analysis'][i]['fon'])
        normalized_gloss = normalize_gloss(morph_data_token['analysis'][i]['gloss'])
        if normalized_gloss == 'FOC' and current_token != '':
            current_multiword = current_token
            tokens.append({'normalized_token' : current_token,
                           'normalized_glosses' : current_glosses,
                           'normalized_morphemes' : current_morphemes,
                           'starting_index' : starting_index})
            current_token = normalized_fon
            current_glosses = [normalized_gloss]
            current_morphemes = [normalized_fon]
            starting_index = i
        else:
            current_token += normalized_fon
            current_glosses.append(normalized_gloss)
            current_morphemes.append(normalized_fon)

        if current_multiword != '':
            current_multiword += normalized_fon
    if current_token != '':
        tokens.append({'normalized_token': current_token,
                       'normalized_glosses': current_glosses,
                       'normalized_morphemes' : current_morphemes,
                       'starting_index': starting_index})
    return current_multiword, tokens

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

def is_code_switching(normalized_token, glosses):
    if len(glosses) > 1:
        return False
    if glosses[0].lower() in RUSSIAN_LOANWORDS:
        return False
    return is_similar(normalized_token, glosses[0])

def is_similar(fon, gloss):
    """
    returns True if fon is the transciption of the word specified by gloss
    :param fon:
    :param gloss:
    """
    return distance(transliterate(fon), gloss) < (len(fon) / 2)


def transliterate(fon):
    return fon.translate(EVENKI_RUS_TAB)

def main():
    print(normalize_gloss("[вырасти.родиться]"))


if __name__ == '__main__':
    main()
