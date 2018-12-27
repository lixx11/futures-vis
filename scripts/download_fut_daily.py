#!/usr/bin/env python

"""Download futures daily data from tushare website.

Usage:
    download_fut_daily.py <ts-token> <data-dir> [options]

Options:
    -h --help               Show this screen.
    --start-date=<DATE>     Specify start date [default: 19900101].
    --end-date=<DATE>       Specify end date [default: NOW].
"""

from docopt import docopt
import tushare as ts
import os
import sys
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, inspect
from tqdm import tqdm
from datetime import datetime
import time


SLEEP_TIME = 5


if __name__ == "__main__":
    argv = docopt(__doc__)
    ts.set_token(argv['<ts-token>'])
    pro = ts.pro_api()
    data_dir = argv['<data-dir>']
    start_date = argv['--start-date']
    end_date = argv['--end-date']
    if end_date == 'NOW':
        end_date = datetime.now().strftime('%Y%m%d')

    # download all daily data for each exchange, calculate detailed statistics and add to csv files
    for exchange in ('SHFE', 'DCE', 'CZCE', 'CFFEX', 'INE'):
        list_file = os.path.join(data_dir, '%s.csv' % exchange)
        list_df = pd.read_csv(list_file)
        ts_code = list_df['ts_code']
        list_df = list_df.set_index('ts_code')
        print('%d instrumnets to be processed' % len(list_df))
        db = create_engine('sqlite:///%s' % (os.path.join(data_dir, '%s.db' % exchange)))

        for i in tqdm(range(len(ts_code))):
            start_date = str(list_df['list_date'][i])
            end_date = str(list_df['delist_date'][i])
            daily_df = pro.fut_daily(ts_code=ts_code[i], start_date=start_date, end_date=end_date)
            daily_df.to_sql(ts_code[i], db, if_exists='replace', index=False)
            list_df.at[ts_code[i], 'vol'] = daily_df['vol'].sum()
            list_df.at[ts_code[i], 'amount'] = daily_df['amount'].sum()
            list_df.at[ts_code[i], 'high'] = daily_df['high'].max()
            list_df.at[ts_code[i], 'low'] = daily_df['low'].min()
            time.sleep(SLEEP_TIME)
        list_df.to_csv(list_file)
    
    # download all daily data for each trading date
    db = create_engine('sqlite:///%s' % (os.path.join(data_dir, 'daily.db')))
    for date in tqdm(pd.date_range(start=start_date, end=end_date)):
        date_str = date.strftime('%Y%m%d')
        daily_df = pro.fut_daily(trade_date=date_str)
        if len(daily_df) > 0:
            daily_df.to_sql(date_str, db, if_exists='replace', index=False)
        time.sleep(SLEEP_TIME)
    # calc summary of futures data
    db = create_engine('sqlite:///%s' % (os.path.join(data_dir, 'daily.db')))
    inspector = inspect(db)
    table_names = inspector.get_table_names()
    dates = pd.to_datetime(table_names)
    dates = dates.sort_values()

    res = {
        'date': [],
        'total_futures_type': [],
        'total_instrument': [],
        'total_vol': [],
        'total_amount': [],
        'SHFE_futures_type': [],
        'SHFE_instrument': [],
        'SHFE_vol': [],
        'SHFE_amount': [],
        'DCE_futures_type': [],
        'DCE_instrument': [],
        'DCE_vol': [],
        'DCE_amount': [],
        'CZCE_futures_type': [],
        'CZCE_instrument': [],
        'CZCE_vol': [],
        'CZCE_amount': [],
        'CFFEX_futures_type': [],
        'CFFEX_instrument': [],
        'CFFEX_vol': [],
        'CFFEX_amount': [],
        'INE_futures_type': [],
        'INE_instrument': [],
        'INE_vol': [],
        'INE_amount': [],
    }
    ts_suffix_to_exchange = {
        'SHF': 'SHFE',
        'DCE': 'DCE',
        'ZCE': 'CZCE',
        'CFX': 'CFFEX',
        'INE': 'INE'
    }
    for date in tqdm(dates):
        date_str = date.strftime('%Y%m%d')
        df = pd.read_sql_table(date_str, db, columns=['ts_code', 'vol', 'amount'])
        df['amount'] = pd.to_numeric(df['amount'])
        df['vol'] = pd.to_numeric(df['vol'])
        df['normal'] = df['ts_code'].apply(lambda x: x.split('.')[0][-4:].isdigit())
        df = df[df['normal'] == True]  # keep normal instruments only
        df['exchange'] = df['ts_code'].apply(lambda x: ts_suffix_to_exchange[x.split('.')[-1]])
        df['type'] = df['ts_code'].apply(lambda x: x.split('.')[0][:-4])
        res['date'].append(date_str)
        res['total_futures_type'].append(len(df['type'].unique()))
        res['total_instrument'].append(len(df['type']))
        res['total_amount'].append(df['amount'].sum())
        res['total_vol'].append(df['vol'].sum())
        for exchange in ('SHFE', 'DCE', 'CZCE', 'CFFEX', 'INE'):
            res['%s_futures_type' % exchange].append(len(df[df['exchange'] == exchange]['type'].unique()))
            res['%s_instrument' % exchange].append(len(df[df['exchange'] == exchange]['type']))
            res['%s_amount' % exchange].append(df[df['exchange'] == exchange]['amount'].sum())
            res['%s_vol' % exchange].append(df[df['exchange'] == exchange]['vol'].sum())
    
    stats_df = pd.DataFrame(res)
    stats_df.to_csv(os.path.join(data_dir, 'daily_stats.csv'), encoding='utf-8', index=False)
