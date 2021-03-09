import datetime
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
    return arg.endswith('km') and arg[:-2].replace('.', '', 1, ).isnumeric()


def is_elevation(arg):
    return (arg.endswith('ft') and arg[:-2].replace(',', '').isnumeric()) or (
            arg.endswith('m') and arg[:-1].replace(',', '').isnumeric())


def is_flight_level(arg):
    return arg.startswith('fl') and arg[2:].isnumeric() and int(arg[2:]) <= 450


def is_speed(arg):
    return arg.endswith('kts') and arg[:-3].replace('.', '', 1, ).isnumeric()


def valid_date(arg):
    try:
        parse(arg)
        return True
    except ValueError:
        return False


if __name__ == '__main__':
    time_start = time()
    logger = getLogger(__name__, )
    basicConfig(format='%(asctime)s : %(name)s : %(levelname)s : %(message)s', level=INFO, )
    spell_checker = SpellChecker(case_sensitive=True, distance=1, language='en', tokenizer=None, )

    with open(encoding='utf-8', file='./fixes.json', mode='r', ) as fixes_fp:
        FIXES = load(fp=fixes_fp, )

    # Bolomon ?
    # Durzana ?
    spell_checker.word_frequency.load_text_file(filename='./words.json', encoding='utf-8', tokenizer=None, )

    # todo add data after June 2009
    url = 'https://raw.githubusercontent.com/arif-zaman/airplane-crash/master/Airplane_Crashes_Since_1908.csv'
    df = read_csv(filepath_or_buffer=url, parse_dates=['Date'])
    df['day'] = df.apply(lambda x: '{}-{}'.format(x['Date'].date().month, x['Date'].date().day, ), axis=1, )

    xml_url = 'http://app.ntsb.gov/aviationquery/Download.ashx?type=xml'

    today = '{}-{}'.format(datetime.date.today().month, datetime.date.today().day, )
    logger.info('crashes on this day in history: {}'.format(df[df.day == today]['day'].count()))
    for index, row in df[df.day == today].iterrows():
        aboard = 'an unknown number' if isnan(row['Aboard']) else int(row['Aboard'])
        current_year = row['Date'].date().year
        current_summary = row['Summary']
        if type(current_summary) == float:
            current_summary = ''
        current_summary = ' '.join(current_summary.strip().split())
        fatalities = row['Fatalities']
        flight = row['Flight #']
        ground = row['Ground']
        location = row['Location'].strip() if type(row['Location']) == str else ''
        operator = row['Operator'].strip() if type(row['Operator']) == str else 'unknown operator'
        for key, value in FIXES.items():
            current_summary = current_summary.replace(key, value, )
            location = location.replace(key, value, )
            operator = operator.replace(key, value, )
        current_summary_lower = current_summary.lower()
        for key, value in {'’': ' ', '\'': ' ', '-': ' ', '/': ' ', '..': '.'}.items():
            current_summary_lower = current_summary_lower.replace(key, value)
        tokens = word_tokenize(text=current_summary_lower)
        misspelled = spell_checker.unknown(tokens, )
        if len(misspelled) > 0:
            for word in misspelled:
                if not any(
                        [is_distance(word), is_elevation(word), is_flight_level(word), is_speed(word), valid_date(word),
                         word.replace('nm', '').isnumeric(), word.replace('.', '').isnumeric(),
                         word.replace(',', '').isnumeric(), ], ):
                    logger.warning('misspelled: {}'.format(word, ), )

        output = 'In {} '.format(current_year, )
        if type(flight) == str and flight != '-':
            flight = flight.replace(' / -', '')
            output += '{} flight {} crashed '.format(operator, flight, )
        elif flight == '-' or isnan(float(flight, ), ):
            output += 'a {} flight crashed '.format(operator, ) if operator.startswith('U.S.') or not any(
                [operator.startswith(c) for c in {'A', 'E', 'I', 'O', 'U', 'u'}]) else 'an {} flight crashed '.format(
                operator, )
        else:
            output += '{} flight {} crashed '.format(operator, flight, )
        if location == '':
            output += 'at an unknown location '
        elif location.startswith('Between '):
            output += 'between {} '.format(location.replace('Between ', ''))
        elif location.startswith('Near '):
            output += 'near {} '.format(location.replace('Near ', ''))
        elif location.startswith('Off '):
            output += 'off {} '.format(location.replace('Off ', ''))
        elif location.startswith('Over '):
            output += 'over {} '.format(location.replace('Over ', ''))
        else:
            output += 'near {} '.format(location, )
        output += 'with {} aboard. '.format(aboard, )
        if isnan(fatalities):
            output += 'The number of passenger/crew fatalities is unknown. '
        elif fatalities > 1:
            output += 'There were {} passenger/crew fatalities. '.format(int(fatalities, ), )
        elif int(fatalities) == 1:
            output += 'There was 1 passenger/crew fatality. '
        if isnan(ground):
            output += 'The number of ground fatalities is unknown. '
        elif ground > 1:
            output += 'There were {} ground fatalities. '.format(int(ground, ), )
        elif int(ground) == 1:
            output += 'There was 1 ground fatality. '

        if len(current_summary) > 0:
            output += current_summary

        output = ' '.join(output.split())

        logger.info('{}: {}'.format(len(output, ), output, ))

    logger.info('total time: {:5.2f}s'.format(time() - time_start))
