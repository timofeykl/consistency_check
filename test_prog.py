print('smth\n'
      '\n'
      'Wait for further instructions...')


import cx_Oracle as cx
import pandas as pd
import datetime
import sys
import os
import numpy as np

year_input = int(input('Type year:'))
month_input = int(input('Type month:'))

print('Connecting to DWH1...')
dsn_new = """
#connection just like Oracle likes 
"""
connection_new = cx.connect(..., dsn_new)

print('Query in progress...')

query_new = """select *
            from _
            where _ is not null"""

bank_subs = pd.read_sql(query_new,
                        con=connection_new,
                        index_col='APP_NUMBER',
                        parse_dates=['PERIOD_DT',
                                     'CONTRACT_DT',
                                     'RETAIL_DT',
                                     'DELIVERY_DT',
                                     'REGISTRION_DT',
                                     ]
                        )

print('Connecting to DWH2...')

dsn = """!!!
"""
connection = cx.connect("!!!", dsn)

print('Query in progress...')


query = open("query_indicator.sql", "r").read()

query = query.format(year_input, month_input)

ind_month = pd.read_sql(query,
                        con=connection,
                        index_col='APP_NUMBER',
                        parse_dates=['DATE',
                                     'BIRTHDAY',
                                     'DATE',
                                     ]
                        )

print('Checking for input period:')

if ((bank_subs['PERIOD_DT'].dt.month == month_input) &
    (year_input == bank_subs['PERIOD_DT'].dt.year)).any():

    print('')
    print(bank_subs.groupby(['PERIOD_DT']).agg(['count']))
    print('')
    print(ind_month.groupby(['M_', 'Y_']).agg(['count']))



    proceed = input('Do you wish to proceed?' \
                '(Y/N): ').lower()

    if proceed == 'n':
        sys.exit()
    elif proceed != 'y':
        while proceed != 'y' and proceed != 'n':
            proceed = input('Incorrent input. \n' \
                        'Try again: ')
        if proceed == 'n':
            sys.exit()
else:
    print('Month or year do not match input number on dm_sm.bank_subsidy.')
    sys.exit()








