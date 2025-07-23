from src.config import FeatureSelectionConfig
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from src.exception import CustomException
from src.logger import logging
import sys

class SpreadRatioFilter(BaseEstimator, TransformerMixin):

    """
    Check spread ratio for each feature - remove features with low spread

    Parameters:
        features: list[str]
        Note : The code structure need features, must be passed as a list 
    
    """

    def __init__(self,features: list) -> None:
        self.feature_selection_config = FeatureSelectionConfig()
        self.features = features
        self._selected_features : list[str] = None
        

    
    def fit(self, X: pd.DataFrame) -> pd.DataFrame:
        X = X.copy()
        try:
            Q1 = X[self.features].quantile(self.feature_selection_config.Q1)
            Q3 = X[self.features].quantile(self.feature_selection_config.Q3)
            IQR = Q3 - Q1
            _min = X[self.features].min()
            _max = X[self.features].max()
        
            Iqr_ratio = IQR / (_max - _min)
        
            mask = Iqr_ratio < self.feature_selection_config.spread_ratio_threshold
            self._selected_features = mask.index[mask == False].tolist()

        except Exception as e:
            logging.info("Spread ratio filter failed")
            raise CustomException(e, sys)   
        return self
    
    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        X = X.copy()
        if self._selected_features is None:
            raise RuntimeError("Spread ratio filter must be fitted before transform().")

        return X[self._selected_features]

        
if __name__ == "__main__":
    pass
    