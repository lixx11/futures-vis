from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.conf import settings
from pyecharts import Line, Bar
from pyecharts.echarts import events
from pyecharts_javascripthon.dom import alert
import os
import pandas as pd
from sqlalchemy import create_engine, inspect
import numpy as np
from tqdm import tqdm
from datetime import datetime, timedelta
import csv


REMOTE_HOST = "https://pyecharts.github.io/assets/js"

# Create your views here.
def overview(request):
    template = loader.get_template('futures_data/overview.html')
    stats_data = pd.read_csv(os.path.join(settings.DATA_DIR, 'daily.csv'))

    time_index = pd.to_datetime(stats_data['date'], format='%Y%m%d').dt.strftime('%Y-%m-%d').tolist()
    charts = {}
    for exchange in ('total', 'SHFE', 'DCE', 'CZCE', 'CFFEX', 'INE'):
        futures_type = stats_data['%s_futures_type' % exchange].tolist()
        instrument = stats_data['%s_instrument' % exchange].tolist()
        vol = stats_data['%s_vol' % exchange].tolist()
        amount = stats_data['%s_amount' % exchange].tolist()
        charts[exchange] = stats_plot(time_index, futures_type, instrument, vol, amount)

    context = dict(
        total_chart=charts['total'].render_embed(),
        SHFE_chart=charts['SHFE'].render_embed(),
        DCE_chart=charts['DCE'].render_embed(),
        CZCE_chart=charts['CZCE'].render_embed(),
        CFFEX_chart=charts['CFFEX'].render_embed(),
        INE_chart=charts['INE'].render_embed(),
        host=REMOTE_HOST,
        script_list=charts['total'].get_js_dependencies(),
        chart_ids=(
            charts['total']._chart_id, 
            charts['SHFE']._chart_id, 
            charts['DCE']._chart_id, 
            charts['CZCE']._chart_id, 
            charts['CFFEX']._chart_id, 
            charts['INE']._chart_id
        ),
        tag='overview',
    )
    return HttpResponse(template.render(context, request))


def stats_plot(time_index, futures_type, instrument, vol, amount):
    line = Line('', '', width='100%')
    line.add(
        '期货种类',
        time_index,
        futures_type,
        is_datazoom_show=True,
        datazoom_type='both',
        datazoom_range=[0, 100],
        is_more_utils=True,
    )
    line.add(
        '期货合约',
        time_index,
        instrument,
        is_datazoom_show=True,
        datazoom_type='both',
        datazoom_range=[0, 100],
        is_more_utils=True,
    )
    line.add(
        '交易量/手',
        time_index,
        vol,
        is_datazoom_show=True,
        datazoom_type='both',
        datazoom_range=[0, 100],
        is_more_utils=True,
    )
    line.add(
        '交易额/万元',
        time_index,
        amount,
        is_datazoom_show=True,
        datazoom_type='both',
        datazoom_range=[0, 100],
        is_more_utils=True,
        legend_selectedmode='single'
    )
    return line


def callback_test(params):
    alert(params.name)


def exchange_view(request, exchange):
    if exchange == 'SHFE':
        exchange_ch = '上期所'
    elif exchange == 'DCE':
        exchange_ch = '大商所'
    elif exchange == 'CZCE':
        exchange_ch = '郑商所'
    elif exchange == 'CFFEX':
        exchange_ch = '中金所'
    elif exchange == 'INE':
        exchange_ch = '上期原油'
    else:
        return HttpResponse('不支持此交易所：%s' % exchange)
    
    template = loader.get_template('futures_data/exchange.html')

    daily_data = pd.read_csv(os.path.join(settings.DATA_DIR, 'daily.csv'))
    time_index = pd.to_datetime(daily_data['date'], format='%Y%m%d').dt.strftime('%Y-%m-%d').tolist()

    futures_type = daily_data['%s_futures_type' % exchange].tolist()
    instrument = daily_data['%s_instrument' % exchange].tolist()
    vol = daily_data['%s_vol' % exchange].tolist()
    amount = daily_data['%s_amount' % exchange].tolist()
    line = stats_plot(time_index, futures_type, instrument, vol, amount)

    context = dict(
        chart=line.render_embed(),
        host=REMOTE_HOST,
        script_list=line.get_js_dependencies(),
        exchange=exchange,
        exchange_ch=exchange_ch,
        tag=exchange,
    )
    return HttpResponse(template.render(context, request))


def instruments_data(request, exchange):
    futures_data = pd.read_csv(os.path.join(settings.DATA_DIR, '%s.csv' % exchange))
    ts_code = futures_data['ts_code'].values
    symbol = futures_data['symbol'].values
    name = futures_data['name'].values
    code = futures_data['fut_code'].values
    list_date = list(map(str, futures_data['list_date'].values))
    delist_date = list(map(str, futures_data['delist_date'].values))
    life_time = (pd.to_datetime(delist_date) - pd.to_datetime(list_date)).days
    now = datetime.now()
    alive = (pd.to_datetime(delist_date) - pd.to_datetime(now)) > timedelta(0)
    vol = futures_data['vol'].values
    amount = futures_data['amount'].values
    high = futures_data['high'].values
    low = futures_data['low'].values
    max_fluc = high / low - 1.
    low[np.isnan(low)] = 0.
    high[np.isnan(high)] = 0.
    max_fluc[np.isnan(max_fluc)] = 0.
    response_data = []
    for i in range(len(ts_code)):
        response_data.append({
            'symbol': str(symbol[i]),
            'name': str(name[i]),
            'code': str(code[i]),
            'list_date': str(list_date[i]),
            'delist_date': str(delist_date[i]),
            'life_time': str(life_time[i]),
            'alive': str(alive[i]),
            'vol': str(vol[i]),
            'amount': str(amount[i]),
            'high': str(high[i]),
            'low': str(low[i]),
            'max_fluc': str('%.2f' % (max_fluc[i] * 100))
        })
    return JsonResponse(response_data, safe=False)


def major_instruments_view(request):
    template = loader.get_template('futures_data/major_instruments.html')
    context = dict(
        tag='major_instruments',
    )
    return HttpResponse(template.render(context, request))


def major_instruments_data(request, code, plot_type):
    if code == 'ALL':  # major instruments basic info
        major_instruments_info_file = os.path.join(settings.DATA_DIR, 'major_instruments_info.csv')
        major_instruments_info = pd.read_csv(major_instruments_info_file)
        response_data = major_instruments_info.to_dict(orient='records')
        return JsonResponse(response_data, safe=False)
    else:  # time series of specified instrument
        db = create_engine('sqlite:///%s' % (os.path.join(settings.DATA_DIR, 'major_instruments.db')))
        df = pd.read_sql_table(code, db)
        date = pd.to_datetime(df['date'], format='%Y%m%d').dt.strftime('%Y-%m-%d').tolist()
        if plot_type == 'price':
            data = df['close'].values.tolist()
        elif plot_type == 'vol':
            data = df['vol'].values.tolist()
        elif plot_type == 'amount':
            data = df['amount'].values.tolist()
        else:
            return HttpResponse('Wrong plot type: %s' % plot_type)
        response_data = list(map(list, zip(*[date, data]))) 
        return JsonResponse(response_data, safe=False)


def basis_view(request):
    template = loader.get_template('futures_data/basis.html')
    context = dict(
        tag='basis'
    )
    return HttpResponse(template.render(context, request))
