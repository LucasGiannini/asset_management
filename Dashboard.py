
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
from data_base_connection import *
import ast




## Getting dividends. The CSV file was created by the web scraping file
dividends = pd.read_csv('TESTE_1.csv')

## Some data processing is done in the dividends table
dividends = pre_processing_dividends_file(dividends)


today_str = datetime.datetime.today().strftime('%Y-%m-%d')

## This codes are necessary to relate to each one of the indexes for the Central Bank API
codes_dict = {'ipca':433, 'cdi':12} 



##--------------------##--------------------##--------------------##--------------------##--------------------
## FASE DE TESTES APENAS -- Ja pedindo as dados na base de dados
#df_input_stocks, df_input_funds, df_input_fix = data_base_client_input_info('test')

#df_final_stocks, df_final_funds, df_final_fix = data_base_client_performace_info('test')


#possible_stocks = df_input_stocks['stock'].unique()
#possible_funds = df_input_funds['stock'].unique()
#possible_fix = df_final_fix['Stock'].unique()


### Dashboard variables
#all_options = {
#    'Ações': possible_stocks,
#    'Fundos Imobiliários': possible_funds,
#    'Renda Fixa': possible_fix}

## The company's logo s loaded to be displayed in the dashboard.
logo = 'company_logo.png'
encoded_image_logo = base64.b64encode(open(logo, 'rb').read())

## A CSS is defined
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


## Staring the DashBoard code.
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([
    ## IMAGE AND TOP BANNER
    html.Div(html.Img(src='data:image/png;base64,{}'.format(encoded_image_logo.decode()),
    style={"height":"80"}),style={'backgroundColor':'black', "textAlign": "center"}),

    html.Div(html.H3('Acompanhe o desempenho da sua carteira!', style={"textAlign": "center","color":"orange"})),
    html.Hr(),

    ## UPDATE INFOS BUTTON
    html.Button('Atualizar Informações', id='update-infos'),
    html.Div(id='last-update-time', style={"margin-left": "1%","color":"#1f77b4"}),
    html.Hr(),
    html.Div(
     dcc.Loading(
                    id="loading",
                    #children=[html.Div([html.Div(id="start")])],
                    fullscreen =  False,
                    type="cube",
                    loading_state={'is_loading':True},
                    #style={"margin-left": "20%"},
                    color = "orange"
                ), style={"textAlign": "center"}),

    html.Br(),
    html.H3('A performance geral da carteira',style={"textAlign": "center","color":"orange"}),

    html.Div([
        ## First column -- PLOTTING GENERAL PORTFOLIO PERFORMANCE IN THE TABLE
        html.Div([
            html.H6('Performance Geral:', style={"margin-left": "5%"}),
            html.Br(),
            html.Div(id='general-performance-table'),
            html.Hr(),
            ##PLOTTING IMAGE WITH PROFIT IMFORMATION
            html.Img(id='portfolio-image', style={"margin-left": "20%"}),
            
            ], className="six columns"),
           
        ## Second Column -- PLOTTING GENERAL PORTFOLIO PERFORMANCE IN BAR CHART
    html.Div([
            html.H6('Distribuição Geral', style={"margin-left": "5%"}),
            dcc.Graph(id='bar_chart_geral'), 
                                   
                ], className="six columns"),
                         ], className="row"),
    ###
    ## SECOND ROW OF DASHBOARD
    html.Hr(),
    html.Div(
        ## RADIOITEM TO CHOOSE INVESTMENT TYPE (STOCKS, FUNDS, FIXED)
         dcc.RadioItems(
                id='investment-type',
                options=[{'label': k, 'value': k} for k in ['Ações', 'Fundos Imobiliários', 'Renda Fixa']], 
                value='Ações',
                labelStyle={'display': 'inline-block', "margin-right": "30px"},
                style={"textAlign": "center","color":"orange", "font-size": 25}
            ), style={'backgroundColor':'black'}),

    html.Hr(), 
   
   ## THIRD ROW OF DASHBOARD
    html.Div([
        ## First column -- PLOTTING PIE CHART WITH CHOSEN INVESTMENT DISTRIBUTION
        html.Div([
            html.H6('Distribuição da carteira:', style={"margin-left": "5%"}),
            dcc.Graph(id='pie_chart'), 
            html.Hr(),
            ], className="six columns"),
           
        ## Second Column -- PLOTTING BAR CHART WITH CHOSEN INVESTMENT PERFORMANCE
        html.Div([
            html.H6('Performance dos Investimentos', style={"margin-left": "5%"}),
            dcc.Graph(id='bar_chart'), 
            html.Hr(),                        
                ], className="six columns"),
                         ], className="row"),

    ## FOURTH ROW OF DASHBOARD 
    html.Hr(),
    html.H3('A performance de cada investimento',style={"textAlign": "center","color":"orange"}),
    ## DROP DOWN TO CHOOSE STOCK/FUND/FIX VALUE
    html.Div([dcc.Dropdown(
                id='stock-fund',
                #options=[{'label':i, 'value':i} for i in set(stocks)],
                #value= stocks[0]
                ),              
                ]),
    html.Hr(),      
    html.Div([
        ## First column -- PLOTTING LINE CHART OF VALUE CHOSEN IN DROP DOWN
        html.Div([
            
            ## Only displayed if FIXED is chosen in Radio Item 
            html.Div(
            dcc.RadioItems(
                id='funds-dividends',
                options=[{'label': k, 'value': k} for k in ['Fund','Dividend']], 
                value='Fund',
                labelStyle={'display': 'inline-block', "margin-right": "30px"},
                #style={'display':'none'}
            ),style={'backgroundColor':'black', "textAlign": "center"}),
            ## LINE CHART FOR STOCK/FUND/FIXED
            dcc.Graph(id='line_chart'),
            ], className="six columns"),

            
        ## Second Column -- PLOTTING STOCK/FUND/FIXED PERFORMANCE INFRMATION IN LINE CHART
        html.Div([
                html.H6('Dados da performance da ação', style={"margin-left": "5%"}),
                html.Div(id='stock-performance-table'),  
                html.Hr(),
                html.Img(id='stock-image', style={"margin-left": "20%"}),                                 
                ], className="six columns"),
                         ], className="row"),

    ## DIVS USED TO STORE INFORMATION WHICH IS COMPUTED ONLY ONCE AND TRNAMITED AMONG THE CALLBACKS
    html.Div(id='stores-df_final_stocks', style={'display': 'none'}),
    html.Div(id='stores-df_final_funds', style={'display': 'none'}),
    html.Div(id='stores-df_dividends', style={'display': 'none'}),
    html.Div(id='stores-df_final_fix', style={'display': 'none'}),

    html.Div(id='stores-df_last_day_stocks', style={'display': 'none'}),
    html.Div(id='stores-df_last_day_funds', style={'display': 'none'}),
    html.Div(id='stores-df_last_day_fix', style={'display': 'none'}),

    html.Div(id='stores-all_options', style={'display': 'none'}),   
    
    html.Hr(),

])

