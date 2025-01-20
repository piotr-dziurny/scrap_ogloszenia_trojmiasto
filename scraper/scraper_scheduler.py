import time
import logging
from datetime import datetime, timedelta
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from ogloszenia_trojmiasto.spiders.ogloszenia import OgloszeniaSpider
from pathlib import Path

log_dir = Path("/scraper/logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "scraper.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler() # print in terimnal 
    ]
)

def run_spider():
    logging.info("Starting spider...")
    try:
        process = CrawlerProcess(get_project_settings())
        process.crawl(OgloszeniaSpider)
        process.start()
        logging.info("Spider run completed successfully")
    except Exception as e:
        logging.error(f"Error during spider run: {str(e)}")

def main():
    logging.info("Starting scheduler...")
    
    logging.info("Running initial spider...")
    run_spider()
    
    next_run = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=3)
    logging.info(f"Next scheduled run at: {next_run}")
    
    while True:
        now = datetime.now()
        if now >= next_run:
            run_spider()
            next_run += timedelta(days=3)
            logging.info(f"Next scheduled run at: {next_run}")
        
        time.sleep(60*60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.critical(f"Critical error in scheduler: {str(e)}")
        raise
