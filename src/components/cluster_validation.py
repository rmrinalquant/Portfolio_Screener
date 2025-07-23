from sklearn.metrics import silhouette_score, calinski_harabasz_score,davies_bouldin_score
from src.logger import logging
from src.exception import CustomException
from src.config import ModelEvaluationConfig, ModelTrainerConfig
import sys
import pandas as pd
from sklearn.metrics import adjusted_rand_score

class ClusterValidation:
    def __init__(self):
        self._val_params = ModelEvaluationConfig()
        self._model_params = ModelTrainerConfig()
        self.ari_ : list = list()
        self.silhouette_ : float = None
        self.davies_ : float = None
        self.calinski_ : float = None


    def cluster_metrics(self, X : pd.DataFrame, cluster_model : object) -> object:
        try:
            logging.info("Model Validation started")
            X = X.copy()
            self.silhouette_ = silhouette_score(X, cluster_model.labels_, metric=self._val_params.metric)
            self.calinski_ = calinski_harabasz_score(X, cluster_model.labels_)
            self.davies_ = davies_bouldin_score(X, cluster_model.labels_)
            return self
        
        except Exception as e:
            logging.info(f"Model Validation failed with exception {e}")
            raise CustomException(e, sys)
    


    def stability_test(self, X : pd.DataFrame, labels : list, cluster_model : object, k : int = 2) -> object:
        try:
            logging.info("Model stability check started")
            X = X.copy()
            base_label = pd.Series(labels, index=X.index,name ='base_label')

            for i in range(self._val_params.ari_iter):
                sample = X.sample(frac=1, replace=True, random_state=i)
                km = cluster_model(n_clusters= k, n_init=self._model_params.n_init,
                                   random_state=self._model_params.random_state).fit(sample)
                
                label_b = km.labels_
                _temp = adjusted_rand_score(base_label.loc[sample.index], label_b)
                self.ari_.append(_temp)
            return self


        except Exception as e:
            logging.info(f"Model Validation failed with exception {e}")
            raise CustomException(e, sys)