## CALLBACK RESPONSIBLE FOR DISPLAYING FUND | DIVIDEND RADIOITEM, IF FUNDS ARE CHOSEN AS INVESTMENT TYPE
@app.callback(
    dash.dependencies.Output('funds-dividends', 'style'),
    [dash.dependencies.Input('investment-type', 'value')])
def display_radio_item_funds(investment_type):
    if investment_type != 'Fundos Imobiliários':
        return({'display':'none'})
    else:
        return({"margin-left": "10%","color":"orange", "font-size": 15})
    

## CALLBACK WHICH ADJUSTS DROP DOWN VALUES ACCORDING TO THE INVESTMENT TYPE CHOSEN IN THE RADIOITEM
@app.callback(
    dash.dependencies.Output('stock-fund', 'options'),
    dash.dependencies.Output('stock-fund', 'value'),
    [dash.dependencies.Input('investment-type', 'value')],
    [dash.dependencies.Input('stores-all_options', 'children')])
def set_options(investment_type, all_options):

    all_options = ast.literal_eval(all_options)

    if investment_type == 'Ações':
        possible_stocks = all_options['Ações']
        start_value = possible_stocks[0] 
    elif investment_type == 'Fundos Imobiliários':
        possible_funds = all_options['Fundos Imobiliários']
        start_value = possible_funds[0] 
    elif investment_type == 'Renda Fixa':
        possible_fix = all_options['Renda Fixa']
        start_value = possible_fix[0] 

    return ([{'label': i, 'value': i} for i in all_options[investment_type]], start_value)

