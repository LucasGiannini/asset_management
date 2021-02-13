
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas_datareader import data as pdr
from datetime import datetime, timedelta, date
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image, ImageFont, ImageDraw 

import base64
import datetime
import io

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
from generate_dataframe_functions import *
from graph_functions_dashboard import *
from working_with_dividends import *

#### Stocks ####
## Define stocks
stocks = ['FESA4','KLBN4','ITSA4','EGIE3','PETR4', 'FESA4','KLBN4']
stocks_request = [i+'.SA' for i in stocks] ## Necessary to do the request
stocks_buy_date = ['2020-06-02', '2020-06-02', '2020-06-02', '2020-06-02', '2020-06-02', '2020-06-10', '2020-12-10']


## Define time interval
today_str = date.today().strftime('%Y-%m-%d')
finish_day_str = today_str
start_day_str = '2020-06-02'

##Define invested value in each date
purchased_value_stocks = [110, 500, 1000, 1500, 750, 1300, 800]


## Getting input as DataFrame -- Should be imported
df_input_stocks = pd.DataFrame({'stock':stocks, 'stock_buy_date':stocks_buy_date, 'purchased_value':purchased_value_stocks})

#### Funds ####

###              TEST INFORMATION         ####


## Define stocks
funds = ['IRDM11','HGLG11','VILG11','MXRF11', 'MGFF11', 'VILG11', 'MGFF11']
funds_request = [i+'.SA' for i in funds] ## Necessary to do the request
funds_buy_date = ['2020-07-02', '2020-07-02', '2020-07-02', '2020-07-02', '2020-07-02', '2020-12-10', '2020-12-10']

## Define time interval
today_str = datetime.datetime.today().strftime('%Y-%m-%d')
finish_day_str = today_str
start_day_str = '2020-06-02'

##Define invested value in each date
purchased_value_funds = [400, 450, 650, 850, 1500, 850, 1500]


## Getting input as DataFrame -- Should be imported
df_input_funds = pd.DataFrame({'stock':funds, 'stock_buy_date':funds_buy_date, 'purchased_value':purchased_value_funds})

## Getting dividends
dividends = pd.read_csv('TESTE_1.csv')
dividends = pre_processing_dividends_file(dividends)
dict_funds = define_input_dict(df_input_funds)


####  FIXEd INCOME ###

fix_base = ['ipca', 'cdi', 'ipca']
fix_names = []
count_ipca = 0
count_cdi = 0
for i in range(len(fix_base)):
    if fix_base[i] == 'ipca':
        count_ipca = count_ipca + 1
        fix_names.append(fix_base[i] + ' fix ' + str(count_ipca))
    if fix_base[i] == 'cdi':
        count_cdi = count_cdi + 1
        fix_names.append(fix_base[i] + ' fix ' + str(count_cdi))


fix_buy_date = ['2020-06-01', '2020-07-02', '2020-08-01']
fix_buy_date_API_format = [datetime.datetime.strptime(i, "%Y-%m-%d").strftime("%d/%m/%Y") for i in fix_buy_date]

today_str = datetime.datetime.today().strftime('%Y-%m-%d')

purchased_value_fix = [12000, 4000, 6000]
fix_indexes = [1.2, 1.15, 1.12]


df_input_fix = pd.DataFrame({'base':fix_base, 'fix_buy_date':fix_buy_date, 
                         'fix_purchased_value':purchased_value_fix, 'fix_indexes':fix_indexes})

df_input_fix.set_index('fix_buy_date', inplace = True)

start_date = min(fix_buy_date_API_format)
finish_date = datetime.datetime.strptime(today_str, "%Y-%m-%d").strftime("%d/%m/%Y")
codes_dict = {'ipca':433, 'cdi':12}


### Dashboard variables

all_options = {
    'Ações': set(stocks),
    'Fundos Imobiliários': set(funds),
    'Renda Fixa': set(fix_names)}


