from src.config import FeatureMappingConfig, DataTransformationConfig
import pandas as pd
from pathlib import Path
from src.logger import logging
from src.exception import CustomException
import numpy as np
from src.utils import save_parquet

class label_cluster():
    def __init__(self):
        self.mapping_obj = FeatureMappingConfig()
        self.data_transformation_config = DataTransformationConfig()
        self._transformed_data : pd.DataFrame = None
        self._merged_data : pd.DataFrame = None

    def _read_data(self, *data_paths : list)-> pd.DataFrame:
        """
        Note : The order in which path is send is cluster_validation, transfromed data and merged data
               Will fix it on later versions

        lst [0] = cluster_validation
        lst [1] = transformed data
        lst [2] = merged data
        """
        return [pd.read_parquet(path) for path in data_paths]

    
    def mapper(self, data : pd.DataFrame, label :list ,feature_name:str) -> pd.DataFrame:
            data[feature_name] = label
            data[feature_name] = (data[feature_name].map(self.mapping_obj.bucket_label_map[feature_name]))
            return data

        
    def distance_cal(self, data, feature_name, label, bucket):
        _data = data[data[bucket] == label]
        centroid = _data[feature_name].mean().values

        dis = np.linalg.norm(_data[feature_name].values - centroid, axis=1)
        return dis


    def initialze_labeler(self, *data_paths : str)-> pd.DataFrame:  
        logging.info("Entered the label cluster method or component")

        _data = self._read_data(*data_paths)
    
        for bucket, value in self.mapping_obj.k_value.items():
            temp_data = _data[0].groupby("buckets").get_group(bucket)
            temp_data = temp_data[temp_data['k_value'] == value]

            label = temp_data['labels'].values[0]
            
            _transformed_data = self.mapper(_data[1], label, bucket)
            _merged_data = self.mapper(_data[2], label, bucket)

        self._transformed_data = _transformed_data
        self._merged_data = _merged_data

        return self
    
    def rank_cluster(self):
        if self._transformed_data is None and self._merged_data is None:
            raise Exception("Run initialze_labeler before running rank_cluster")
        
        for bucket, feature in self.mapping_obj.bucket.items():
            factor_name = tuple(set(self._transformed_data[bucket].values))
            self._transformed_data[f'{bucket}_distance'] = np.nan
            self._merged_data[f'{bucket}_distance'] = np.nan
            
            for factor in factor_name:
                
                mask = self._transformed_data[bucket] == factor
                dis = self.distance_cal(self._transformed_data, feature, factor, bucket)
                self._transformed_data.loc[mask, f'{bucket}_distance'] = dis
                self._merged_data.loc[mask, f'{bucket}_distance'] = dis

        #save_parquet(file_path = self.data_transformation_config.transformed_data_path, df= self._transformed_data, engine='pyarrow')
        #save_parquet(df = self._merged_data, file_path = self.data_transformation_config.merged_data_path, engine='pyarrow')

        return self
    
        
            
if __name__ == "__main__":
    pass
    


