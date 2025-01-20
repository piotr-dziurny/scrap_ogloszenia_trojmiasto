import time
import logging
import threading
import map_generator
from app import app
from datetime import datetime

def run_map_generator():
    try:
        logging.info(f"[{datetime.now()}] Generating map...")
        map_generator.main()
    except Exception as e:
        logging.error(f"Map generation failed: {e}")

def schedule_map_generation():  
    while True:
        now = datetime.now()
        if now.hour in [6, 18] and now.minute == 0:
            run_map_generator() 
            time.sleep(60)
        time.sleep(60*60) 

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    
    try:
        # start the scheduler in a separate thread
        scheduler_thread = threading.Thread(target=schedule_map_generation, daemon=True)
        scheduler_thread.start()
        
        app.run_server(host="0.0.0.0", port=8050, debug=False)
    except Exception as e:
        logging.error(f"Error while trying to run the Dash APP: {e}")
        raise

if __name__ == "__main__":
    main()
