from sklearn.cluster import KMeans
from src.logger import logging
from src.exception import CustomException
from src.utils import save_parquet, save_to_dataframe
from src.config import ModelTrainerConfig, FeatureMappingConfig, ModelEvaluationConfig
from src.components.cluster_validation import ClusterValidation
import pandas as pd
import numpy as np
import sys
import json

class ModelTrainer:
    def __init__(self):
        self.trainer_obj = ModelTrainerConfig()
        self.mapping_obj = FeatureMappingConfig()
        self.thresold_obj = ModelEvaluationConfig()
        self.result_metric_ : pd.DataFrame = None
        self.best_k_vals_ : pd.DataFrame = None
        self.labels_ : list = None

    def cluster_model(self, X , bucket : str = None): 
        models = { 'k-means' : KMeans,
        }

        try:
            temp = []
            best_temp = []
            logging.info("Model training started")
            print(f"Running Clustring algorithm for cluster {bucket}")
            for k in range(2,self.trainer_obj.n_clusters+1):
                kmeans = models['k-means'](n_clusters= k,n_init=self.trainer_obj.n_init ,random_state=self.trainer_obj.random_state).fit(X)
                self.labels_ = kmeans.labels_
                obj = ClusterValidation().cluster_metrics(X, kmeans).stability_test(X, kmeans.labels_, models['k-means'],k)
                #distance = kmeans.transform(X)

                params = {
                    'buckets' : bucket if bucket is not None else 'Full Dataset',
                    'k_value' : k,
                    'inertia' : kmeans.inertia_,
                    'centers' : json.dumps(kmeans.cluster_centers_.tolist()),
                    'ari_median' : np.median(obj.ari_),
                    'ari_std' : np.std(obj.ari_),
                    'silhouette' : obj.silhouette_,
                    'davies' : obj.davies_,
                    'calinski' : obj.calinski_,
                    'labels' : self.labels_
                }

                temp.append(params)
                if params['ari_median'] > self.thresold_obj.ari and params['silhouette'] > self.thresold_obj.silhouette and params['davies'] < self.thresold_obj.davies and params['k_value'] < self.thresold_obj.k:
                    best_temp.append(params)

            self.result_metric_ = save_to_dataframe(self.result_metric_, temp)
            print(self.result_metric_)
            if len(best_temp) > 0:
                self.best_k_vals_ = save_to_dataframe(self.best_k_vals_, best_temp)
            else:
                logging.info("There is no model that met the required threshold")
                raise Warning("There is no model that met the required threshold")
            
            print(self.best_k_vals_)
            return self
    
        except Exception as e:
            logging.info(f"Model training failed with exception {e}")
            raise CustomException(e, sys)

    def initialze_model(self, data):
        for bucket, value in self.mapping_obj.bucket.items():
            df = data[value]
            self.cluster_model(df, bucket)

        save_parquet(self.trainer_obj.model_path, self.result_metric_, engine='pyarrow')

        if self.best_k_vals_ is not None:
            save_parquet(self.trainer_obj.best_k_vals_path, self.best_k_vals_, engine='pyarrow')

        return self

if __name__ == "__main__":
    pass
    
