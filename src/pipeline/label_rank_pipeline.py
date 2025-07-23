from src.components.cluster_lable_cent_rank import label_cluster
import src.components.data_transformation as data_transformation
from pathlib import Path    
from src.utils import save_parquet


if __name__ == '__main__':
       
    """
    Note : The flow running pipeline is as follows:
            1. Cluster pipeline - it insures data ingestion, transformation modeling and saving the data in parquet format
            2. Label cluster pipeline - fetches data from artifacts and do labeling and ranking 
                                        ( Make sure to check for path as the date changes with each run - change 07_22_2025_23_45_08 to the latest date)

    """

    file_path = Path(__file__).resolve().parent.parent.parent / "artifacts"
    obj = label_cluster()
    obj.initialze_labeler(file_path / "cluster_validation" / "07_22_2025_23_45_08" /"model.parquet",
                              file_path / "transformed_data" / "transformed.parquet",
                                file_path / "merged_data" / "merged.parquet").rank_cluster()
       
       
    transformed_data = obj._transformed_data
    merged_data = obj._merged_data

    save_parquet(file_path = file_path / "final_data" / "transformed_final_data.parquet", df= transformed_data, engine='pyarrow')
    save_parquet(df = merged_data, file_path = file_path / "final_data" / "merged_final_data.parquet", engine='pyarrow')
