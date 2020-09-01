import datetime
from json import load
from logging import INFO
from logging import basicConfig
from logging import getLogger
from math import isnan
from time import time

from dateutil.parser import parse
from pandas import read_csv
from spellchecker import SpellChecker


def valid_date(arg):
    try:
        parse(arg)
        return True
    except ValueError:
        return False


def is_flight_level(arg):
    return arg.startswith('fl') and arg[2:].isnumeric() and int(arg[2:]) <= 450


if __name__ == '__main__':
    time_start = time()
    logger = getLogger(__name__, )
    basicConfig(format='%(asctime)s : %(name)s : %(levelname)s : %(message)s', level=INFO, )
    spell_checker = SpellChecker(case_sensitive=True, distance=2, language='en', tokenizer=None, )

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
        aboard = int(row['Aboard'])
        current_year = row['Date'].date().year
        current_summary = row['Summary']
        if type(current_summary) == float:
            current_summary = ''
        current_summary = current_summary.strip()
        fatalities = row['Fatalities']
        flight = row['Flight #']
        ground = row['Ground']
        location = row['Location'].strip() if type(row['Location']) == str else ''
        operator = row['Operator'].strip()
        for key, value in FIXES.items():
            current_summary = current_summary.replace(key, value, )
            location = location.replace(key, value, )
            operator = operator.replace(key, value, )
        current_summary_lower = current_summary.lower()
        for key, value in {'’': ' ', '\'': ' ', '-': ' ', '/': ' ', '..': '.'}.items():
            current_summary_lower = current_summary_lower.replace(key, value)
        # todo think about using the nltk word tokenizer here to simplify this code
        tokens = current_summary_lower.split()
        tokens = [token[:-1] if any([token.endswith(p) for p in {':', ',', '.', ')'}]) else token for token in tokens]
        tokens = [token[1:] if any([token.startswith(p) for p in {'(', }]) else token for token in tokens]
        misspelled = spell_checker.unknown(tokens, )
        if len(misspelled) > 0:
            for word in misspelled:
                if not any([word.replace(',', '').isnumeric(), valid_date(word), is_flight_level(word), ], ):
                    logger.warning('misspelled: {}'.format(word))

        output = 'In {} '.format(current_year, )
        if type(flight) == str and flight != '-':
            output += '{} flight {} crashed '.format(operator, flight, )
        elif flight == '-' or isnan(float(flight, ), ):
            output += 'a {} flight crashed '.format(operator, ) if operator.startswith('U.S.') or not any(
                [operator.startswith(c) for c in {'A', 'E', 'I', 'O', 'U'}]) else 'an {} flight crashed '.format(
                operator, )
        else:
            output += '{} flight {} crashed '.format(operator, flight, )
        output += 'near {} '.format(location, ) if location != '' else 'at an unknown location '
        output += 'with {} aboard. '.format(aboard, )
        if fatalities > 0:
            output += 'There were {} passenger/crew fatalities. '.format(int(fatalities))
        else:
            output += 'There were no passenger/crew fatalities. '
        if ground > 0:
            output += 'There were {} ground fatalities. '.format(int(fatalities))
        if len(current_summary) > 0:
            output += current_summary

        logger.info('{}: {}'.format(len(output), output))

    logger.info('total time: {:5.2f}s'.format(time() - time_start))