logo = 'company_logo.png'
encoded_image_logo = base64.b64encode(open(logo, 'rb').read())

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([
    html.Div(html.Img(src='data:image/png;base64,{}'.format(encoded_image_logo.decode()),
    style={"margin-left": "40%","height":"80"}),style={'backgroundColor':'black'}),

    html.Div(html.H3('Acompanhe o desempenho da sua carteira!', style={"margin-left": "35%","color":"orange"}), style={'backgroundColor':'black'}),
    html.Hr(),
    html.Button('Atualizar Informações', id='update-infos'),
    html.Div(id='last-update-time', style={"margin-left": "1%","color":"#1f77b4"}),
    html.Hr(),
    html.Br(),
    html.H3('A performance geral da carteira',style={"margin-left": "40%","color":"orange"}),
    #html.Div(id='general-performance-table'),
    #html.Br(),
    #html.Hr(),
    ###
    html.Div([
        ## First column -- Ploting general portfolio information on a pie chart
        html.Div([
            html.H6('Performance Geral:', style={"margin-left": "5%"}),
            html.Br(),
            html.Div(id='general-performance-table'),
            html.Hr(),
            html.Img(id='portfolio-image', style={"margin-left": "20%"}),
            
            ], className="six columns"),
           
        ## Second Column -- Ploting general portfolio information on a pie chart
    html.Div([
            html.H6('Distribuição Geral', style={"margin-left": "5%"}),
            dcc.Graph(id='bar_chart_geral'), 
                                   
                ], className="six columns"),
                         ], className="row"),
    ###

    html.Hr(),
    html.Div(
         dcc.RadioItems(
                id='investment-type',
                options=[{'label': k, 'value': k} for k in all_options.keys()], 
                value='Ações',
                labelStyle={'display': 'inline-block', "margin-right": "30px"},
                style={"margin-left": "40%","color":"orange", "font-size": 25}
            ), style={'backgroundColor':'black'}),

    html.Hr(), 
   
    html.Div([
        ## First column -- Ploting general portfolio information on a pie chart
        html.Div([
            html.H6('Distribuição da carteira:', style={"margin-left": "5%"}),
            dcc.Graph(id='pie_chart'), 
            html.Hr(),
            ], className="six columns"),
           
        ## Second Column -- Ploting general portfolio information on a pie chart
        html.Div([
            html.H6('Performance dos Investimentos', style={"margin-left": "5%"}),
            dcc.Graph(id='bar_chart'), 
            html.Hr(),                        
                ], className="six columns"),
                         ], className="row"),


    html.Hr(),
    html.H3('A performance de cada investimento',style={"margin-left": "35%","color":"orange"}),
    html.Div([dcc.Dropdown(
                id='stock-fund',
                #options=[{'label':i, 'value':i} for i in set(stocks)],
                #value= stocks[0]
                ),              
                ]),
    html.Hr(),      
    html.Div([
        ## First column -- Ploting general portfolio information on a pie chart
        html.Div([
            #html.H6('Performance da ação', style={"margin-left": "5%"}),

            dcc.RadioItems(
                id='funds-dividends',
                options=[{'label': k, 'value': k} for k in ['Fund','Dividend']], 
                value='Fund',
                labelStyle={'display': 'inline-block', "margin-right": "30px"},
                #style={'display':'none'}
            ),

            dcc.Graph(id='line_chart'),
            ], className="six columns"),

            
        ## Second Column -- Ploting general portfolio information on a pie chart
        html.Div([
                html.H6('Dados da performance da ação', style={"margin-left": "5%"}),
                html.Div(id='stock-performance-table'),  
                html.Hr(),
                html.Img(id='stock-image', style={"margin-left": "20%"}),                                 
                ], className="six columns"),
                         ], className="row"),

    html.Div(id='stores-df_final_stocks', style={'display': 'none'}),
    html.Div(id='stores-df_final_funds', style={'display': 'none'}),
    html.Div(id='stores-df_dividends', style={'display': 'none'}),
    html.Div(id='stores-df_final_fix', style={'display': 'none'}),
   
    
    html.Hr(),

], style={'backgroundColor': '#111111'})


