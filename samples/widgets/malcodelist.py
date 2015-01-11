#!/usr/bin/env python

import logging
import sys
logger = logging.getLogger(__name__)


class MalcodeList (Widget):

    def run(self):

        try:
            import feedparser
        except ImportError:
            logger.error('Please install feedparser python module')
            sys.exit()

        d = feedparser.parse('rss')

        records = list()
        for item in d.entries:
            ref = item.link
            url = 'http://{}'.format(
                item.description.replace('URL: ', '').split(',')[0])

            record = {
                'url': url,
                'ref': ref
            }
            records.append(record)

        return records
