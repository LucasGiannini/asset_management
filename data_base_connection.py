import pymongo
from pymongo import MongoClient
import pandas as pd

## Let us first set the connection

def data_base_client_performace_info(client):

    ## Let us first set the connection
    cluster = MongoClient('mongodb+srv://teste:teste@cluster0.lo8zl.mongodb.net/<dbname>?retryWrites=true&w=majority')
    data_base = cluster['asset_management_example'] ## refers to the sample portfolio
    collection = data_base['asset_management_example'] ## refers to the sample portfolio


    client = collection.find_one({'_id':client}) ## Normally, each client should have his/her id
    ## We get the info regarding the investments performce, already computed
    df_final_stocks = pd.DataFrame(client['stocks_values']).set_index('Date')
    df_final_funds = pd.DataFrame(client['funds_values']).set_index('Date')
    df_final_fix = pd.DataFrame(client['fix_values']).set_index('data')

    return(df_final_stocks, df_final_funds, df_final_fix)

def data_base_client_input_info(client):
    ## Let us first set the connection
    cluster = MongoClient('mongodb+srv://teste:teste@cluster0.lo8zl.mongodb.net/<dbname>?retryWrites=true&w=majority')
    data_base = cluster['asset_management_example'] ## refers to the sample portfolio
    collection = data_base['asset_management_example'] ## refers to the sample portfolio

    client = collection.find_one({'_id':client}) ## Normally, each client should have his/her id
    df_input_stocks = pd.DataFrame(client['stocks_input'])
    df_input_funds = pd.DataFrame(client['funds_input'])
    df_input_fix = pd.DataFrame(client['fix_input']).set_index('fix_buy_date')

    return(df_input_stocks, df_input_funds, df_input_fix)