@app.callback(
    dash.dependencies.Output('funds-dividends', 'style'),
    [dash.dependencies.Input('investment-type', 'value')])
def define_display_funds(investment_type):
    if investment_type != 'Fundos Imobiliários':
        return({'display':'none'})
    else:
        return({"margin-left": "10%","color":"orange", "font-size": 15})
    


@app.callback(
    dash.dependencies.Output('stock-fund', 'options'),
    dash.dependencies.Output('stock-fund', 'value'),
    [dash.dependencies.Input('investment-type', 'value')])
def set_cities_options(investment_type):
    if investment_type == 'Ações':
        start_value = stocks[0] 
    if investment_type == 'Fundos Imobiliários':
        start_value = funds[0] 
    if investment_type == 'Renda Fixa':
        start_value = fix_names[0] 

    return ([{'label': i, 'value': i} for i in all_options[investment_type]], start_value)


@app.callback(
    dash.dependencies.Output('general-performance-table', 'children'),
    dash.dependencies.Output('bar_chart_geral', 'figure'),
    dash.dependencies.Output('stores-df_final_stocks', 'children'),
    dash.dependencies.Output('stores-df_final_funds', 'children'),
    dash.dependencies.Output('stores-df_dividends', 'children'),
    dash.dependencies.Output('stores-df_final_fix', 'children'),
    dash.dependencies.Output('portfolio-image', 'src'),
    [dash.dependencies.Input('update-infos', 'n_clicks')])     
def update_information_and_plot_general_table(n_clicks):
    ## Stocks ##
    df_final_stocks, performance_info_stocks = pipeline_and_performance_info(df_input_stocks)
 
    ## Funds ##
    df_final_funds, performance_info_funds = pipeline_and_performance_info(df_input_funds)
    df_dividends = pipeline_dividends(df_final_funds, dividends, dict_funds)

    df_final_fix = calculate_fix_dataframe(start_date, finish_date, codes_dict, df_input_fix)


    performance_info_fix = calculate_performance_fix(df_final_fix)

    all_investments = pd.concat([pd.DataFrame([performance_info_stocks], index = ['stocks']), 
                                pd.DataFrame([performance_info_funds], index = ['funds']),
                                pd.DataFrame([performance_info_fix], index = ['fix'])])

    invested_percentual = all_investments['total_invested_value'].apply(lambda x: x /all_investments['total_invested_value'].sum())
    profit_percentual = all_investments['profit'].apply(lambda x: x /all_investments['profit'].sum())
    
    options=['Ações', 'Fundos Imobiliários', 'Renda Fixa']

    portfolio_dist_fig = plot_portfolio_distribution(invested_percentual, profit_percentual, options)

    total_invested_value = all_investments['total_invested_value'].sum()
    total_accumulated_value_valorization = all_investments['total_accumulated_value'].sum()
    total_accumulated_value_dividends = get_all_acumulated_dividends(df_dividends)
    total_accumulated_value = total_accumulated_value_valorization + total_accumulated_value_dividends
    total_yeld = ((total_accumulated_value / total_invested_value) - 1) * 100
    profit = total_accumulated_value - total_invested_value

    table_all = plot_performance_table(round(total_invested_value,2), 
                                    round(total_accumulated_value,2), 
                                    round(total_yeld,2), 
                                    round(profit,2), total_accumulated_value_dividends, 'GERAL')

    write_profit_in_image('portfolio', round(profit,2))
    encoded_image = base64.b64encode(open('image_display_portfolio.png', 'rb').read())

    return(table_all, portfolio_dist_fig, 
            df_final_stocks.to_json(date_format='iso', orient='split'), 
            df_final_funds.to_json(date_format='iso', orient='split'),
            df_dividends.to_json(date_format='iso', orient='split'), 
            df_final_fix.to_json(date_format='iso', orient='split'),
           'data:image/png;base64,{}'.format(encoded_image.decode()))


