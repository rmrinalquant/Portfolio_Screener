from src.components.data_ingestion import DataIngestion
from src.components.data_transformation import DataTransformation
from src.components.cluster_models import ModelTrainer
from src.config import DataIngestionConfig, FeatureSelectionConfig
from src.exception import CustomException
from src.logger import logging
import os
import sys


class cluster_pipeline:
    
    def __init__(self):
        self.feature_config = FeatureSelectionConfig()
        self.ingestion_config = DataIngestionConfig()

    def run_pipeline(self):
        logging.info("Pipeline has started")
        base_dir = os.path.abspath(os.path.join(__file__,"..","..",".."))
        path = os.path.join(base_dir,'.env')
        data_ingestion = DataIngestion(_path=path)
        data_ingestion.initiate_data_ingestion()    

        data_transformation = DataTransformation()
        transformed_data, _ = data_transformation.initiate_transformation(
                                   fundamental_data_path = DataIngestionConfig.fundamental_data_path,
                                   technical_data_path = DataIngestionConfig.technical_data_path,
                                   metadata_data_path = DataIngestionConfig.metadata_data_path,
                                   features = self.feature_config.features
                                )

        obj = ModelTrainer()
        obj.initialze_model(transformed_data)
        logging.info("Pipeline has completed")



if __name__ == '__main__':
    try:
        obj = cluster_pipeline()
        obj.run_pipeline()
    except Exception as e:
        logging.info("Pipeline has failed")
        raise CustomException(e, sys)
                          
