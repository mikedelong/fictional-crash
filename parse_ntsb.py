import urllib
from logging import INFO
from logging import basicConfig
from logging import getLogger
from time import time
from xml.etree import ElementTree

if __name__ == '__main__':
    time_start = time()
    logger = getLogger(__name__, )
    basicConfig(format='%(asctime)s : %(name)s : %(levelname)s : %(message)s', level=INFO, )

    xml_url = 'http://app.ntsb.gov/aviationquery/Download.ashx?type=xml'

    d = urllib.request.urlopen(xml_url).read()
    tree = ElementTree.fromstring(d)

    logger.info('total time: {:5.2f}s'.format(time() - time_start))
