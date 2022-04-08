"""
Parse and summarize plane crashes for this day through 2009
"""
import datetime
from json import dump
from json import load
from logging import INFO
from logging import basicConfig
from logging import getLogger
from math import isnan
from time import time

from dateutil.parser import parse
from nltk import word_tokenize
from pandas import read_csv
from spellchecker import SpellChecker


def is_distance(arg):
    """
    parse token as a distance in kilometers
    :param arg: input string
    :return: True or False
    """
    return arg.endswith('km') and arg[:-2].replace('.', '', 1, ).isnumeric()


def is_elevation(arg):
    """
    parse a token as an elevation in feet or meters
    :param arg: input string
    :return: True or False
    """
    return (arg.endswith('ft') and arg[:-2].replace(',', '').isnumeric()) or (
            arg.endswith('m') and arg[:-1].replace(',', '').isnumeric())


def is_flight_level(arg):
    """
    Parse token as a flight level
    :param arg: input string
    :return: True or False
    """
    return arg.startswith('fl') and arg[2:].isnumeric() and int(arg[2:]) <= 450


def is_speed(arg):
    """
    Special case code for tokens that may be speeds in knots (kts)
    :param arg: input string
    :return: True or False
    """
    return arg.endswith('kts') and arg[:-3].replace('.', '', 1, ).isnumeric()


def is_valid_date(arg):
    """
    Is this string a valid date?
    :param arg: input string
    :return: True or False
    """
    try:
        parse(arg)
        return True
    except ValueError:
        return False


