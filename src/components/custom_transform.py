from pathlib import Path
from sklearn.base import BaseEstimator, TransformerMixin
import numpy as np
import pandas as pd
from src.logger import logging

class SectorMedianImputer(BaseEstimator, TransformerMixin):
    def __init__(self, sector : str = 'sector', features : list[str] | None = None):
        '''
        sector - name of the sector column in the dataframe - chosen to be 'sector' by default
        '''
        self.features = features  
        self.sector = sector
        self._median : pd.DataFrame | None = None

    
    def fit(self, X : pd.DataFrame, y=None):
        X = X.copy()
        if self.features is None:
            self.features = X.columns
        self._median = X.groupby(self.sector)[self.features].median()
        return self

    def transform(self, X, y = None):
        if self._median is None:
            raise RuntimeError("Median imputer is not fitted")

        X = X.copy()
        for col in self.features:
            X[col] = X[col].fillna(X[self.sector].map(self._median[col]))
        
        return X
 
class SectorNeutralizor(BaseEstimator, TransformerMixin):
    def __init__(self, sector : str = 'sector', features : list[str] | None = None):
        '''
        sector - name of the sector column in the dataframe - chosen to be 'sector' by default
        '''
        self.features = features  
        self.sector = sector
        self._median : pd.DataFrame | None = None
        self._iqr : pd.DataFrame | None = None

    def fit(self, X : pd.DataFrame, y=None, q_3 = 0.75, q_1 = 0.25):
        X = X.copy()
        if self.features is None:
            self.features = X.columns
        grp = X.groupby(self.sector)[self.features]
        
        self._median =  grp.median()
        self._iqr = grp.quantile(q_3) - grp.quantile(q_1)

        return self

    def transform(self, X, y = None):
        if self._median is None or self._iqr is None:
            raise RuntimeError("SectorNeutralizer must be fitted before transform().")

        X = X.copy()

        for col in self.features:
            med = X[self.sector].map(self._median[col])
            try:
                iqr = X[self.sector].map(self._iqr[col])
            except:
                logging.info(f"zero division error for column {col}")
                raise RuntimeError(f"zero division error for column {col}")
            X[col] = (X[col] - med) / iqr

        return X

class clipper:
    def __init__(self, min = -5, max = 5, features : list[str] | None = None):
        self.min = min
        self.max = max
        self.features = features

    def fit(self, X, y=None):
        if self.features is None:
            self.features = X.columns
        return self

    def transform(self, X, y=None):
        X = X.copy()
        for col in X.columns:
            X[col] = np.clip(X[col], self.min, self.max)
        return X
    
if __name__ == "__main__":
    pass    