## CALLBACK RESPONSIBLE FOR GETTING THE HISTORICAL DATA FROM THE DATABASE, ORGANIZING THE DIVIDNDS AND COMPUTING GENERAL PERFORMANCE
## THE INFORMATION IS PLOTED IN THE TABLE, BAR CHART AND IMAGE
## THE DATAFRAMES GOTTEN FROM THE DATABASE ARE SAVED IN THE DIVS, SO THAT THEY CAN BE USED IN OTHER CALLBACKS
@app.callback(
    dash.dependencies.Output('general-performance-table', 'children'),
    dash.dependencies.Output('bar_chart_geral', 'figure'),
    dash.dependencies.Output('stores-df_final_stocks', 'children'),
    dash.dependencies.Output('stores-df_final_funds', 'children'),
    dash.dependencies.Output('stores-df_dividends', 'children'),
    dash.dependencies.Output('stores-df_final_fix', 'children'),
    dash.dependencies.Output('stores-df_last_day_stocks', 'children'),
    dash.dependencies.Output('stores-df_last_day_funds', 'children'),
    dash.dependencies.Output('stores-df_last_day_fix', 'children'),
    dash.dependencies.Output('portfolio-image', 'src'),
    dash.dependencies.Output('loading', 'children'),
    dash.dependencies.Output('stores-all_options', 'children'),
    [dash.dependencies.Input('update-infos', 'n_clicks')])     
def computing(n_clicks):
    
    ## We get the historical information of the clients investments stored in the data base 
    ## already done in the beginning of the app
    df_final_stocks, df_final_funds, df_final_fix = data_base_client_performace_info('test')

    df_input_stocks, df_input_funds, df_input_fix = data_base_client_input_info('test')

    ## These are necessary to be shown as possible dropdown values. We create the all_options dictionary, which will be stored in a Div as
    ## a string, and later transfrmed into a dictionary
    possible_stocks = list(df_final_stocks['Stock'].unique())
    possible_funds = list(df_final_funds['Stock'].unique())
    possible_fix = list(df_final_fix['Stock'].unique())

    all_options = str({'Ações': possible_stocks,'Fundos Imobiliários': possible_funds,'Renda Fixa': possible_fix})

    ## We calculate the key performance indicators of each investment type
    performance_info_stocks = performance_info(df_final_stocks, 'stocks')
    performance_info_funds = performance_info(df_final_funds, 'funds')
    performance_info_fix = performance_info(df_final_fix, 'fix')
 
    ## It is important to remember that FUNDS have also dividends to be considered    
    df_dividends = pipeline_dividends(df_final_funds, dividends, define_input_dict(df_input_funds))

   ## It is necessary to add the dividends performance to the funds performance
    performance_info_funds_and_dividends = performance_info_funds
    total_accumulated_value_dividends = get_all_acumulated_dividends(df_dividends)
    performance_info_funds_and_dividends['total_accumulated_value'] = performance_info_funds['total_accumulated_value'] + total_accumulated_value_dividends
    performance_info_funds_and_dividends['profit'] = performance_info_funds_and_dividends['total_accumulated_value'] - performance_info_funds_and_dividends['total_invested_value']
    performance_info_funds_and_dividends['total_yeld'] = (performance_info_funds_and_dividends['profit'] / performance_info_funds_and_dividends['total_invested_value']) * 100



    all_investments = pd.concat([pd.DataFrame([performance_info_stocks], index = ['stocks']), 
                                pd.DataFrame([performance_info_funds_and_dividends], index = ['funds']),
                                pd.DataFrame([performance_info_fix], index = ['fix'])])


    ## Some information of the overall performance is computed 
    invested_percentual = all_investments['total_invested_value'].apply(lambda x: x /all_investments['total_invested_value'].sum())
    profit_percentual = all_investments['profit'].apply(lambda x: x /all_investments['profit'].sum())
    
    ## Plot bar chart of investments distributions and respective profits
    options=['Ações', 'Fundos Imobiliários', 'Renda Fixa']
    portfolio_dist_fig = plot_portfolio_distribution(invested_percentual, profit_percentual, options)

    ## information to be displayed in general performance table 
    total_invested_value = all_investments['total_invested_value'].sum()
    total_accumulated_value = all_investments['total_accumulated_value'].sum()
    profit = total_accumulated_value - total_invested_value
    total_yeld = (profit / total_invested_value) * 100

    ## Plot general performance table
    table_all = plot_performance_table(round(total_invested_value,2), 
                                    round(total_accumulated_value,2), 
                                    round(total_yeld,2), 
                                    round(profit,2), total_accumulated_value_dividends, 'GERAL')

    ## Writing profit in displayed image
    write_profit_in_image('portfolio', round(profit,2))
    encoded_image = base64.b64encode(open('image_display_portfolio.png', 'rb').read())

    ## THE LAST_DAY DATAFRAMES ARE ALSO COMPUTED, SO THAT THEY CAN BE USED IN OTHER CALLBACKS
    df_last_day_stocks = df_final_stocks[df_final_stocks.index.isin([max(df_final_stocks.index)])]  ## Gets the last day of all stocks 
    df_last_day_funds = df_final_funds[df_final_funds.index.isin([max(df_final_funds.index)])]  ## Gets the last day of all funds 

    grouped_fix = df_final_fix.groupby('Stock')

    fix_last_day_list = []
    for i in possible_fix:  ## Gets the last day of all fix
        df = grouped_fix.get_group(i)
        fix_last_day_list.append(df[df.index.isin([max(df.index)])])
    df_last_day_fix = pd.concat(fix_last_day_list)

    return(table_all, portfolio_dist_fig, 
            df_final_stocks.to_json(date_format='iso', orient='split'), 
            df_final_funds.to_json(date_format='iso', orient='split'),
            df_dividends.to_json(date_format='iso', orient='split'), 
            df_final_fix.to_json(date_format='iso', orient='split'),
            df_last_day_stocks.to_json(date_format='iso', orient='split'),
            df_last_day_funds.to_json(date_format='iso', orient='split'),
            df_last_day_fix.to_json(date_format='iso', orient='split'),
           'data:image/png;base64,{}'.format(encoded_image.decode()),
           ' ',
           all_options)


