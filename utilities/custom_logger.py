import logging
import os

class Log_Maker:
    @staticmethod
    def log_gen():
        logger = logging.getLogger("Wiseyak")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            logs_dir = os.path.join(os.getcwd(), "logs")
            os.makedirs(logs_dir, exist_ok=True)

            file_handler = logging.FileHandler(os.path.join(logs_dir, "wiseyak.log"), mode='a')
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        return logger
