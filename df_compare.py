from test_prog import *
from pathlib import Path

# uploading null values

print('Null values proceeding.')

#only null cells
null_check = bank_subs.loc[:, bank_subs.isna().any()]
#only null columns
null_check = null_check[null_check.isna().any(axis=1)]
null_check = bank_subs[['BRAND',
                        'VEH_TYPE']].merge(null_check
                                           , how='right'
                                           , on='APP_NUMBER')


print(null_check)

print('Check MODEL_CD for UNKNOWN')

unknown_m = bank_subs[bank_subs['MODEL_CD'] == 'UNKNOWN']
print(unknown_m)

# duplicated VIN
dub_vin = bank_subs[bank_subs.duplicated(subset=['VIN'],
                                         keep=False)]

print(dub_vin)

# duplicated APP_NUMBER
dub_app = bank_subs[bank_subs.index.duplicated(keep=False)]

print(dub_app)

# initial subsidy check
vin_fin = pd.merge(bank_subs.loc[:, ['SUBRNB_AMT', 'CREDIT_AMT']],
                   ind_month.loc[:, ['VALUE_AMT', 'TOTAL_FINANCE_AMOUNT']],
                   how='outer',
                   on='APP_NUMBER',
                   )

vin_fin = vin_fin[(abs(vin_fin['SUBRNB_AMT'] - vin_fin['VALUE_AMT']) > 50)
                  | (vin_fin['CREDIT_AMT'] != vin_fin['TOTAL_FINANCE_AMOUNT'])]
print(vin_fin)


print('Comparing sum of finance amount from both DB...')
# old DWH
query = open('credit_amt_old.sql', 'r').read()
query = query.format(year_input, month_input, month_input + 1)

old_amt = pd.read_sql(query
                      , con=connection
                      , parse_dates=['CREDIT_ISSUE_DATE'])

# new DWH
query_new = open('credit_amt_new.sql', 'r').read()
query_new = query_new.format(year_input, month_input, month_input + 1)

new_amt = pd.read_sql(query_new
                      , con=connection_new
                      , parse_dates=['CREDIT_DATE'])

amt_comp = pd.merge(new_amt.loc[:, ['NEW_AMT', 'CREDIT_NUMBER']],
                    old_amt.loc[:, ['OLD_AMT', 'CN']],
                    how='outer',
                    left_on='CREDIT_NUMBER',
                    right_on='CN')

amt_comp = amt_comp[(amt_comp['NEW_AMT'] != amt_comp['OLD_AMT'])]

print(amt_comp)

# Simple check cells for RRP and 'круг'
print('RRP & BRAND check...')
rrp_brand = bank_subs[((bank_subs['CREDIT_PROGRAM_NM'].
                        str.contains("rrp", na=False, case=False))
                       & (~(bank_subs['RRP_DISCOUNT_PRC'] > 0)))
                      |
                      ((bank_subs['CREDIT_PROGRAM_NM'].str.contains("круг", na=False, case=False))
                       & (~(bank_subs['CREDIT_PROGRAM_NM'].str.contains("rrp", na=False, case=False)))
                       & (~(bank_subs['BRAND_DISCOUNT_PRC'] > 0)))]
print(rrp_brand)

print('Negative value check for critical columns...')


#somehow 'less' didn't work
sub_zero = bank_subs[(bank_subs['VEHICLE_COST_AMT'] < 0) |
                               (bank_subs['CASCO_SUBSIDY_AMT'] < 0) |
                                (bank_subs['NETTO_CREDIT_CAR_AMT'] < 0) |
                               (bank_subs['CREDIT_AMT'] < 0) |
                               (bank_subs['INTEREST_SUBSIDY_PRC'] < 0)]

print(sub_zero)

#groupby

subs_group = bank_subs.groupby(['BRAND', 'VEH_TYPE'])
subs_group = subs_group.agg({"CREDIT_CONTRACT_NUM": "count",
                             "CASCO_SUBSIDY_AMT": "sum",
                             "CREDIT_AMT": "sum",
                             "SUBRNB_AMT": "sum",
                             "SERV_SPREAD_AMT": "sum",
                             "AF_SPREAD_AMT": "sum",
                             "SUB_EW_AMT": "sum",
                             "NET_SUBSIDY_AMT": "sum",
                             "SUBRNB_RECALC_AMT": "sum",
                             "AF_SPREAD_RECLAC_AMT": "sum",
                             "NET_RECALC_AMT": "sum",
                             "LOYALTY_SUBSIDY_AMT": "sum",
                             "RRP_SUBSIDY_AMT": "sum",
                             "INTEREST_SUBSIDY_AMT": "sum"
                             })

print(subs_group)

print('Uploading to XLSX...')

writer = pd.ExcelWriter\
    ('test_subsidy_'+str(month_input)+'_'+str(year_input)+'.xlsx'
     , engine='xlsxwriter')

ind_month.to_excel(writer, sheet_name='')
bank_subs.to_excel(writer, sheet_name='dm_sm.bank_subsidy')
null_check.to_excel(writer, sheet_name='total_null_check')
unknown_m.to_excel(writer, sheet_name='UNKNOWN_MODEL_CD')
dub_app.to_excel(writer, sheet_name='duplicate_apps')
dub_vin.to_excel(writer, sheet_name='duplicate_vins')
vin_fin.to_excel(writer, sheet_name='initital_subs_and_fin_check')
amt_comp.to_excel(writer, sheet_name='total_finance_check')
rrp_brand.to_excel(writer, sheet_name='rrp_brand_check')
sub_zero.to_excel(writer, sheet_name='negative_values_check')
subs_group.to_excel(writer, sheet_name='aggregated_values')

writer.save()

print('Done.')

#df.groupby(['Col1','Col2','Col3']).agg({'Col3': ['count'], 'Col4': ['count','sum']})


# ((bank_subs['CREDIT_PROGRAM_NM'].isin(["круг"]))
# & ((bank_subs['BRAND_DISCOUNT_PRC'] > 0)))]


# [bank_subs.loc[:, ['SUBRNB_AMT', 'CREDIT_AMT']]]


# df = pd.read_csv("dup.csv")
# app_series = bank_subs["APP_NUMBER"]
# df[ids.isin(ids[ids.duplicated()])].sort("ID")
#
# dupl =
#
# print(pd.merge(ind_month
#          , bank_subs
#          , how='left'
#          , on='APP_NUMBER'
#          , validate='many_to_one'))
#
#
