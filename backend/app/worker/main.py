import time
# pyrefly: ignore [missing-import]
from loguru import logger

def main():
    logger.info("Starting Background Worker Process...")
    try:
        while True:
            logger.info("Worker heartbeat...")
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Worker stopped.")

if __name__ == "__main__":
    main()
