from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.conf import settings
from pyecharts import Line, Bar
import os
import pandas as pd
import numpy as np


REMOTE_HOST = "https://pyecharts.github.io/assets/js"

# Create your views here.
def overview(request):
    template = loader.get_template('futures_data/overview.html')
    # stats_data = pd.read_csv(os.path.join(settings.DATA_DIR), 'daily_stats.csv')
    stats_data = pd.read_csv('D:\\data\\tushare\\daily_stats.csv')

    time_index = pd.to_datetime(stats_data['date'], format='%Y%m%d').dt.strftime('%Y-%m-%d').tolist()
    # total stats
    total_futures_type = stats_data['total_futures_type'].tolist()
    total_instrument = stats_data['total_instrument'].tolist()
    total_vol = stats_data['total_vol'].tolist()
    total_amount = stats_data['total_amount'].tolist()
    total_line = stats_plot(time_index, total_futures_type, total_instrument, total_vol, total_amount)
    # SHF stats
    SHF_futures_type = stats_data['SHF_futures_type'].tolist()
    SHF_instrument = stats_data['SHF_instrument'].tolist()
    SHF_vol = stats_data['SHF_vol'].tolist()
    SHF_amount = stats_data['SHF_amount'].tolist()
    SHF_line = stats_plot(time_index, SHF_futures_type, SHF_instrument, SHF_vol, SHF_amount)
    # DCE stats
    DCE_futures_type = stats_data['DCE_futures_type'].tolist()
    DCE_instrument = stats_data['DCE_instrument'].tolist()
    DCE_vol = stats_data['DCE_vol'].tolist()
    DCE_amount = stats_data['DCE_amount'].tolist()
    DCE_line = stats_plot(time_index, DCE_futures_type, DCE_instrument, DCE_vol, DCE_amount)
    # ZCE stats
    ZCE_futures_type = stats_data['ZCE_futures_type'].tolist()
    ZCE_instrument = stats_data['ZCE_instrument'].tolist()
    ZCE_vol = stats_data['ZCE_vol'].tolist()
    ZCE_amount = stats_data['ZCE_amount'].tolist()
    ZCE_line = stats_plot(time_index, ZCE_futures_type, ZCE_instrument, ZCE_vol, ZCE_amount)
    # CFX stats
    CFX_futures_type = stats_data['CFX_futures_type'].tolist()
    CFX_instrument = stats_data['CFX_instrument'].tolist()
    CFX_vol = stats_data['CFX_vol'].tolist()
    CFX_amount = stats_data['SHF_amount'].tolist()
    CFX_line = stats_plot(time_index, CFX_futures_type, CFX_instrument, CFX_vol, CFX_amount)
    # INE stats
    INE_futures_type = stats_data['INE_futures_type'].tolist()
    INE_instrument = stats_data['INE_instrument'].tolist()
    INE_vol = stats_data['INE_vol'].tolist()
    INE_amount = stats_data['INE_amount'].tolist()
    INE_line = stats_plot(time_index, INE_futures_type, INE_instrument, INE_vol, INE_amount)

    context = dict(
        total_chart=total_line.render_embed(),
        SHF_chart=SHF_line.render_embed(),
        DCE_chart=DCE_line.render_embed(),
        ZCE_chart=ZCE_line.render_embed(),
        CFX_chart=CFX_line.render_embed(),
        INE_chart=INE_line.render_embed(),
        host=REMOTE_HOST,
        script_list=total_line.get_js_dependencies()
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


def SHFE_view(request):
    return HttpResponse('not implemented yet!')


def DCE_view(request):
    return HttpResponse('not implemented yet!')


def CZCE_view(request):
    return HttpResponse('not implemented yet!')


def CFFEX_view(request):
    return HttpResponse('not implemented yet!')


def INE_view(request):
    return HttpResponse('not implemented yet!')