@app.callback(
    dash.dependencies.Output('pie_chart', 'figure'),
    [dash.dependencies.Input('stores-df_final_stocks', 'children')],
    [dash.dependencies.Input('stores-df_final_funds', 'children')],
    [dash.dependencies.Input('stores-df_final_fix', 'children')],
    [dash.dependencies.Input('update-infos', 'n_clicks')],
    [dash.dependencies.Input('investment-type', 'value')])   
def print_pie_chart(df_final_stocks_json, df_final_funds_json, df_final_fix_json,  n_cliks, investment_type):
    #if n_clicks != None:
    if investment_type == 'Ações':
        df_final = pd.read_json(df_final_stocks_json, orient='split')
        df_last_day = df_final[df_final.index.isin([max(df_final.index)])]  ## Gets the last day of all stocks 
    elif investment_type == 'Fundos Imobiliários':
        df_final = pd.read_json(df_final_funds_json, orient='split')
        df_last_day = df_final[df_final.index.isin([max(df_final.index)])]  ## Gets the last day of all stocks 
    elif investment_type == 'Renda Fixa':
        fix_final = pd.read_json(df_final_fix_json, orient='split')
        grouped_fix = fix_final.groupby('Stock')

        fix_last_day_list = []
        for i in fix_final['Stock'].unique():
            df = grouped_fix.get_group(i)
            fix_last_day_list.append(df[df.index.isin([max(df.index)])])
        df_last_day = pd.concat(fix_last_day_list)

    
    fig = plot_pie_graph(df_last_day)

    return fig


@app.callback(
    dash.dependencies.Output('bar_chart', 'figure'),
    Output('last-update-time', 'children'),
    [dash.dependencies.Input('stores-df_final_stocks', 'children')],
    [dash.dependencies.Input('stores-df_final_funds', 'children')],
    [dash.dependencies.Input('stores-df_final_fix', 'children')],
    [dash.dependencies.Input('update-infos', 'n_clicks')],
     [dash.dependencies.Input('investment-type', 'value')])    
def print_bar_chart(df_final_stocks_json, df_final_funds_json,df_final_fix_json, n_clicks, investment_type):
    #if n_clicks != None:

    if investment_type == 'Ações':
        df_final = pd.read_json(df_final_stocks_json, orient='split')
        df_last_day = df_final[df_final.index.isin([max(df_final.index)])]  ## Gets the last day of all stocks 

    elif investment_type == 'Fundos Imobiliários':
        df_final = pd.read_json(df_final_funds_json, orient='split')
        df_last_day = df_final[df_final.index.isin([max(df_final.index)])]  ## Gets the last day of all stocks 

    elif investment_type == 'Renda Fixa':
        fix_final = pd.read_json(df_final_fix_json, orient='split')
        grouped_fix = fix_final.groupby('Stock')

        fix_last_day_list = []
        for i in fix_final['Stock'].unique():
            df = grouped_fix.get_group(i)
            fix_last_day_list.append(df[df.index.isin([max(df.index)])])
        df_last_day = pd.concat(fix_last_day_list)

    
    fig = all_performances(df_last_day)

    now = datetime.datetime.now()
    day = str(now).split(' ')[0]
    time = str(now).split(' ')[1].split('.')[0]

    return (fig, 'Última atualização feita no dia ' + day + ' às ' + time)


@app.callback(
    dash.dependencies.Output('line_chart', 'figure'),
    [dash.dependencies.Input('funds-dividends', 'value')],
    [dash.dependencies.Input('stock-fund', 'value')],
    [dash.dependencies.Input('stores-df_final_stocks', 'children')],
    [dash.dependencies.Input('stores-df_final_funds', 'children')],
    [dash.dependencies.Input('stores-df_dividends', 'children')],
     [dash.dependencies.Input('stores-df_final_fix', 'children')],
    [dash.dependencies.Input('update-infos', 'n_clicks')],
     [dash.dependencies.Input('investment-type', 'value')])   
