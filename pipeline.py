from Scripts.Src.Utils import general
from Scripts.Src.inserter import insert_data
from Scripts.Src.db import connection
from Scripts.Src.db import Schema
import yfinance as yf
import risk_metric as rm
import os
from Scripts.Src.fetcher import ingest_fundamental_data, ingest_tech_data
import pandas as pd
import time

'''
Run by checking the data size usually it hit the rate limit around 3000 tickers at a time.
    - Divide it into two halfs and run the second after the first half is done with time lag of 15 mins

Important
---------
- Use small batch function to gather data for size < 1000

Feature enhancements
-------------------
    Rollback feature
    Use this approach for end will figure out  the optimized technique 
    Scheduling jobs
    Multithreading
'''

# Setting up base directory for connection
base_dir  = os.path.abspath(os.path.join(__file__,".."))
path = os.path.join(base_dir,'Config', '.env')

# Setting up path for loading data
def data_path(file_name):
    base_dir = os.path.dirname(__file__)
    data_path = os.path.join(base_dir,"Data","Raw_data", f'{file_name}')
    return data_path

def small_batch_job(data, query, cursor):
    data = general.batch(data, 100)
    staged_data = ingest_fundamental_data.data_staging(data)
    insert_data.insert_data(staged_data, query, cursor)
    print("Inserted data:",staged_data)

def root_data(data,cursor):
    root_query = "Insert into MetaData_US_companies (Ticker, Company, Sector, Country, Industry, BusinessSummary) VALUES %s ON CONFLICT (Ticker) DO NOTHING"
    small_batch_job(data, root_query, cursor)
    
def fundamental_data(data,cursor):
    cursor.execute("Select Stock_Id,Ticker from MetaData_US_companies")
    query = "Insert into Fundamental_Metrics ( Stock_Id,trailing_pe,forward_pe,\
                    price_to_book,price_to_sales,peg_ratio,profit_margin,return_on_equity,return_on_assets,revenue_growth,\
                        eps_growth,dividend_yield,debt_to_equity,current_ratio,market_cap,operating_cash_flow,free_cash_flow) VALUES %s ON CONFLICT (Stock_Id) DO NOTHING"
    _data = cursor.fetchall()
    chunk = general.batch(data, 100)
    pair = {ticker: _id for _id, ticker in _data}
    staged_data = ingest_fundamental_data.data_staging(chunk, pair)
    insert_data.insert_data(staged_data, query, cursor) 
    print("Inserted data:",staged_data)

def tech_raw_data(data,cursor):

    '''
    Ingests Technical data from Yahoo Finance

    Parameters
    ----------
    data : list of tickers (list of list) - batch
    cursor : cursor object of database connection

    Note
    ----
    Send small file and load into the database first if not the server will close the connection
    '''
    
    cursor.execute("Select Stock_Id,Ticker from MetaData_US_companies")
    query = "Insert into Technical_Data( Stock_Id,Date,Open,High,Low,Close,Volume) VALUES %s "
    _data = cursor.fetchall()
    chunk = general.batch(data, 100)
    pair = {ticker: _id for _id, ticker in _data}
    staged_data = ingest_tech_data.data_staging(chunk, pair)
    insert_data.insert_data(staged_data, query, cursor) 
    #print("Inserted data:",staged_data)


def risk_metric(cursor, conn):
    query = " Select Date, m.Stock_ID,Ticker,Close \
          from MetaData_US_companies as m \
          inner join Technical_Data as t on m.Stock_Id = t.Stock_Id\
          where date between '2020-04-16' and '2025-12-20' \
          order by m.Ticker, t.date "
    insert_query = "Insert into Risk_Return_Metrics (Stock_Id,annual_return,volatility ,sharpe_ratio,beta,max_drawdown) VALUES %s ON CONFLICT (Stock_Id) DO NOTHING"
    risk_free = yf.download(tickers = "^IRX", period = '8y', interval = '1d',group_by = 'ticker', auto_adjust = True)
    risk_free = risk_free.loc['2024-04-16':]['^IRX']['Close']
    annalized_risk_free = risk_free.mean()/100 
    market_data = pd.read_sql_query(query, conn)
    staged_data = rm.risk_metric('2024-04-16', '2025-12-20', market_data, annalized_risk_free)
    
    insert_data.insert_data(staged_data, insert_query, cursor) 

def main():
    conn = connection.get_neon_connection(path)
    cursor = conn.cursor()
    
    #Schema.drop_table(cursor)
    Schema.create_table(cursor)
    data = pd.read_csv(data_path('S&p_500.csv'))['Symbol'].to_list()
    #root_data(data, cursor)
    #fundamental_data(data,cursor)
    #tech_raw_data(data,cursor)
    risk_metric(cursor, conn)
    #root_query = "Insert into MetaData_US_companies (Ticker, Company, Sector, Country, Industry, BusinessSummary) VALUES %s ON CONFLICT (Ticker) DO NOTHING"    
    #half = len(data)//2      # Send the data in batches hiting rate limit -- send half and other half after 15 mins -- input manually in the job function 
    
    conn.commit()
    conn.close()
    cursor.close()

        

if __name__ == "__main__":
    main()
    
