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


# todo move fix data from code to data
FIXES = {
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
    'Monseny': 'Montseny',
    'Agusta': 'Augusta',
    'Rilyadh': 'Riyadh',
    'tarmaby': 'tarmac by',
    'hydraulicontrol': 'hydraulic control'
}

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
    for index, row in select_df.iterrows():
        aboard = int(row['Aboard'])
        current_year = row['Date'].date().year
        current_summary = row['Summary']
        if type(current_summary) == float:
            current_summary = ''
        current_summary = current_summary.strip()
        fatalities = row['Fatalities']
        flight = row['Flight #']
        location = row['Location'].strip()
        operator = row['Operator'].strip()
        for key, value in FIXES.items():
            current_summary = current_summary.replace(key, value, )
            location = location.replace(key, value, )
            operator = operator.replace(key, value, )
        tokens = current_summary.split()
        tokens = [token[:-1] if any([token.endswith(p) for p in {':', ',', '.'}]) else token for token in tokens]
        tokens = [token.replace('’', '\'') for token in tokens]
        misspelled = spell_checker.unknown(tokens, )
        exceptions = {'aircraft\'s', 'helicopter\'s', 'pilot\'s', 'shoulder-launched', }
        if len(misspelled) > 0:
            for word in misspelled:
                if not any([word.replace(',', '').isnumeric(), valid_date(word), is_flight_level(word),
                            word in exceptions, ], ):
                    logger.warning('misspelled: {}'.format(word))

        output = 'In {} '.format(current_year, )
        if type(flight) == str and flight != '-':
            output += '{} flight {} crashed at/near '.format(operator, flight, )
        elif flight == '-' or isnan(float(flight, ), ):
            output += 'a {} flight crashed at/near '.format(operator, )
        else:
            output += '{} flight {} crashed at/near '.format(operator, flight, )
        output += '{} with {} aboard. '.format(location, aboard, )
        if fatalities > 0:
            output += 'There were {} fatalities. '.format(int(fatalities))
        else:
            output += 'There were no fatalities.'
        if len(current_summary) > 0:
            output += current_summary

        logger.info(output)

    logger.info('total time: {:5.2f}s'.format(time() - time_start))