def print_performance_stock(fund_dividend, stock_fund, df_final_stocks_json, df_final_funds_json, df_dividends_json,  df_final_fix_json, n_cliks, investment_type):
    #if n_clicks != None:   
    if investment_type == 'Ações':
        df_final = pd.read_json(df_final_stocks_json, orient='split')       

    elif investment_type == 'Fundos Imobiliários':
        df_final = pd.read_json(df_final_funds_json, orient='split') 
        if fund_dividend == 'Dividend': 
            df_dividends = pd.read_json(df_dividends_json, orient='split')    
            return( plot_dividends_performance(stock_fund, df_final[df_final['Stock']==stock_fund],
                 df_dividends[df_dividends['Fund'] == stock_fund]))
        
    elif investment_type == 'Renda Fixa':
        df_final = pd.read_json(df_final_fix_json, orient='split')

    grouped_stocks = df_final.groupby('Stock')
    df_stock = grouped_stocks.get_group(stock_fund)
    fig = plot_stock_performance(stock_fund, df_stock)
    return fig
  


@app.callback(
    dash.dependencies.Output('stock-performance-table', 'children'),
    dash.dependencies.Output('stock-image', 'src'),
    [dash.dependencies.Input('stock-fund', 'value')],
    [dash.dependencies.Input('stores-df_final_stocks', 'children')],
    [dash.dependencies.Input('stores-df_final_funds', 'children')],
    [dash.dependencies.Input('stores-df_dividends', 'children')],
    [dash.dependencies.Input('stores-df_final_fix', 'children')],
    [dash.dependencies.Input('update-infos', 'n_clicks')],
    [dash.dependencies.Input('investment-type', 'value')])    
def stock_table(stock_fund, df_final_stocks_json, df_final_funds_json,df_dividends_json, df_final_fix_json, n_clicks, investment_type):


    if investment_type == 'Ações':
        df_final = pd.read_json(df_final_stocks_json, orient='split')
    elif investment_type == 'Fundos Imobiliários':
        df_final = pd.read_json(df_final_funds_json, orient='split')
        df_dividends = pd.read_json(df_dividends_json, orient='split')
    

    elif investment_type == 'Renda Fixa':
        df_final = pd.read_json(df_final_fix_json, orient='split')

        
    grouped_stocks = df_final.groupby('Stock')
    df_stock = grouped_stocks.get_group(stock_fund) ## Get a DataFrame only containing this stock
    stock_last_day = df_stock.loc[max(df_stock.index)] ## Get last day of this stocl data frame


    ## Calculate the required information
    total_invested_value_stock = stock_last_day['Total Invested']    
    total_accumulated_value_stock = stock_last_day['Accumulated Value']

    if investment_type == 'Fundos Imobiliários':
        total_accumulated_value_dividends = get_acumulated_dividend(df_dividends, stock_fund)
        total_yeld_stock = (((total_accumulated_value_stock + total_accumulated_value_dividends) / total_invested_value_stock) - 1) * 100
        profit_stock = total_accumulated_value_stock + total_accumulated_value_dividends - total_invested_value_stock

    if investment_type in ['Ações', 'Renda Fixa']:
        total_yeld_stock = ((total_accumulated_value_stock / total_invested_value_stock) - 1) * 100
        profit_stock = total_accumulated_value_stock - total_invested_value_stock
        total_accumulated_value_dividends = 0.0

    table = plot_performance_table(round(total_invested_value_stock,2), round(total_accumulated_value_stock,2), 
                        round(total_yeld_stock,2), round(profit_stock,2),  
                            round(total_accumulated_value_dividends,2), investment_type)

    write_profit_in_image('stock', round(profit_stock,2))
    encoded_image = base64.b64encode(open('image_display_stock.png', 'rb').read())

    return(table,  'data:image/png;base64,{}'.format(encoded_image.decode()))



if __name__ == '__main__':
    app.run_server(debug=True)