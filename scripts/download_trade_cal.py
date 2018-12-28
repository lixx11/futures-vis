#!/usr/bin/env python

"""Download trade calendar for specified date range.

Usage:
    download_fut_daily.py <ts-token> [options]

Options:
    -h --help               Show this screen.
    --start-date=<DATE>     Specify start date [default: 19900101].
    --end-date=<DATE>       Specify end date [default: NOW].
    --exchange=<EXCHANGE>   Specify exchange [default: ALL].
    -o --output=<FILE>      Specify output filename [default: td.csv].
"""


from docopt import docopt
import tushare as ts
from datetime import datetime
import pandas as pd
import sys


EXCHANGES = ('SHFE', 'DCE', 'CFFEX', 'CZCE', 'INE')


if __name__ == "__main__":
    argv = docopt(__doc__)
    tk = argv['<ts-token>']
    exchange = argv['--exchange']
    start_date = argv['--start-date']
    end_date = argv['--end-date']
    if end_date == 'NOW':
        end_date = datetime.now().strftime('%Y%m%d')
    output = argv['--output']

    ts.set_token(tk)
    pro = ts.pro_api()
    if exchange == 'ALL':
        exchanges = EXCHANGES
    else:
        exchanges = (exchange,)
    
    cal_df = None
    for ex in exchanges:
        _df = pro.query(
            'trade_cal', exchange=ex, start_date=start_date, end_date=end_date
        )
        _df = _df.set_index('cal_date')
        if cal_df is None:
            cal_df = pd.DataFrame({
                ex: _df['is_open']
            })
        else:
            cal_df[ex] = _df['is_open']
    cal_df.fillna(0, inplace=True)
    if exchange == 'ALL':
        cal_df['ALL'] = cal_df['SHFE'] + cal_df['DCE'] + cal_df['CFFEX'] + cal_df['CZCE'] + cal_df['INE']
    trading_dates = cal_df[cal_df[exchange] > 0]
    trading_dates.to_csv(output)
    print('Trading dates saved to %s' % output)
