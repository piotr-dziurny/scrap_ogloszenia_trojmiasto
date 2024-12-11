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
            database=os.getenv("DB_NAME"),
            ssl_ca=os.getenv("SSL_CA_PATH")
        )

        self.cursor = self.conn.cursor()

    def create_table(self):
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS scraped_items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            url VARCHAR(255) UNIQUE NOT NULL,
            title VARCHAR(255),
            price FLOAT,
            price_per_sqr_meter FLOAT,
            rooms INT,
            floor INT,
            square_meters FLOAT,
            year DATE,
            address VARCHAR(255),
            coastline_distance FLOAT,
            gdynia_downtown_distance FLOAT,
            gdansk_downtown_distance FLOAT,
            sopot_downtown_distance FLOAT,
            ins_date DATE
        )
        """
        try:
            self.cursor.execute(create_table_sql)
            self.conn.commit()
            print("Table scraped_items created")
        except mysql.connector.Error as error:
            print(f"Error creating table: {error}")

    def drop_table(self):
        drop_table_sql = """
        DROP TABLE scraped_items
        """
        self.cursor.execute(drop_table_sql)
        self.conn.commit()
        print("Table scraped_items dropped")

    def get_existing_urls(self):
        """

        get all urls currently in the db
        
        """
        self.cursor.execute("SELECT url FROM scraped_items")
        return {row[0] for row in self.cursor.fetchall()}

    def insert_item(self, item):
        """

        insert new item into the database. If listing's url is in database -> skip

        """

        query = """
        INSERT IGNORE INTO scraped_items (url, title, price, price_per_sqr_meter, rooms, floor, square_meters, year, address,
        coastline_distance, gdynia_downtown_distance, gdansk_downtown_distance, sopot_downtown_distance, ins_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)

        """
        try:
            self.cursor.execute(query, (
                item["title"],
                item["url"],
                item["price"],
                item["price_per_sqr_meter"],
                item["rooms"],
                item["floor"],
                item["square_meters"],
                item["year"],
                item["address"],
                item["coastline_distance"],
                item["gdynia_downtown_distance"],
                item["gdansk_downtown_distance"],
                item["sopot_downtown_distance"],
                item["ins_date"]
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
    #db_helper.drop_table()
    db_helper.close()
