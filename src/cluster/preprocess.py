from cluster import data_loader
from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd


df = data_loader.merged_df

class MedianImputer(BaseEstimator, TransformerMixin):
    
    def __init__(self, sector=None, columns=None):
        self.columns = columns  
        self.sector = sector
    
    def fit(self, X, y=None):
        self.median = {}
        if self.columns is None:
            self.columns = X.columns
        for col in self.columns:
            self.median[col] = X[col].median()
        return self

    def transform(self, X):
        X_trans = X.copy()
        for 