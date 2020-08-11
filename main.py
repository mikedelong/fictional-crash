from logging import INFO
from logging import basicConfig
from logging import getLogger
from time import time

from pandas import read_csv

if __name__ == '__main__':
    time_start = time()
    logger = getLogger(__name__, )
    basicConfig(format='%(asctime)s : %(name)s : %(levelname)s : %(message)s', level=INFO, )

    url = 'https://raw.githubusercontent.com/arif-zaman/airplane-crash/master/Airplane_Crashes_Since_1908.csv'
    df = read_csv(filepath_or_buffer=url)
    logger.info(df.shape)

    logger.info('total time: {:5.2f}s'.format(time() - time_start))
