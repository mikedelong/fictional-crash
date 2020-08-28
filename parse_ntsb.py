from logging import INFO
from logging import basicConfig
from logging import getLogger
from time import time

import urllib3
from certifi import where
from pandas import DataFrame
from xmltodict import parse

if __name__ == '__main__':
    time_start = time()
    logger = getLogger(__name__, )
    basicConfig(format='%(asctime)s : %(name)s : %(levelname)s : %(message)s', level=INFO, )

    xml_url = 'https://app.ntsb.gov/aviationquery/Download.ashx?type=xml'

    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=where(), )
    response = http.request('GET', xml_url, )
    data = parse(response.data)
    logger.info('got NTSB XML')

    df = DataFrame(data['DATA']['ROWS']['ROW'])
    df = df.rename(axis='columns', mapper={key: key[1:] for key in data['DATA']['ROWS']['ROW'][0]}, )
    logger.info('{}'.format(len(df)))
    logger.info(list(df))

    logger.info('total time: {:5.2f}s'.format(time() - time_start))
