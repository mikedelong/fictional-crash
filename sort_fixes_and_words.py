from json import dump
from json import load
from logging import INFO
from logging import basicConfig
from logging import getLogger
from time import time

if __name__ == '__main__':
    time_start = time()
    logger = getLogger(__name__, )
    basicConfig(format='%(asctime)s : %(name)s : %(levelname)s : %(message)s', level=INFO, )
    logger.info('started')

    with open(encoding='utf-8', file='./fixes.json', mode='r', ) as fixes_fp:
        fixes = load(fp=fixes_fp, )

    logger.info('read fixes')
    with open(encoding='utf-8', file='./fixes.json', mode='w', ) as fixes_fp:
        dump(allow_nan=False, check_circular=False, ensure_ascii=False, fp=fixes_fp, indent=True, obj=fixes,
             sort_keys=True, )
    logger.info('wrote sorted fixes')
    del fixes_fp

    with open(encoding='utf-8', file='./words.json', mode='r', ) as words_fp:
        words = load(fp=words_fp, )
    words = sorted(words)
    with open(encoding='utf-8', file='./words.json', mode='w', ) as words_fp:
        dump(ensure_ascii=False, fp=words_fp, indent=True, obj=words, )
    logger.info('wrote sorted words')
    del words_fp

    logger.info('total time: {:5.2f}s'.format(time() - time_start))
