import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas_datareader import data as pdr
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
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
def plot_stock_performance(df_stock):
    stock_name = df_stock.iloc[0]['Stock']

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
    def plot_performance_table(total_invested_value,total_accumulated_value,total_yeld, profit):
    
        fig = go.Figure(data=[go.Table(
            header=dict(values=['Total Investido (R$)', 'Total Acumulado (R$)', 'Rendimento Total (%)', 'Lucro (R$)'],
                        line_color='darkslategray',
                        fill_color='orange',
                        align='center'),
            cells=dict(values=[[total_invested_value], # 1st column
                            [total_accumulated_value], # 2nd column
                            [total_yeld], # 3rd columns
                            [[profit]]], # 4th column

                    line_color='darkslategray',
                    fill_color='lightcyan',
                    align='center'))
        ])

        fig.update_layout(width=700, height=300)
        return(fig)


 #-----------------------#----------------------#-----------------------#----------------------
 
    ## This function is used to write information in an Image. It recieves the values and writes eather in the stock image
## or in the general one.

def write_information_in_image_general(total_invested_value, total_accumulated_value, total_yeld, profit, pic_name):
    
    font = ImageFont.truetype("calibri.ttf", 30)
    
    ## The values are transformed into strings, so that they can be writen in the image.
    
    total_invested_value_str = "R$ " + str(round(total_invested_value,2))
    total_accumulated_value_str = "R$ " + str(round(total_accumulated_value,2))
    total_yeld_str = str(round(total_yeld,2)) + '%'
    profit_str = "R$ " + str(round(profit,2))
    
    
    ## General Picture
    if pic_name == 'picture_general_results':
    
        background_image = Image.open(pic_name + ".png")

        image_editable = ImageDraw.Draw(background_image)

        image_editable.text((75,65), total_yeld_str, (0, 0, 0), font = font)
        image_editable.text((200,65), total_invested_value_str, (0, 0, 0), font = font)
        image_editable.text((385,65), total_accumulated_value_str, (0, 0, 0), font = font)
        image_editable.text((565,65), profit_str, (0, 0, 0), font = font)


        background_image.save("image_display.png") 

    ## Stock Picture
    elif pic_name == 'picture_general_results_stock':

        background_image = Image.open(pic_name + ".png")

        image_editable = ImageDraw.Draw(background_image)

        image_editable.text((75,65), total_yeld_str, (0, 0, 0), font = font)
        image_editable.text((200,65), total_invested_value_str, (0, 0, 0), font = font)
        image_editable.text((40,185), total_accumulated_value_str, (0, 0, 0), font = font)
        image_editable.text((210,185), profit_str, (0, 0, 0), font = font)


    background_image.save("image_display_stock.png")