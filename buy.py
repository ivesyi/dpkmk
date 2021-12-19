import streamlit as st
import requests
import json
import pandas as pd
from glom import glom
import numpy as np

import ast
from pandas import json_normalize


def only_dict(d):
    '''
    Convert json string representation of dictionary to a python dict
    '''
    return ast.literal_eval(d)


def list_of_dicts(ld):
    '''
    Create a mapping of the tuples formed after
    converting json strings of list to a python list
    '''
    return dict([(list(d.values())[1], list(d.values())[0]) for d in ast.literal_eval(ld)])


def calc_purity(features):
    nums = tuple(features.split('-')[:-1])

    purity_dict = {}
    for num in nums:
        x = int(num) % 10
        if purity_dict.get(x):
            purity_dict[x] = purity_dict[x] + 1
        else:
            purity_dict[x] = 1

    all_values = purity_dict.values()
    return max(all_values)


def calc_phase(token_id):
    if token_id.startswith(1):
        return '创世猫'

    if token_id.startswith(3):
        return '后代猫'


def calc_params(contract_params):
    params_dict = {}
    all_kvp = contract_params.split(',')
    kvp = [(k, v) for k, v in zip(all_kvp[::2], all_kvp[1::2])]
    params_dict.update(kvp)
    # print(params_dict)
    # print(params_dict['body'])

    for keys in params_dict:
        params_dict[keys] = int(params_dict[keys])
    params_dict['sum'] = params_dict['strength'] + params_dict['agility'] + params_dict['stamina'] + params_dict[
        'endurance'] + params_dict['luck'] + params_dict['will'] + params_dict['spirit']
    # print(params_dict['sum'])
    return params_dict


kt_params = {'order_by_price': 'asc', 'order_by_time': '', 'phase': 1, 'reproduction_times': -1, 'page': 1,
             'per_page': 5}


# params['order_by_time'] = ''
# params['reproduction_times'] = ''


def display(data):
    cats = data['list']['data']
    df = json_normalize(cats)

    show_columns = {'token_id': 'ID', 'price': 'BNB价格', 'usdt_price': 'USDT价格',
                    'contract_cat.breeding_times': '可繁殖次数', 'contract_cat.features': '纯度'}

    show_params_columns = {'sum': '数值和', 'strength': '力量', 'agility': '敏捷', 'stamina': '耐力1', 'endurance': '耐力2',
                           'luck': '幸运',
                           'will': '意志', 'spirit': '精神'}

    params_df = json_normalize(df['contract_cat.contract_params'].apply(calc_params).tolist())
    show_params_df = params_df[['sum', 'strength', 'agility', 'stamina', 'endurance', 'luck', 'will', 'spirit']].rename(
        columns=show_params_columns)

    show_df = df[
        ['token_id', 'price', 'usdt_price', 'contract_cat.breeding_times', 'contract_cat.features']].rename(
        columns=show_columns)

    show_df.BNB价格 = show_df.BNB价格.apply(lambda x: round(float(x), 2))
    show_df.可繁殖次数 = show_df.可繁殖次数.apply(lambda x: 5 - x)
    show_df.纯度 = show_df.纯度.apply(lambda x: calc_purity(x))

    show_list = show_df.join([show_params_df])

    print(show_list.head())

    st.dataframe(show_list.style.highlight_max(axis=0), 900, 1000)  # Same as st.write(df)

    # A = json_normalize(cats.apply(only_dict).tolist()).add_prefix('columnA.')
    # B = json_normalize(cats.apply(list_of_dicts).tolist()).add_prefix('columnB.pos.')

    # df = df['token_id','phase','price','usdt_price','contract_cat.breeding_times']
    # print(df)
    # for cat in cats:
    #     print(cat['token_id'])
    # df = pd.DataFrame(
    #     np.random.randn(50, 20),
    #     columns=('ID', '序号', '价格', '可繁殖次数', '纯度', '数值合', '力量', '敏捷', '耐力1', '耐力2', '幸运', '意志', '精神'))
    pass


try:
    response = requests.get('https://www.dontplaywithkitty.io/api/api/v1/market/list', params=kt_params, timeout=10)
    # print(response.text)
    response.raise_for_status()
    response_dict = json.loads(response.text)
    if response_dict['code'] == '10000':
        display(response_dict['data'])
    # Code here will only run if the request is successful
except requests.exceptions.HTTPError as errh:
    print(errh)
except requests.exceptions.ConnectionError as errc:
    print(errc)
except requests.exceptions.Timeout as errt:
    print(errt)
except requests.exceptions.RequestException as err:
    print(err)

# st.write("""
#     #My first app
#     Hello *world!*
# """)


# df = pd.DataFrame(
#     np.random.randn(50, 20),
#     columns=('col %d' % i for i in range(20)))
#
# st.dataframe(df)  # Same as st.write(df)
