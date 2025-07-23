
import pandas as pd
from sklearn import set_config
set_config(transform_output="pandas") 
from src.components.custom_transform import SectorMedianImputer, SectorNeutralizor,clipper
from src.config import DataIngestionConfig, DataTransformationConfig
import sys
from src.components.feature_selector import SpreadRatioFilter
from src.exception import CustomException
from src.logger import logging
from src.config import DataTransformationConfig
from sklearn.preprocessing import PowerTransformer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from src.utils import save_object, save_parquet

class DataTransformation:
       def __init__(self):

              self.data_transformation_config = DataTransformationConfig()
              self.ingestion_config = DataIngestionConfig()
              self._merged_data : pd.DataFrame = None
              self._transformed_data : pd.DataFrame = None

       def get_data_transformation_object(self, features):
              """
              The function returns the data transformation pipeline

              Note : The sector column is removed after the neutralization step, if required add manually into future steps
              
              """
              try:
                     
                     logging.info("Data transformation started")

                     Yeo_transform_step = ColumnTransformer(
                            transformers = [
                                   ('yeo', PowerTransformer(method = 'yeo-johnson', standardize = False), features)
                            ],
                            remainder='passthrough',
                            verbose_feature_names_out=False
                     )

                     pre_processor = Pipeline(
                            steps = [
                                   ("median_imputer", SectorMedianImputer(features = features)),
                                   ('power_transformer',Yeo_transform_step),
                                   ("neutralizer", SectorNeutralizor(features = features)),
                                   ("spread_ratio_filter", SpreadRatioFilter(features = features)),
                                   ("clipper", clipper())
                            ]
                     )

                     logging.info("Data transformation completed")

                     return pre_processor
              except Exception as e:
                     logging.info(f"Error in data transformation: {e}")
                     raise CustomException(e, sys)
              

       def initiate_transformation(self, fundamental_data_path, technical_data_path, metadata_data_path, features : list[str] = None):
              try:

                     logging.info("Initiating transformation on data")
                     logging.info("Reading data")

                     fundamental_data = pd.read_csv(fundamental_data_path)
                     risk_data = pd.read_csv(technical_data_path)
                     metadata_data = pd.read_csv(metadata_data_path)

                     logging.info("Merging data")
                     merged_df = pd.merge(fundamental_data, risk_data, on='stock_id', how='inner')
                     merged_df = pd.merge(merged_df, metadata_data[['stock_id', 'ticker','sector']], on='stock_id', how = 'inner')

                     logging.info("Removed rows where more than 10 values are missing")
                     row_missing = merged_df.isna().sum(axis = 1)
                     #removed_data = merged_df.loc[row_missing >=10]
                     merged_df = merged_df.loc[row_missing < 10]
                     self._merged_data = merged_df
                     save_parquet(df= merged_df, file_path = self.data_transformation_config.merged_data_path, engine='pyarrow')
                     
                     if features is None:
                            features = merged_df.columns


                     merged_df = merged_df[features]

                     logging.info("Applying transformation on raw data")

                     preprocessor_obj = self.get_data_transformation_object(features = features[0:-1])
                     transformed_data = preprocessor_obj.fit_transform(merged_df)
                     logging.info("Data transformation completed")

                     
                     save_object(
                            file_path = self.data_transformation_config.preprocessed_object_path,
                            obj = preprocessor_obj
                     )

                     save_parquet(df= transformed_data, file_path = self.data_transformation_config.transformed_data_path, engine='pyarrow')

                     return (
                            transformed_data,
                            self.data_transformation_config.preprocessed_object_path
                     )
                  
              except Exception as e:
                     logging.info(f"Error in data initiation: {e}")
                     raise CustomException(e, sys)

if __name__ == '__main__':
       pass
                      
       