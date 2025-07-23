from pathlib import Path
from dataclasses import dataclass
from datetime import datetime


@dataclass
class DataIngestionConfig:
    artifacts_dir: Path = Path(__file__).resolve().parent.parent / "artifacts"
    
    fundamental_data_path: Path  = artifacts_dir / "fundamental.csv"
    technical_data_path:   Path  = artifacts_dir / "technical.csv"
    metadata_data_path:    Path  = artifacts_dir / "metadata.csv"
    


@dataclass
class DataTransformationConfig:
    artifacts_dir: Path = Path(__file__).resolve().parent.parent / "artifacts"
    preprocessed_object_path: Path  = artifacts_dir / "preprocessed.pkl"
    transformed_data_path: Path  = artifacts_dir /"transformed_data" /"transformed.parquet"
    merged_data_path : Path = artifacts_dir / "merged_data" / "merged.parquet"
    
@dataclass
class FeatureSelectionConfig:
    spread_ratio_threshold: float = 0.04
    Q1: float = 0.25
    Q3: float = 0.75

    features = ['trailing_pe', 'forward_pe', 'price_to_book',
                    'price_to_sales', 'profit_margin', 'return_on_equity',
                    'return_on_assets', 'revenue_growth', 'eps_growth', 'dividend_yield',
                    'debt_to_equity', 'current_ratio', 'operating_cash_flow',
                    'free_cash_flow', 'annual_return', 'volatility', 'sharpe_ratio', 'beta',
                    'max_drawdown', 'sector']

@dataclass
class FeatureMappingConfig:
    bucket = {
    'Value': ['trailing_pe', 'price_to_sales'],
    'Growth': ['revenue_growth','return_on_assets'],
    'Quality': ['profit_margin','return_on_assets'],
    'Defensive': ['current_ratio','debt_to_equity'],
    'Risk_Momentum':  ['sharpe_ratio','max_drawdown']
}
    
    # Final K value for buckets
    k_value = { 'Value': 4, 'Growth': 2, 'Quality': 3, 'Defensive': 3, 'Risk_Momentum': 3 }

    # Label names
    bucket_label_map = {
    "Value": {
        0: "Overvalued",
        1: "Undervalued",
        2: "Undervalued",
        3: "Fair Value"      # deep-value vs moderate both mapped to one label
    },
     "Growth": {
        0: "Low Growth",
        1: "High Growth"
    },
   "Quality": {
        0: "Lower Quality",
        1: "High Quality",
        2: "Average Quality"
    },

    'Defensive': {0:'Average Defense',
                  1:'Low Defense', 
                  2:'High Defense'
    },
    "Risk_Momentum": {
        0: "Poor risk adjusted gains",
        1: "Average risk adjusted gains",
        2: "Strong risk adjusted gains"
    }
}
    
@ dataclass
class ModelTrainerConfig:
    # Path
    file_name = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}"
    artifacts_dir: Path = Path(__file__).resolve().parent.parent / "artifacts"
    model_path: Path  = artifacts_dir /"cluster_validation" / file_name / "model.parquet"
    best_k_vals_path: Path = artifacts_dir /"candidate_values" / file_name / "best_k_vals.parquet"

    # Parameters K-Means
    random_state: int = 42
    max_iter: int = 100
    n_clusters: int = 10
    n_init: int = 50   

@dataclass
class ModelEvaluationConfig:
    metric = 'euclidean' 
    ari_iter = 200

    # K selection parameters
    ari : float = 0.65
    silhouette: int = 0.35
    davies: int = 1.2
    k : int = 5