## CALLBACK RESPONSIBLE FOR PRINTING THE INVESTMENTS DISTRIBUTION IN A PIE CHART
@app.callback(
    dash.dependencies.Output('pie_chart', 'figure'),
    [dash.dependencies.Input('stores-df_last_day_stocks', 'children')],
    [dash.dependencies.Input('stores-df_last_day_funds', 'children')],
    [dash.dependencies.Input('stores-df_last_day_fix', 'children')],
    [dash.dependencies.Input('update-infos', 'n_clicks')],
    [dash.dependencies.Input('investment-type', 'value')])   
def print_pie_chart(df_last_day_stocks_json, df_last_day_funds_json, df_last_day_fix_json,  n_cliks, investment_type):
    #if n_clicks != None:
    if investment_type == 'Ações':
        df_last_day = pd.read_json(df_last_day_stocks_json, orient='split')
    elif investment_type == 'Fundos Imobiliários':
        df_last_day = pd.read_json(df_last_day_funds_json, orient='split')
    elif investment_type == 'Renda Fixa':
       
        df_last_day = pd.read_json(df_last_day_fix_json, orient='split')

    
    fig = plot_pie_graph(df_last_day)

    return fig


## CALLBACK RESPONSIBLE FOR PRINTING THE INVESTMENTS DISTRIBUTION IN A BAR CHART
@app.callback(
    dash.dependencies.Output('bar_chart', 'figure'),
    Output('last-update-time', 'children'),
    [dash.dependencies.Input('stores-df_last_day_stocks', 'children')],
    [dash.dependencies.Input('stores-df_last_day_funds', 'children')],
    [dash.dependencies.Input('stores-df_last_day_fix', 'children')],
    [dash.dependencies.Input('update-infos', 'n_clicks')],
     [dash.dependencies.Input('investment-type', 'value')])    
def print_bar_chart(df_last_day_stocks_json, df_last_day_funds_json, df_last_day_fix_json, n_clicks, investment_type):
    #if n_clicks != None:

    if investment_type == 'Ações':
        df_last_day = pd.read_json(df_last_day_stocks_json, orient='split')

    elif investment_type == 'Fundos Imobiliários':
        df_last_day = pd.read_json(df_last_day_funds_json, orient='split')

    elif investment_type == 'Renda Fixa':
        df_last_day = pd.read_json(df_last_day_fix_json, orient='split')
    
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
    stock_last_day = df_stock.loc[max(df_stock.index)] ## Get last day of this stock data frame

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