if __name__ == '__main__':
    TIME_START = time()
    LOGGER = getLogger(__name__, )
    basicConfig(format='%(asctime)s : %(name)s : %(levelname)s : %(message)s', level=INFO, )

    with open(encoding='utf-8', file='./fixes.json', mode='r', ) as fixes_fp:
        fixes = load(fp=fixes_fp, )

    LOGGER.info('read fixes')
    with open(encoding='utf-8', file='./fixes.json', mode='w', ) as fixes_fp:
        dump(allow_nan=False, check_circular=False, ensure_ascii=False, fp=fixes_fp,
             indent=True, obj=fixes, sort_keys=True, )
    LOGGER.info('wrote sorted fixes')
    del fixes_fp

    with open(encoding='utf-8', file='./words.json', mode='r', ) as words_fp:
        words = load(fp=words_fp, )
    words = sorted(words)
    with open(encoding='utf-8', file='./words.json', mode='w', ) as words_fp:
        dump(ensure_ascii=False, fp=words_fp, indent=True, obj=words, )
    LOGGER.info('wrote sorted words')
    del words_fp

    SPELL_CHECKER = SpellChecker(case_sensitive=True, distance=1, language='en', tokenizer=None, )

    with open(encoding='utf-8', file='./fixes.json', mode='r', ) as fixes_fp:
        FIXES = load(fp=fixes_fp, )

    SPELL_CHECKER.word_frequency.load_text_file(
        encoding='utf-8', filename='./words.json', tokenizer=None, )

    # todo add data after June 2009
    CSV_URL = 'https://raw.githubusercontent.com/arif-zaman/airplane-crash/master/' \
              'Airplane_Crashes_Since_1908.csv'
    DATA = read_csv(filepath_or_buffer=CSV_URL, parse_dates=['Date'])
    DATA['day'] = DATA.apply(
        axis=1,
        func=lambda x: '{}-{}'.format(x['Date'].date().month, x['Date'].date().day, ),
    )

    XML_URL = 'http://app.ntsb.gov/aviationquery/Download.ashx?type=xml'

    base_date = datetime.date.today()
    offset = datetime.timedelta(days=0) # was 301
    reference_date = base_date + offset
    LOGGER.info('reference date is %s', reference_date)
    TODAY = '{}-{}'.format(reference_date.month, reference_date.day, )
    LOGGER.info('crashes on this day in history: %d', DATA[DATA.day == TODAY]['day'].count())
    data_today = DATA[DATA.day == TODAY]
    for index, row in DATA[DATA.day == TODAY].iterrows():
        aboard = 'an unknown number' if isnan(row['Aboard']) else int(row['Aboard'])
        current_year = row['Date'].date().year
        CURRENT_SUMMARY = row['Summary']
        CURRENT_SUMMARY = '' if isinstance(CURRENT_SUMMARY, float) else \
            ' '.join(CURRENT_SUMMARY.strip().split())
        fatalities = row['Fatalities']
        flight = row['Flight #']
        ground = row['Ground']
        location = row['Location'].strip() if isinstance(row['Location'], str) else ''
        operator = row['Operator'].strip() if isinstance(row['Operator'], str) else \
            'unknown operator'
        LOGGER.debug(operator)
        for key, value in FIXES.items():
            CURRENT_SUMMARY = CURRENT_SUMMARY.replace(key, value, )
            location = location.replace(key, value, )
            operator = operator.replace(key, value, )

        CURRENT_SUMMARY_LOWER = CURRENT_SUMMARY.lower()
        for key, value in {'’': ' ', '\'': ' ', '-': ' ', '/': ' ', '..': '.'}.items():
            CURRENT_SUMMARY_LOWER = CURRENT_SUMMARY_LOWER.replace(key, value)
        tokens = word_tokenize(text=CURRENT_SUMMARY_LOWER)
        misspelled = SPELL_CHECKER.unknown(tokens, )
        if misspelled:
            for word in misspelled:
                if not any(
                        [is_distance(word), is_elevation(word), is_flight_level(word),
                         is_speed(word), is_valid_date(word), word.replace('nm', '').isnumeric(),
                         word.replace('.', '').isnumeric(), word.replace(',', '').isnumeric(), ],
                ):
                    LOGGER.warning('misspelled: %s', word)

        OUTPUT = 'In {} '.format(current_year, )
        if isinstance(flight, str) and flight != '-':
            flight = flight.replace(' / -', '')
            OUTPUT += '{} flight {} crashed '.format(operator, flight, )
        elif flight == '-' or isnan(float(flight, ), ):
            OUTPUT += 'a {} flight crashed '.format(operator, ) if \
                operator.startswith('U.S.') or operator.startswith('US') or not any(
                    operator.startswith(c) for c in {'A', 'E', 'I', 'O', 'U', 'u'}) \
                else 'an {} flight crashed '.format(operator, )
        else:
            OUTPUT += '{} flight {} crashed '.format(operator, flight, )
        if location == '':
            OUTPUT += 'at an unknown location '
        elif location.startswith('Between '):
            OUTPUT += 'between {} '.format(location.replace('Between ', ''))
        elif location.startswith('Near '):
            OUTPUT += 'near {} '.format(location.replace('Near ', ''))
        elif location.startswith('Off '):
            OUTPUT += 'off {} '.format(location.replace('Off ', ''))
        elif location.startswith('Over '):
            OUTPUT += 'over {} '.format(location.replace('Over ', ''))
        else:
            OUTPUT += 'near {} '.format(location, )
        OUTPUT += 'with {} aboard. '.format(aboard, )
        if isnan(fatalities):
            OUTPUT += 'The number of passenger/crew fatalities is unknown. '
        elif fatalities > 1:
            OUTPUT += 'There were {} passenger/crew fatalities. '.format(int(fatalities, ), )
        elif int(fatalities) == 1:
            OUTPUT += 'There was 1 passenger/crew fatality. '
        if isnan(ground):
            OUTPUT += 'The number of ground fatalities is unknown. '
        elif ground > 1:
            OUTPUT += 'There were {} ground fatalities. '.format(int(ground, ), )
        elif int(ground) == 1:
            OUTPUT += 'There was 1 ground fatality. '

        if CURRENT_SUMMARY:
            OUTPUT += CURRENT_SUMMARY

        OUTPUT = ' '.join(OUTPUT.split())

        LOGGER.info('%d: %s', len(OUTPUT, ), OUTPUT, )

    LOGGER.info('total time: {:5.2f}s'.format(time() - TIME_START))
