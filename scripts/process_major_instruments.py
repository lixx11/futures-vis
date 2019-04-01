#!/usr/bin/env python

"""Process futures data to obtain major instruments info.

Usage:
    download_fut_daily.py <data-dir> [options]

Options:
    -h --help               Show this screen.
    --TD=<FILE>             Specify trading dates file [default: td.csv].
"""


import pandas as pd 
from docopt import docopt
import os
from sqlalchemy import create_engine, inspect
from tqdm import tqdm
import sys
from datetime import datetime
import numpy as np


EXCHANGES = ('SHFE', 'DCE', 'CFFEX', 'CZCE', 'INE')


if __name__ == "__main__":
    argv = docopt(__doc__)
    data_dir = argv['<data-dir>']
    td = argv['--TD']
    trading_dates = pd.read_csv(td)['cal_date'].values.tolist()
    today = datetime.now().strftime('%Y%m%d')
    latest_trading_date = [date for date in trading_dates if datetime.strptime(str(date), '%Y%m%d') <= datetime.strptime(today, '%Y%m%d')][-1]

    futures_codes = []
    for ex in EXCHANGES:
        df = pd.read_csv(
            os.path.join(data_dir, '%s.csv' % ex)
        )
        futures_codes += df['fut_code'].unique().tolist()
    print('Total futures types: %d' % len(futures_codes))

    major_instruments = {code: [] for code in futures_codes}
    daily_db = create_engine('sqlite:///%s' % (os.path.join(data_dir, 'daily.db')))
    inspector = inspect(daily_db)
    tables = inspector.get_table_names()
    instruments_db = create_engine('sqlite:///%s' % (os.path.join(data_dir, 'major_instruments.db')))
    
    for table in tqdm(tables):
        df = pd.read_sql_table(table, daily_db)
        df.dropna(inplace=True)
        df['is_normal'] = df['ts_code'].apply(lambda x: x.split('.')[0][-1].isdigit())
        df = df[df['is_normal'] == True]  # keep normal instruments only
        df['code'] = df['ts_code'].apply(lambda x: ''.join(c for c in x.split('.')[0] if not c.isdigit()))
        for code in futures_codes:
            instruments_rows = df[df['code'] == code]
            if len(instruments_rows) == 0:
                continue
            major_row = instruments_rows.loc[instruments_rows['vol'].idxmax()]
            major_instruments[code].append({
                'date': table,
                'open': major_row['open'],
                'high': major_row['high'],
                'low': major_row['low'],
                'close': major_row['close'],
                'vol': major_row['vol'],
                'amount': major_row['amount'],
                'instrument': major_row['ts_code'].split('.')[0]
            })
    
    instruments_info = []
    for code in major_instruments.keys():
        if len(major_instruments[code]) == 0:
            continue
        instrument_df = pd.DataFrame(major_instruments[code], columns=['date', 'instrument', 'open', 'high', 'low', 'close', 'vol', 'amount'])
        instruments_df = instrument_df.sort_values('date')
        instrument_df.to_sql(code, instruments_db, if_exists='replace', index=False)
        latest_price = instrument_df.iloc[-1]['close']
        update_time = instrument_df.iloc[-1]['date']
        list_date = instrument_df.iloc[0]['date']
        alive = str(update_time) == latest_trading_date
        life_time = (datetime.strptime(update_time, '%Y%m%d') - datetime.strptime(list_date, '%Y%m%d')).days
        vol =instrument_df['vol'].sum()
        amount = instrument_df['amount'].sum()
        latest_vol = instrument_df.iloc[-1]['vol']
        latest_amount = instrument_df.iloc[-1]['amount']
        high = instrument_df['high'].max()
        low = instrument_df['low'].min()
        max_fluc = high / low - 1.
        instruments_info.append({
            'symbol': code,
            'latest_price': latest_price,
            'update_time': update_time,
            'list_date': list_date,
            'alive': alive,
            'life_time': life_time,
            'vol': vol,
            'amount': amount,
            'latest_vol': latest_vol,
            'latest_amount': latest_amount,
            'high': high,
            'low': low,
            'max_fluc': max_fluc,
        })
    
    instruments_info_df = pd.DataFrame(
        instruments_info, 
        columns=['symbol', 'latest_price', 'update_time', 'list_date', 'alive', 'life_time', 'vol', 'amount', 'latest_vol', 'latest_amount', 'high', 'low', 'max_fluc']
    )
    instruments_info_df.to_csv(
        os.path.join(data_dir, 'major_instruments_info.csv'), 
        encoding='utf-8', index=False
    )
