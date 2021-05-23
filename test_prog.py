print('dm_sm.bank_subsidy test\n'
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

print('Connecting to DWHNW_PDB...')
dsn_new = """(DESCRIPTION=(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)
(HOST=rnb-vmdwh-dbpr03.rci.renault.ru)(PORT=1521))
(ADDRESS=(PROTOCOL=TCP)
(HOST=rnb-vmdwh-dbpr03.rci.renault.ru)(PORT=1521))
(LOAD_BALANCE= yes))
(CONNECT_DATA=(SERVER=DEDICATED)(SERVICE_NAME=DWHNW_PDB)))
"""
connection_new = cx.connect("iz01340", "iz01340", dsn_new)

print('Query in progress...')

query_new = """select *
            from dm_sm.bank_subsidy\
            where app_number is not null"""

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

print('Connecting to DWHPR_DG...')

dsn = """(DESCRIPTION=(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)
(HOST=rnb-vmdwh-dbpr04.rci.renault.ru)(PORT=1521))
(ADDRESS=(PROTOCOL=TCP)
(HOST=rnb-vmdwh-dbpr03.rci.renault.ru)(PORT=1521))
(LOAD_BALANCE= yes))
(CONNECT_DATA=(SERVER=DEDICATED)(SERVICE_NAME=DWHPR_DG)))
"""
connection = cx.connect("iz01340", "iz01340", dsn)

print('Query in progress...')


query = open("query_indicator.sql", "r").read()

query = query.format(year_input, month_input)

ind_month = pd.read_sql(query,
                        con=connection,
                        index_col='APP_NUMBER',
                        parse_dates=['CREDIT_ISSUE_DATE',
                                     'CASKO_START_DATE',
                                     'BIRTHDAY',
                                     'CREDIT_CLOSED_DATE',
                                     'CASKO_END_DATE'
                                     ]
                        )

print('Checking for input period:')

if ((bank_subs['PERIOD_DT'].dt.month == month_input) &
    (year_input == bank_subs['PERIOD_DT'].dt.year)).any():

    print('From DM_SM.BANK_SUBSDY Group by PERIOD_DT...')
    print(bank_subs.groupby(['PERIOD_DT']).agg(['count']))
    print('From DWH.V_INDICATOR_FPA Group by M_OF_FINANCING...')
    print(ind_month.groupby(['M_OF_FINANCING', 'Y_OF_FINANCING']).agg(['count']))



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








