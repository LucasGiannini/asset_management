import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas_datareader import data as pdr
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta, date

#-----------------------#----------------------#-----------------------#----------------------
## The function recieves the imported table containing the inputs and transforms it into a dictionary
## The dictionary is then used to perform the operations. It is a better data structure for this case.


def define_input_dict(df_input):
    
    grouped_input = df_input.groupby('stock')
    input_dict = {}
    for i in df_input['stock'].values:
        purchase_value_date = []
        dates = grouped_input.get_group(i)['stock_buy_date'].values.tolist()
        values = grouped_input.get_group(i)['purchased_value'].values.tolist()
        for j in range(len(dates)):
            purchase_value_date.append((dates[j], values[j]))

        input_dict[i] = purchase_value_date
        
    return(input_dict)


#-----------------------#----------------------#-----------------------#----------------------
## This function recieves the input_dictionary and starts inputing the information in the final table.
## It requests the stocks values and adds the purchased values in each date.

def generate_dataframe_stocks(input_dict, today_str):
    stocks = list(input_dict.keys())   
    stocks_request = [i+'.SA' for i in stocks] 
    all_dfs = []
    
    for i in range(len(stocks)):
        for j in range(len(input_dict[stocks[i]])):
            ## Requests stock values
            df_stock = pdr.DataReader(stocks_request[i], 'yahoo', input_dict[stocks[i]][j][0], today_str) 
            df_stock['Stock'] = stocks[i]
            
            ## Adds purchased values in right dates.
            df_stock['Purchased Value'] = 0.0
            df_stock.at[input_dict[stocks[i]][j][0], 'Purchased Value'] = input_dict[stocks[i]][j][1]           
                   
        
            all_dfs.append(df_stock)

    df_final = pd.concat(all_dfs)
    return(df_final)  

#-----------------------#----------------------#-----------------------#----------------------

## This is the main function to create the table. It recieves the data frame created in the last function 
## (containing the stocks values and purchased values in each day). This function calculates several features for the table,
## in only ine loop.

## It recieves the data frame created in the previuos table, the column name the percentual growth should be calculated
## and the input dictionary.

def calculate_daily_percentual_growth(df_with_purchased, column, input_dict):
    grouped_stock = df_with_purchased.groupby('Stock')
    all_dfs = []
    
    for i in list(input_dict.keys()):
        df_stock = grouped_stock.get_group(i) ## For each stock
        
        purchased_value = np.array(df_stock['Purchased Value'])
        
        accumulative_invested_value = []
        percentual_growth_stock = []
        accumulative_investment = []
        accumulative_growth_stock = []
        
        percentual_growth_stock.append(0)
        for j in range(df_stock.shape[0]-1): 
            relative_value = ((df_stock.iloc[j+1][column] - df_stock.iloc[j][column]) / df_stock.iloc[j][column]) * 100

            percentual_growth_stock.append(relative_value) ## Calculating the daily percentual growth of the column
            
            if j == 0:
                accumulative_value = percentual_growth_stock[j]
                
                accumulative_invested_value.append(purchased_value[j])
                accumulative_investment.append(accumulative_invested_value[j])
                
            else:   
                accumulative_value = ((accumulative_growth_stock[j-1]/100 + 1) * (percentual_growth_stock[j]/100 + 1)) - 1
                
                accumulative_invested_value.append(purchased_value[j] + accumulative_invested_value[j-1] )
                accumulative_investment.append( (accumulative_investment[j-1] + purchased_value[j]) * 
                                               (1 + percentual_growth_stock[j]/100 ))
                
            accumulative_growth_stock.append(accumulative_value * 100)
            
         ## The last values of some features should be calculated afterwars, since the loop goes untill n-1
        
        accumulative_value_last =  (accumulative_growth_stock[-1]/100 + 1) * (percentual_growth_stock[-1]/100 + 1) - 1 
        accumulative_growth_stock.append(accumulative_value_last * 100)     
        
        accumulative_invested_value.append(purchased_value[-1] + accumulative_invested_value[-1] )
        accumulative_investment.append(accumulative_investment[-1] * (1 + percentual_growth_stock[-1]/100 ))
        
        
        df_stock['Total Invested'] = accumulative_invested_value
        df_stock['Percentual Stock Daily Growth (%)'] = percentual_growth_stock         
        df_stock['Accumulated Value'] = accumulative_investment
        df_stock['Your Current Yeld (%)'] = ( (df_stock['Accumulated Value'] - df_stock['Total Invested']) / 
                                             df_stock['Total Invested'])* 100
        df_stock['Stock Current Yeld (%)'] = accumulative_growth_stock
        
        all_dfs.append(df_stock)
        
    df_final = pd.concat(all_dfs)
    
    return(df_final)

    
#-----------------------#----------------------#-----------------------#----------------------

## This function basicallly removes the duplicates in the index values for each stock

def add_purchased_value_column(df_requests, input_dict):    
    grouped_stock = df_requests.groupby('Stock')
    all_dfs = []
    for i in list(input_dict.keys()):
        df_stock = grouped_stock.get_group(i)
        df_stock = df_stock.loc[~df_stock.index.duplicated(keep='last')] ## The duplicates are removed, 
                                                                         ## and we keep the latest date

        all_dfs.append(df_stock)

    df_with_purchased = pd.concat(all_dfs)
    return(df_with_purchased)  

#-----------------------#----------------------#-----------------------#----------------------

