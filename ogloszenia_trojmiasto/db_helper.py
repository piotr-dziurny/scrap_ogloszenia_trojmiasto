import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

class DatabaseHelper:
    def __init__(self):
        """
        init db connection
        """

        self.conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )

        self.cursor = self.conn.cursor()

    def create_table(self):
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS scraped_items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            url VARCHAR(255) NOT NULL,
            title VARCHAR(255),
            price FLOAT,
            price_per_sqr_meter FLOAT,
            rooms INT,
            floor INT,
            square_meters FLOAT,
            year DATE,
            address VARCHAR(255),
            city VARCHAR(255),
            coastline_distance FLOAT,
            gdynia_downtown_distance FLOAT,
            gdansk_downtown_distance FLOAT,
            sopot_downtown_distance FLOAT,
            area VARCHAR(255),
            created_ts TIMESTAMP,
            scraped_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_latest BOOLEAN NOT NULL DEFAULT 1,
            UNIQUE KEY url_latest (url, is_latest)
        )
        """

        try:
            self.cursor.execute(create_table_sql)
            self.conn.commit()
            print("Table scraped_items created")
        except mysql.connector.Error as error:
            print(f"Error creating table: {error}")

    def update_scraped_ts(self, url):
        """
        update scraped_ts column for the given url
        """

        query = "UPDATE scraped_items SET scraped_ts = NOW() WHERE url = %s AND is_latest = 1"
        try:
            self.cursor.execute(query, (url,))
            self.conn.commit()
        except mysql.connector.Error as error:
            print(f"Error updating scraped_ts: {error}")

    def get_existing_urls(self):
        """
        get all urls and their last scraped timestamps currently in the db where is_latest = 1
        """

        self.cursor.execute("SELECT url, scraped_ts FROM scraped_items WHERE is_latest = 1")
        return {row[0]: row[1] for row in self.cursor.fetchall()}


    def update_is_latest(self, url):
        """
        set is_latest column to 0 for the given url
        """

        query = "UPDATE scraped_items SET is_latest = 0 WHERE url = %s AND is_latest = 1"
        try:
            self.cursor.execute(query, (url,))
            self.conn.commit()
        except mysql.connector.Error as error:
            print(f"Error updating is_latest: {error}")

    def is_changed(self, url, item):
        """
        check if the new item differs from the existing item in the db 
        returns True if data has changed, False otherwise
        """
        query = """
        SELECT title, price, price_per_sqr_meter, rooms, floor, square_meters, year, address, city 
        FROM scraped_items 
        WHERE url = %s AND is_latest = 1
        """
        self.cursor.execute(query, (url,))
        result = self.cursor.fetchone()
        
        if not result:
            return True  # new entry
        
        fields_to_compare = ["title", "price", "price_per_sqr_meter", "rooms", 
                            "floor", "square_meters", "year", "address", "city"]
        
        current_values = [item[field] for field in fields_to_compare]
        
        for db_value, new_value in zip(result, current_values):
            if db_value != new_value:
                return True  # data has changed
                
        return False  # no changes detected


    def insert_item(self, item):
        """
        insert new item into the database. If listing's url is in database -> skip
        """

        query = """
        INSERT IGNORE INTO scraped_items (url, title, price, price_per_sqr_meter, rooms, floor, square_meters, year, address, city,
        coastline_distance, gdynia_downtown_distance, gdansk_downtown_distance, sopot_downtown_distance, area, created_ts, scraped_ts, is_latest)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)

        """
        try:
            self.cursor.execute(query, (
                item["url"],
                item["title"],
                item["price"],
                item["price_per_sqr_meter"],
                item["rooms"],
                item["floor"],
                item["square_meters"],
                item["year"],
                item["address"],
                item["city"],
                item["coastline_distance"],
                item["gdynia_downtown_distance"],
                item["gdansk_downtown_distance"],
                item["sopot_downtown_distance"],
                item["area"],
                item["created_ts"],
                item["scraped_ts"],
                item["is_latest"],
            ))

            self.conn.commit()
        except mysql.connector.Error as error:
            print(f"Error inserting values to the table: {error}")

    def close(self):
        self.cursor.close()
        self.conn.close()

if __name__ == "__main__":
    db_helper = DatabaseHelper()
    db_helper.create_table()
    db_helper.close()
