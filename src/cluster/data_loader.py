from etl.db import connection
import pandas as pd
import os


base_dir = os.path.abspath(os.path.join(__file__,"..","..",".."))
path = os.path.join(base_dir,'Config', '.env')

conn= connection.get_neon_connection(path)
cursor = conn.cursor()

cursor.execute("Select * from MetaData_US_companies")
temp_sp  = cursor.fetchall()
sp500_df = pd.DataFrame(temp_sp, columns = ['Stock_Id', 'Ticker', 'Company', 'Sector', 'Country', 'Industry', 'BusinessSummary', 'Created_at'])   


cursor.execute("Select * from Fundamental_Metrics")
temp_f = cursor.fetchall()
fundamental_df = pd.DataFrame(temp_f, columns = ['Stock_Id','trailing_pe','forward_pe','price_to_book','price_to_sales'	,'peg_ratio','profit_margin','return_on_equity','return_on_assets','revenue_growth','eps_growth','dividend_yield','debt_to_equity','current_ratio','market_cap','operating_cash_flow','free_cash_flow','created_at'])


cursor.execute("Select * from risk_return_metrics")
temp_t = cursor.fetchall()
risk_df = pd.DataFrame(temp_t, columns = ['Stock_Id','annual_return','volatility','sharpe_ratio','beta','max_drawdown','created_at'])  
risk_df = risk_df.sort_values('Stock_Id').reset_index(drop=True)



merged_df = pd.merge(fundamental_df, risk_df, on='Stock_Id', how='inner')
merged_df = pd.merge(merged_df, sp500_df[['Stock_Id', 'Ticker','Sector']], on='Stock_Id', how = 'inner')
