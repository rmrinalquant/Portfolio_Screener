from Utils import data_utils
from Scripts.Src import load_meta_data
import os

# Setting up base directory for connection
base_dir  = os.path.abspath(os.path.join(__file__,".."))
path = os.path.join(base_dir,'Config', '.env')
conn = data_utils.get_connection(path)
cursor = conn.cursor()

# Setting up path for loading data
base_dir = os.path.dirname(__file__)
data_path = os.path.join(base_dir,"Data","Raw_data", f'{"Us_tickers.txt"}')

def main():
    #Schema.create_table(conn, cursor)
    data = data_utils.read_ticker_data(data_path)
    load_meta_data.load_data(data)
    print(data)
    


if __name__ == "__main__":
    main()
    conn.close()
    cursor.close()
