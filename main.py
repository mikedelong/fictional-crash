import datetime
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
    return arg.startswith('fl') and arg[2:].isnumeric() and int(arg[2:]) < 400


if __name__ == '__main__':
    time_start = time()
    logger = getLogger(__name__, )
    basicConfig(format='%(asctime)s : %(name)s : %(levelname)s : %(message)s', level=INFO, )
    spell_checker = SpellChecker(case_sensitive=True, distance=2, language='en', tokenizer=None, )

    # Durzana ?
    spell_checker.word_frequency.load_text_file(filename='./words.json', encoding='utf-8', tokenizer=None, )

    # todo add data after June 2009
    url = 'https://raw.githubusercontent.com/arif-zaman/airplane-crash/master/Airplane_Crashes_Since_1908.csv'
    df = read_csv(filepath_or_buffer=url, parse_dates=['Date'])
    df['day'] = df.apply(lambda x: '{}-{}'.format(x['Date'].date().month, x['Date'].date().day, ), axis=1, )

    today = '{}-{}'.format(datetime.date.today().month, datetime.date.today().day, )
    select_df = df[df.day == today]
    logger.info('crashes on this day in history: {}'.format(len(select_df)))
    # todo report the data sensibly
    # todo report fatalities
    # todo move fix data from code to data
    fixes = {
        '  ': ' ',
        ',,': ',',
        'Destoryed': 'Destroyed',
        'classisymptoms': 'classic symptoms',
        'approah': 'approach',
        'Slamed': 'Slammed',
        'condtions': 'conditions',
        'geographiand': 'geography and',
        'AtlantiOcean': 'Atlantic Ocean',
        'forcasted': 'forecasted',
        'publistatements': 'public statements',
        'tragicrash': 'tragic crash',
        'liftoff': 'lift-off',
        'obsticales': 'obstacles',
        'enroute': 'en route',
        'attemping': 'attempting',
        'Nyarigongo': 'Nyiragongo',
        'DemocratiRepubliCongo': 'Democratic Republic of the Congo',
        'Taroma': 'Tahoma',
        'Military - ': '',
        '  - Taxi': '',
    }
    for index, row in select_df.iterrows():
        current_year = row['Date'].date().year
        current_summary = row['Summary']
        if type(current_summary) == float:
            current_summary = ''
        current_summary = current_summary.strip()
        for key, value in fixes.items():
            current_summary = current_summary.replace(key, value, )
        tokens = current_summary.split()
        tokens = [token[:-1] if any([token.endswith(p) for p in {':', ',', '.'}]) else token for token in tokens]
        tokens = [token.replace('’', '\'') for token in tokens]
        misspelled = spell_checker.unknown(tokens, )
        exceptions = {'aircraft\'s', 'pilot\'s', }
        if len(misspelled) > 0:
            for word in misspelled:
                if not any([word.replace(',', '').isnumeric(), valid_date(word), is_flight_level(word),
                            word in exceptions, ], ):
                    logger.warning('misspelled: {}'.format(word))

        aboard = int(row['Aboard'])
        flight = row['Flight #']
        location = row['Location']
        location = location.replace('DemocratiRepubliCongo', 'Democratic Republic of the Congo', )
        operator = row['Operator']
        operator = operator.replace('Taroma', 'Tahoma', )
        operator = operator.replace('Military - ', '', )
        operator = operator.replace('  - Taxi', '')
        # todo consolidate this into a simpler structure; either we have a flight number or we don't
        if type(flight) == str and flight != '-':
            if len(current_summary) == 0:
                logger.info('In {} {} flight {} crashed at/near {} with {} aboard.'.format(current_year, operator,
                                                                                           flight, location, aboard, ))
            else:
                logger.info(
                    'In {} {} flight {} crashed at/near {} with {} aboard: {}'.format(current_year, operator, flight,
                                                                                      location, aboard,
                                                                                      current_summary, ))
        elif flight == '-' or isnan(float(flight, ), ):
            if len(current_summary) == 0:
                logger.info(
                    'In {} a {} flight crashed at/near {} with {} aboard.'.format(current_year, operator, location,
                                                                                  aboard, ))
            else:
                logger.info(
                    'In {} a {} flight crashed at/near {} with {} aboard: {}'.format(current_year, operator, location,
                                                                                     aboard, current_summary, ))
        else:
            if len(current_summary) == 0:
                logger.info('In {} {} flight {} crashed at/near {} with {} aboard.'.format(current_year, operator,
                                                                                           flight, location, aboard, ))
            else:
                logger.info(
                    'In {} {} flight {} crashed at/near {} with {} aboard: {}'.format(current_year, operator, flight,
                                                                                      location, aboard, current_summary,
                                                                                      ))

    logger.info('total time: {:5.2f}s'.format(time() - time_start))
