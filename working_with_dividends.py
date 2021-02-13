
import pandas as pd
import numpy as np
import datetime

def pre_processing_dividends(value):
    value = value.split('\n')[0]
    value = value.replace(',', '.')
    return(value)

def pre_processing_dividends_file(dividends):    
    dividends = pd.read_csv('TESTE_1.csv')
    dividends.drop('Unnamed: 0', axis = 'columns', inplace = True)
    dividends.columns = ['Kind', 'Purchase Date', 'Pay Date', 'Value', 'Fund']
    dividends['Fund'].value_counts()

    dividends['Purchase Date'] = dividends['Purchase Date'].apply(lambda x: datetime.datetime.strptime(x, '%d/%m/%Y'))
    dividends['Pay Date'] = dividends['Pay Date'].apply(lambda x: datetime.datetime.strptime(x, '%d/%m/%Y'))

    dividends['Value'] = dividends['Value'].apply(lambda VALUE:pre_processing_dividends(VALUE))
    dividends['Value'] = dividends['Value'].astype(float)

    return(dividends.set_index(dividends['Purchase Date']))


##---------------------------##---------------------------##---------------------------##---------------------------##---------------------------

def pipeline_dividends(df_final_funds, dividends, dict_funds):
    
    grouped_df = df_final_funds.groupby('Stock')
    grouped_dividends = dividends.groupby('Fund')

    all_funds_dividends_recieve = {}
    for i in dict_funds.keys():
        df_fund = grouped_df.get_group(i)
        df_dividends = grouped_dividends.get_group(i)
        fund_dividend_recieve = [] 
        for j in range(len(dict_funds[i])):
            purchase_date = dict_funds[i][j][0]
            invested_value = dict_funds[i][j][1]
            value_purchase_date = df_fund[df_fund.index  == purchase_date]['Adj Close'].values[0]
            cotes = invested_value / value_purchase_date

            start_dividends = df_dividends[df_dividends.index >= purchase_date]
            dividends_recieve = np.array(start_dividends['Value']) * cotes
            dividends_dates_recieve  = np.array(start_dividends['Pay Date']) 
            investment_date = [purchase_date] * len(dividends_recieve)
            cote_at_purchase_date = [value_purchase_date] * len(dividends_recieve)

            fund_dividend_recieve.append(pd.DataFrame({'Pay Date':dividends_dates_recieve, 'Recieve':dividends_recieve}))

        all_funds_dividends_recieve[i] = fund_dividend_recieve
        
    
    all_dividends_recieve_df = []

    for i in all_funds_dividends_recieve.keys():
        to_concat = []
        for j in range(len(all_funds_dividends_recieve[i])):
            to_concat.append(all_funds_dividends_recieve[i][j])

        df_dividend = pd.concat(to_concat)

        grouped_pay_day = df_dividend.groupby('Pay Date')    
        pay_dates = df_dividend['Pay Date'].unique()
        recieve_value = []
        for k in pay_dates:
            df_pay_date = grouped_pay_day.get_group(k)
            recieve_value.append(df_pay_date['Recieve'].sum())

        df_dividens_recieve_final = pd.DataFrame({'Pay Day':pay_dates, 'Dividends Recieve':recieve_value})
        df_dividens_recieve_final = df_dividens_recieve_final.sort_values(by = 'Pay Day')
        df_dividens_recieve_final.index = df_dividens_recieve_final['Pay Day']
        df_dividens_recieve_final.drop('Pay Day', axis = 'columns', inplace = True)
        df_dividens_recieve_final['Acumulated Dividends'] = df_dividens_recieve_final['Dividends Recieve'].cumsum()
        df_dividens_recieve_final['Fund'] = i

        all_dividends_recieve_df.append(df_dividens_recieve_final)

    all_dividends_recieve_df = pd.concat(all_dividends_recieve_df) 
           
    return(all_dividends_recieve_df)

##---------------------------##---------------------------##---------------------------##---------------------------##-------------------

def get_all_acumulated_dividends(df_dividends):

    grouped_dividends = df_dividends.groupby('Fund')
    all_acumulated_dividends = 0
    for i in df_dividends['Fund'].unique():
        df_fund = grouped_dividends.get_group(i)
        all_acumulated_dividends = all_acumulated_dividends + df_fund.loc[max(df_fund.index)]['Acumulated Dividends']

    return(all_acumulated_dividends)
    
##---------------------------##---------------------------##---------------------------##---------------------------##-------------------        
    
def get_acumulated_dividend(df_dividends, fund):
    grouped_dividends = df_dividends.groupby('Fund')
    df_fund = grouped_dividends.get_group(fund)
    return(df_fund.loc[max(df_fund.index)]['Acumulated Dividends'])  
    
    

