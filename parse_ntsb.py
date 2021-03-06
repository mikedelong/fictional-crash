import datetime
from logging import INFO
from logging import basicConfig
from logging import getLogger
from time import time

from certifi import where
from pandas import DataFrame
from urllib3 import PoolManager
from xmltodict import parse


def get_day(arg):
    pieces = arg.split('/')
    return '{}-{}'.format(int(pieces[0], ), int(pieces[1], ), )


if __name__ == '__main__':
    time_start = time()
    logger = getLogger(__name__, )
    basicConfig(format='%(asctime)s : %(name)s : %(levelname)s : %(message)s', level=INFO, )

    xml_url = 'https://app.ntsb.gov/aviationquery/Download.ashx?type=xml'

    http = PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=where(), )
    response = http.request('GET', xml_url, )
    data = parse(response.data, )
    logger.info('got NTSB XML')
    df = DataFrame(data['DATA']['ROWS']['ROW'])
    df = df.rename(axis='columns', mapper={key: key[1:] for key in data['DATA']['ROWS']['ROW'][0]}, )
    logger.info('{}'.format(len(df, ), ), )
    df['day'] = df['EventDate'].apply(get_day, )
    for column in ['NumberOfEngines', 'TotalFatalInjuries', 'TotalSeriousInjuries', 'TotalMinorInjuries',
                   'TotalUninjured']:
        df[column] = df[column].apply(lambda x: 0 if x == '' else int(x))
    df['year'] = df['EventDate'].apply(lambda x: int(x[-4:]))

    df['Fatal'] = df['InjurySeverity'].apply(lambda x: 'Yes' if x.startswith('Fatal') else 'No')
    today = '{}-{}'.format(datetime.date.today().month, datetime.date.today().day, )
    logger.info('\n{}'.format(df.dtypes, ), )
    select_df = df[df['day'] == today]
    logger.info('there were {} events on this date in history'.format(len(select_df), ), )
    logger.info('of these {} had fatal injuries'.format(len(select_df[select_df['Fatal'] == 'Yes']), ), )

    fatal_df = select_df[select_df['Fatal'] == 'Yes']
    logger.info('these range from {} to {}'.format(fatal_df['year'].min(), fatal_df['year'].max(), ), )

    logger.info('total time: {:5.2f}s'.format(time() - time_start, ), )
