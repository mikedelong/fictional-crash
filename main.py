import datetime
from logging import INFO
from logging import basicConfig
from logging import getLogger
from math import isnan
from time import time

from pandas import read_csv

if __name__ == '__main__':
    time_start = time()
    logger = getLogger(__name__, )
    basicConfig(format='%(asctime)s : %(name)s : %(levelname)s : %(message)s', level=INFO, )

    # todo add data after June 2009
    url = 'https://raw.githubusercontent.com/arif-zaman/airplane-crash/master/Airplane_Crashes_Since_1908.csv'
    df = read_csv(filepath_or_buffer=url, parse_dates=['Date'])
    df['day'] = df.apply(lambda x: '{}-{}'.format(x['Date'].date().month, x['Date'].date().day, ), axis=1, )

    today = '{}-{}'.format(datetime.date.today().month, datetime.date.today().day, )
    logger.info(today)
    select_df = df[df.day == today]
    logger.info('crashes on this day in history: {}'.format(len(select_df)))
    # todo report the data sensibly
    for index, row in select_df.iterrows():
        current_year = row['Date'].date().year
        current_summary = row['Summary']
        if type(current_summary) == float:
            current_summary = ''
        flight = row['Flight #']
        if flight == '-' or isnan(float(flight, ), ):
            logger.info('{}: {} {}'.format(current_year, row['Location'], current_summary, ))
        else:
            logger.info('{}: {} {}'.format(current_year, row['Location'], current_summary, ))

    logger.info('total time: {:5.2f}s'.format(time() - time_start))
