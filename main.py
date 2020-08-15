import datetime
from logging import INFO
from logging import basicConfig
from logging import getLogger
from math import isnan
from time import time

from pandas import read_csv
from spellchecker import SpellChecker

if __name__ == '__main__':
    time_start = time()
    logger = getLogger(__name__, )
    basicConfig(format='%(asctime)s : %(name)s : %(levelname)s : %(message)s', level=INFO, )
    spell_checker = SpellChecker(case_sensitive=False, distance=2, language='en', tokenizer=None, )
    words = ['yawed', 'spiraling', 'non-instrument', 'Hattiesburg', 'Gulfport', 'preflight', 'flightcrew\'s',
             'captain\'s', 'crossfeed', '36r', 'airplane\'s', 'Gilmer', 'overspeeding', 'maneuver', 'two-engine',
             'peening', 'FL340', 'Prodromos', 'terrorist-proof', 'pilot/flight', 'pilot\'s', 'Durzana', '#3',
             'through-bolts', 'studs/engine', 'Huila', 'Nevado', 'Glendo', 'nose-heaviness', 'Guanabara', 'FL230',
             'minimums', ]
    # Durzana ?
    spell_checker.word_frequency.load_words(words=words)

    # todo add data after June 2009
    url = 'https://raw.githubusercontent.com/arif-zaman/airplane-crash/master/Airplane_Crashes_Since_1908.csv'
    df = read_csv(filepath_or_buffer=url, parse_dates=['Date'])
    df['day'] = df.apply(lambda x: '{}-{}'.format(x['Date'].date().month, x['Date'].date().day, ), axis=1, )

    today = '{}-{}'.format(datetime.date.today().month, datetime.date.today().day, )
    select_df = df[df.day == today]
    logger.info('crashes on this day in history: {}'.format(len(select_df)))
    # todo report the data sensibly
    # todo report fatalities
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
        tokens = [token[:-1] if any([token.endswith(p) for p in {':', ',', '.'}]) else token for
                  token in tokens]
        misspelled = spell_checker.unknown(tokens, )
        if len(misspelled) > 0:
            for word in misspelled:
                if not word.replace(',', '').isnumeric():
                    logger.warning('misspelled: {}'.format(word))
        aboard = int(row['Aboard'])
        flight = row['Flight #']
        location = row['Location']
        operator = row['Operator']
        operator = operator.replace('Taroma', 'Tahoma', )
        operator = operator.replace('Military - ', '', )
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
