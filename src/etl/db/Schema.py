def create_table(cursor):
    '''
    Create Manual schema design for database (Change based on db needs)
    Realtionships
    1-1 - MetaData_US_companies - Fundamental_Metrics
    1-M - MetaData_US_companies - Technical_Metrics

    Paraments
    ----------
    cursor : cursor object of database connection

    Future enhancements
    ----------
    Add logging
    No code solution
    Indexing and optimization

    '''

    try:
        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS MetaData_US_companies (
            Stock_Id INT GENERATED ALWAYS AS IDENTITY (START WITH 910000 INCREMENT BY 1) PRIMARY KEY,
            Ticker VARCHAR(10) UNIQUE NOT NULL,
            Company VARCHAR(200) Default 'Unknown',
            Sector VARCHAR(100) Default 'Unknown',
            Country VARCHAR(100) Default 'Unknown',
            Industry VARCHAR(100) Default 'Unknown',
            BusinessSummary TEXT Default 'No summary available',
            Created_at DATE DEFAULT CURRENT_DATE
        )
    """)
    except Exception as e:
        print(f"Error creating table: {e}")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Fundamental_Metrics (
        Stock_Id INT PRIMARY KEY,
        trailing_pe NUMERIC,
        forward_pe NUMERIC,
        price_to_book NUMERIC,
        price_to_sales NUMERIC,
        peg_ratio NUMERIC,
        profit_margin NUMERIC,
        return_on_equity NUMERIC,
        return_on_assets NUMERIC,
        revenue_growth NUMERIC,
        eps_growth NUMERIC,
        dividend_yield NUMERIC,
        debt_to_equity NUMERIC,
        current_ratio NUMERIC,
        market_cap BIGINT,        
        operating_cash_flow BIGINT,
        free_cash_flow BIGINT,
        Created_at DATE DEFAULT CURRENT_DATE,
        FOREIGN KEY (Stock_Id) REFERENCES MetaData_US_companies (Stock_Id) ON DELETE CASCADE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Technical_Data (
        Row_Id INT GENERATED ALWAYS AS IDENTITY (START WITH 100 INCREMENT BY 1) PRIMARY KEY,
        Stock_Id INT,
        Date DATE,
        Open NUMERIC,
        High NUMERIC,
        Low NUMERIC,
        Close NUMERIC,
        Volume BIGINT,
        Created_at DATE DEFAULT CURRENT_DATE,
        FOREIGN KEY (Stock_Id) REFERENCES MetaData_US_companies (Stock_Id) ON DELETE CASCADE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Risk_Return_Metrics (
        Stock_Id INT PRIMARY KEY,
        annual_return NUMERIC,
        volatility NUMERIC,
        sharpe_ratio NUMERIC,
        beta NUMERIC,
        max_drawdown NUMERIC,
        Created_at DATE DEFAULT CURRENT_DATE,
        FOREIGN KEY (Stock_Id) REFERENCES MetaData_US_companies (Stock_Id) ON DELETE CASCADE
        
    )""")

    
def drop_table(cursor): 
    
    cursor.execute("DROP TABLE IF EXISTS MetaData_US_companies")
    #cursor.execute("DROP TABLE IF EXISTS Ticker_Data_Us")



if __name__ == "__main__":
    pass