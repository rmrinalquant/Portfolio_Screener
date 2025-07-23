import os 
import sys
from src.exception import CustomException
from src.logger import logging
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from src.config import DataIngestionConfig
from src.utils import DBConnection

class DataIngestion:
    def __init__(self, _path : str )-> None:
        self._env_path = _path
        self.ingestion_config = DataIngestionConfig()   

    def initiate_data_ingestion(self) -> Path:
        """
        Initiate Data Ingestion Process from database
        - Save the data to csv in Artifacts
        - Return the path for the data

        """
        logging.info("Entered the data ingestion method or component")
        try:
            logging.info("Exporting data from database to csv file")
            db = DBConnection(env_path= self._env_path)
            conn = db.conn()
            fundamental_data = pd.read_sql("Select * from Fundamental_Metrics", con=conn)
            technical_data = pd.read_sql("Select * from risk_return_metrics", con=conn)
            metadata_data = pd.read_sql("Select * from MetaData_US_companies", con=conn)

            self.ingestion_config.artifacts_dir.mkdir(parents=True, exist_ok=True)
            
            fundamental_data.to_csv(self.ingestion_config.fundamental_data_path, index=False, header=True)
            technical_data.to_csv(self.ingestion_config.technical_data_path, index=False, header=True)
            metadata_data.to_csv(self.ingestion_config.metadata_data_path, index=False, header=True)
            
            logging.info("Exported data from database to csv file")
            conn.close()
            return (
               self.ingestion_config.fundamental_data_path, 
               self.ingestion_config.technical_data_path, 
               self.ingestion_config.metadata_data_path
            )
        except Exception as e:
            logging.info("Error occured in data ingestion")
            raise CustomException(e, sys)
        
if __name__ == '__main__':
    pass
    