def pipeline_and_performance_info(df_input):
    
    today_str = datetime.today().strftime('%Y-%m-%d')
    
    input_dict = define_input_dict(df_input)
    df_requests = generate_dataframe_stocks(input_dict, today_str)
    df_with_purchased = add_purchased_value_column(df_requests, input_dict)
    df_final = calculate_daily_percentual_growth(df_with_purchased, 'Adj Close', input_dict)
    
    df_last_day = df_final[df_final.index.isin([max(df_final.index)])]  ## Gets the last day of all stocks 

    ## Calculate the required values
    total_invested_value = df_last_day['Total Invested'].sum()
    total_accumulated_value = df_last_day['Accumulated Value'].sum()
    total_yeld = ((total_accumulated_value / total_invested_value) - 1) * 100
    profit = total_accumulated_value - total_invested_value
    
    return(df_final, {'total_invested_value':total_invested_value, 'total_accumulated_value':total_accumulated_value,
                     'total_yeld': total_yeld, 'profit':profit})
#-----------------------#----------------------#-----------------------#----------------------

def preprocessing_dataframe(df, investment_date, df_input_fix, i):
    
    df_date_filtered = df[df.index >= investment_date]
    print(df_input_fix.index[i])
    df_date_filtered.at[df_input_fix.index[i], 'Purchased Value'] = df_input_fix[df_input_fix.index == df_input_fix.index[i]]['fix_purchased_value'].values[0]
        
    df_date_filtered['Investment Yeld'] = df['Index Value'] * df_input_fix.iloc[i]['fix_indexes']
        
    df_i_final = calculate_acc_fixed(df_date_filtered) 
    
    return(df_i_final)

#-----------------------#----------------------#-----------------------#----------------------
def calculate_acc_fixed(df):

    investment_yeld = np.array(df['Investment Yeld'])
    index_values = np.array(df['Index Value'])
    purchased_value = df.iloc[0]['Purchased Value']

    accumulated_value = np.zeros(len(investment_yeld))
    accumulated_yeld = np.zeros(len(investment_yeld))
    accumulated_investment = np.zeros(len(investment_yeld))
    
    for i in range(len(investment_yeld)):
        if i == 0:
            accumulated_yeld[i] = investment_yeld[i]
            accumulated_value[i] = purchased_value 
            accumulated_investment[i] = purchased_value
        else:
            accumulated_yeld[i] = (accumulated_yeld[i-1] + 1)  * (index_values[i] + 1) - 1
            accumulated_value[i] = purchased_value * (1 + accumulated_yeld[i])
            accumulated_investment[i] = purchased_value
            
    df['Total Invested'] = accumulated_investment
    df['Your Current Yeld (%)'] = accumulated_yeld
    df['Accumulated Value'] = accumulated_value

    return(df)

#-----------------------#----------------------#-----------------------#----------------------

def bbc_api(codes_dict, code, start_date, finish_date):
    url = 'http://api.bcb.gov.br/dados/serie/bcdata.sgs.{}/dados?formato=json'.format(codes_dict[code])
    url = url + '&dataInicial=' + start_date + '&dataFinal=' + finish_date
    df = pd.read_json(url)
    df['data'] = pd.to_datetime(df['data'], dayfirst = True)
    return(df.set_index('data'))


#-----------------------#----------------------#-----------------------#----------------------

def calculate_fix_dataframe(start_date, finish_date, codes_dict, df_input_fix):
    
    cdi = bbc_api(codes_dict, 'cdi', start_date, finish_date)
    ipca = bbc_api(codes_dict, 'ipca', start_date, finish_date)

    cdi['Index Value'] = cdi['valor'] / 100
    ipca['Index Value'] = ipca['valor'] / 100

    cdi['Purchased Value'] = 0
    ipca['Purchased Value'] = 0

    cdi.drop('valor', axis = 'columns', inplace = True)
    ipca.drop('valor', axis = 'columns', inplace = True)

    all_fixed = []

    count_ipca = 0
    count_cdi = 0
    for i in range(df_input_fix.shape[0]):
        investment_date =  df_input_fix.iloc[i].name
        if df_input_fix.iloc[i]['base'] == 'ipca':
            count_ipca = count_ipca + 1

            ipca_i_final = preprocessing_dataframe(ipca, investment_date, df_input_fix, i)
            ipca_i_final['Index Base'] = 'ipca'
            ipca_i_final['Stock'] = 'ipca fix ' + str(count_ipca)
            ipca_i_final
            all_fixed.append(ipca_i_final)     


        if df_input_fix.iloc[i]['base'] == 'cdi':
            count_cdi = count_cdi + 1

            cdi_i_final = preprocessing_dataframe(cdi, investment_date, df_input_fix, i)
            cdi_i_final['Index Base'] = 'cdi'
            cdi_i_final['Stock'] = 'cdi fix ' + str(count_cdi)
            all_fixed.append(cdi_i_final)

    fix_final = pd.concat(all_fixed)    
    
    return(fix_final)

#-----------------------#----------------------#-----------------------#----------------------

def calculate_performance_fix(fix_final):
    grouped_fix = fix_final.groupby('Stock')

    fix_last_day_list = []
    for i in fix_final['Stock'].unique():
        df = grouped_fix.get_group(i)
        fix_last_day_list.append(df[df.index.isin([max(df.index)])])
    fix_last_day = pd.concat(fix_last_day_list)

    total_invested_value_fix = fix_last_day['Total Invested'].sum()
    total_accumulated_value_fix = fix_last_day['Accumulated Value'].sum()
    total_yeld_fix = ((total_accumulated_value_fix / total_invested_value_fix) - 1) * 100
    profit_fix = total_accumulated_value_fix - total_invested_value_fix

    fix_dict =  {'total_invested_value':total_invested_value_fix, 'total_accumulated_value':total_accumulated_value_fix,
                         ' total_yeld': total_yeld_fix, 'profit':profit_fix}
    
    return(fix_dict)