import logging
from pathlib import Path
import os
from datetime import datetime


LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
log_path = Path(__file__).parent.parent / "logs"
log_path.mkdir(parents=True, exist_ok=True) 
#log_path = os.path.join(os.getcwd(), "logs", LOG_FILE)
#print(log_path)
#LOG_FILE_PATH = os.path.join(log_path, LOG_FILE)
LOG_FILE_PATH = log_path / LOG_FILE 
#os.makedirs(log_path, exist_ok=True)

logging.basicConfig(
        filename=str(LOG_FILE_PATH),
        format="[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
)

if __name__ == "__main__":
    logging.info("Logging has started")
  


