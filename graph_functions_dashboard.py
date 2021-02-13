import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas_datareader import data as pdr
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import dash_table as dt
from plotly.subplots import make_subplots
from PIL import Image, ImageFont, ImageDraw
#-----------------------#----------------------#-----------------------#----------------------

## This funtion plots the general info of the portfolio in a pie chart
def plot_pie_graph(df_last_day):
    fig = go.Figure(data=[go.Pie(labels=df_last_day['Stock'], values=df_last_day['Total Invested'])])
    return(fig)
    
#-----------------------#----------------------#-----------------------#----------------------

## This function plots the performance of all stocks in the last day
def all_performances(df_last_day):
    fig = px.bar(df_last_day, x='Stock', y='Your Current Yeld (%)', color="Total Invested",
             hover_data=['Total Invested'])             
    return(fig)

#-----------------------#----------------------#-----------------------#----------------------

## This function plots the stock performance of a given stock dataframe
def plot_stock_performance(stock_name, df_stock):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_stock.index, y=df_stock["Accumulated Value"],
                        mode='lines+markers',
                        name='Valor Acumulado'))
    fig.add_trace(go.Scatter(x=df_stock.index, y=df_stock['Total Invested'],
                        mode='lines',
                        name='Valor Investido'))

    fig.update_layout(title='Performance da ação ' + stock_name,
                       xaxis_title='Data',
                       yaxis_title='Valor em R$')

    return(fig)

    #-----------------------#----------------------#-----------------------#----------------------

    # This function plots the main information as a table. It can be general info about the portfolio
    # or about a stock in specific
def plot_performance_table(total_invested_value,total_accumulated_value,total_yeld, profit, 
                            total_accumulated_value_dividends, investment_type):

    if investment_type in ['Ações' , 'Renda Fixa', 'GERAL']:       

        table_show = pd.DataFrame({'Total Investido (R$)':[round(total_invested_value,2)],
                                'Total Acumulado (R$)':[round(total_accumulated_value,2)],
                                'Rendimento Total (%)':[round(total_yeld,2)], 'Lucro (R$)':[round(profit,2)]})
        data = table_show.to_dict('rows')
        columns = [{"name": i, "id": i, "editable": False} for i in (table_show.columns)]

        table = dt.DataTable(data=data, columns=columns,
                    style_data_conditional=[{'if': {'row_index': 'odd'},'backgroundColor': 'rgb(255, 128, 0)'}],
                    style_header={'border': '2px solid black', 'backgroundColor': 'rgb(255, 128, 0)'},
                     style_cell={'textAlign': 'center',  "font-size": 16, 'whiteSpace': 'normal', 'height': 'auto'})
        
        return(table)
    
    if investment_type == 'Fundos Imobiliários':
        table_show = pd.DataFrame({'Total Investido (R$)':[round(total_invested_value,2)],
                                'Total Valorização (R$)':[round(total_accumulated_value,2)],
                                'Total Dividendos (R$)':[round(total_accumulated_value_dividends,2)],
                                'Total Acumulado (R$)':[round(total_accumulated_value +total_accumulated_value_dividends,2)],
                                'Rendimento Total (%)':[round(total_yeld,2)], 
                                'Lucro (R$)':[round(profit,2)]})
        data = table_show.to_dict('rows')
        columns = [{"name": i, "id": i, "editable": False} for i in (table_show.columns)]

        table = dt.DataTable(data=data, columns=columns,
                    style_data_conditional=[{'if': {'row_index': 'odd'},'backgroundColor': 'rgb(255, 128, 0)'}],
                    style_header={'border': '2px solid black', 'backgroundColor': 'rgb(255, 128, 0)'},
                    style_cell={'textAlign': 'center',  "font-size": 16, 'whiteSpace': 'normal', 'height': 'auto'})
                   
        
        return(table)



 #-----------------------#----------------------#-----------------------#----------------------
 
    ## This function is used to write information in an Image. It recieves the values and writes eather in the stock image
## or in the general one.

def write_profit_in_image(option, profit):

    font = ImageFont.truetype("calibri.ttf", 34)
    write_text = 'R$ ' + str(profit)

    if option == 'portfolio':
        background_image = Image.open('image_portfolio_performance' + ".png")
        y_location = 80
        name_file = 'image_display_portfolio'
    elif option == 'stock':
        background_image = Image.open('image_stock_performance' + ".png")
        y_location = 105
        name_file = 'image_display_stock'

    width, height = background_image.size
    image_editable = ImageDraw.Draw(background_image)
    w, h = image_editable.textsize(write_text)
  
    image_editable.text(((width - 2.5*w)/2,y_location), write_text, (0, 0, 0), font = font)
    background_image.save(name_file + ".png")


#-----------------------#----------------------#-----------------------#----------------------

def plot_portfolio_distribution(invested_percentual, profit_percentual, options):
    
    fig = go.Figure(data=[
        go.Bar(name='Percentual da Carteira (%)', x=options, y=round(invested_percentual,2) * 100, 
               text =round(invested_percentual * 100,2), textposition='auto'),
        go.Bar(name='Percentual do Lucro (%)', x=options, y=round(profit_percentual * 100,2),
        text =round(profit_percentual * 100,2), textposition='auto')
        ])

    # Change the bar mode
    fig.update_layout(barmode='group')
    fig.update_layout(
    yaxis_title="Percentual do portfólio")
    
    return(fig)


#-----------------------#----------------------#-----------------------#----------------------

def plot_dividends_performance(fund_name, df_fund, df_dividends):
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Bar(x=df_dividends.index, 
                            y=df_dividends["Dividends Recieve"],
                            #mode='lines+markers',
                            name='Dividendos Recebidos'))
    fig.add_trace(go.Scatter(x=df_dividends.index, 
                            y=df_dividends['Acumulated Dividends'],
                            mode='lines',
                            name='Dividendos Acumulados'))

    fig.add_trace(go.Scatter(x=df_fund.index, 
                            y=df_fund['Total Invested'],
                            mode='lines',
                            name='Total Investido'),
                            secondary_y=True)

    fig.update_layout(title='Performance Dividendos de ' + fund_name,
                           xaxis_title='Data',
                           yaxis_title='Valor em R$')

    fig.update_yaxes(title_text="Valor Recebido e Acumulado em Dividendo (R$)", secondary_y=False)
    fig.update_yaxes(title_text="Valor Investido (R$)", secondary_y=True)

    return(fig)