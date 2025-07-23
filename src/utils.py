from dotenv import load_dotenv
import os
import psycopg2
from src.logger import logging
import sys
from src.exception import CustomException
import pickle
import pandas as pd


class DBConnection:
    def __init__(self, prefix:str = 'NEON', env_path : str = '.env') -> None:
        """
        Initialize DB connection
        prefix - DB name prefix
        """       
        self.prefix = prefix.upper()
        load_dotenv(env_path)
        self._conn = None

    def _e(self, key : str) -> str:
        """
        Get environment variable
        """
        key = key.upper()
        var = f"{self.prefix}_{key}"
        val = os.getenv(var)
        if val == None:
            logging.info(f"Environment variable {var} is not set")
            raise RuntimeError(f"Environment variable {var} is not set")
        return val
    
        
    def conn(self) -> psycopg2.extensions.connection:
        """
        Establishes connection to database
        """
        if self._conn and self._conn.closed :
            return self._conn
        try:
            self._conn = psycopg2.connect(
                host= self._e("HOST"),
                database= self._e("NAME"),
                user= self._e("USER"),
                password= self._e("PASSWORD"),
                port= self._e("PORT")                
        )
        except Exception as e:
            logging.info(f"Error connecting to the database: {e}")
            raise RuntimeError(f"Error connecting to the database: {e}")
        return self._conn
    
def save_object(file_path, obj):
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as file_obj:
            pickle.dump(obj, file_obj)
    except Exception as e:
        raise CustomException(e, sys)
    
def save_parquet(file_path, df, **kwargs):
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        df.to_parquet(file_path, index = False, **kwargs)
    except Exception as e:
        raise CustomException(e, sys)
    

def save_to_dataframe(current : pd.DataFrame | None, data):
        df = pd.DataFrame(data)
        return df if current is None else pd.concat([current, pd.DataFrame(data)])

if __name__ == '__main__':
       pass