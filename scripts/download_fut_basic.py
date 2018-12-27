#!/usr/bin/env python

"""Download futures basic data from tushare website.

Usage:
    download_fut_basic.py <ts-token> <data-dir>
"""

from docopt import docopt 
import tushare as ts
import os
import pandas as pd


ALL_FIELDS = 'ts_code,symbol,exchange,name,fut_code,trade_unit,per_unit,quote_unit,quote_unit_desc, d_mode_desc,list_date,delist_date,d_month,last_ddate,trade_time_desc'


def get_futures_symbol(instrument):
    return ''.join([c for c in instrument if not c.isdigit()])

if __name__ == "__main__":
    argv = docopt(__doc__)
    ts.set_token(argv['<ts-token>'])
    pro = ts.pro_api()
    data_dir = argv['<data-dir>']

    # download SHFE data
    exchange = 'SHFE'
    df = pro.fut_basic(exchange=exchange, fut_type='1', fields=ALL_FIELDS)
    futures_types = df['name'].apply(get_futures_symbol).unique()
    print('SHFE has %d futures types: %s' % (len(futures_types), str(futures_types)))
    df.to_csv(os.path.join(data_dir, '%s.csv' % exchange), encoding='utf-8', index=False)

    # download DCE data
    exchange = 'DCE'
    df = pro.fut_basic(exchange=exchange, fut_type='1', fields=ALL_FIELDS)
    futures_types = df['name'].apply(get_futures_symbol).unique()
    print('DCE has %d futures types: %s' % (len(futures_types), str(futures_types)))
    df.to_csv(os.path.join(data_dir, '%s.csv' % exchange), encoding='utf-8', index=False)

    # download CZCE data
    exchange = 'CZCE'
    df = pro.fut_basic(exchange=exchange, fut_type='1', fields=ALL_FIELDS)
    futures_types = df['name'].apply(get_futures_symbol).unique()
    print('CZCE has %d futures types: %s' % (len(futures_types), str(futures_types)))
    df.to_csv(os.path.join(data_dir, '%s.csv' % exchange), encoding='utf-8', index=False)

    # download CFFEX data
    exchange = 'CFFEX'
    df = pro.fut_basic(exchange=exchange, fut_type='1', fields=ALL_FIELDS)
    futures_types = df['name'].apply(get_futures_symbol).unique()
    print('CFFEX has %d futures types: %s' % (len(futures_types), str(futures_types)))
    df.to_csv(os.path.join(data_dir, '%s.csv' % exchange), encoding='utf-8', index=False)

    # download INE data
    exchange = 'INE'
    df = pro.fut_basic(exchange=exchange, fut_type='1', fields=ALL_FIELDS)
    futures_types = df['name'].apply(get_futures_symbol).unique()
    print('INE has %d futures types: %s' % (len(futures_types), str(futures_types)))
    df.to_csv(os.path.join(data_dir, '%s.csv' % exchange), encoding='utf-8', index=False)