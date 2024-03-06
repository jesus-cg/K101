import time
import sys
import RPi.GPIO as GPIO
from datetime import datetime
import pymysql

class FlowMeter:
    def __init__(self, db_host, db_name, db_user, db_pass):
        """
        Initialize the FlowMeter class with database connection details.
        """
        self.db_host = db_host
        self.db_name = db_name
        self.db_user = db_user
        self.db_pass = db_pass
        self.db_connection = None
        self.pin_input = 8
        self.ID = 1234  # For testing purposes
        self.m = 0.0021  # Constant for flow rate calculation
        self.sample_rate = 2  # Sample rate in seconds

        # Set up GPIO for flow sensor
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.pin_input, GPIO.IN)

    def connect_to_db(self):
        """
        Connect to the database.
        """
        try:
            self.db_connection = pymysql.connect(host=self.db_host, user=self.db_user, passwd=self.db_pass, db=self.db_name)
            print("Connected to database")
        except pymysql.MySQLError as e:
            print(f"Error connecting to database: {e}")
            sys.exit(1)

    def start_flow_detection(self):
        """
        Start detecting flow and write data to the database.
        """
        total_liters = 0
        seconds = 0
        time_start = 0
        time_end = 0
        period = 0
        hz = []
        db_good_sample = 0
        db_hz = 0
        db_liter_by_min = 0
        daily_db_liter_by_min = 0

        print("Water Flow - Detection with YF-S201 sensor")

        while True:
            time_start = time.time()
            time_end = time_start + self.sample_rate
            hz = []
            sample_total_time = 0

            current = GPIO.input(self.pin_input)
            edge = current

            # Connection with the Flowmeter and the assignment of values to each variable.
            try:
                while time.time() <= time_end:
                    t = time.time()
                    v = GPIO.input(self.pin_input)
                    if current != v and current == edge:
                        period = t - time_start
                        new_hz = 1 / period
                        hz.append(new_hz)
                        sample_total_time += t - time_start
                        time_start = t

                    current = v

                # Print current time and sensor data
                print('-------------------------------------')
                print('Current Time:', time.asctime(time.localtime()))

                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                seconds += self.sample_rate
                nb_samples = len(hz)
                if nb_samples > 0:
                    average = sum(hz) / float(len(hz))

                    good_sample = sample_total_time / self.sample_rate
                    print("\t", round(sample_total_time, 4), '(sec) good sample')
                    db_good_sample = round(good_sample * 100, 4)
                    print("\t", db_good_sample, '(%) good sample')
                    average = average * good_sample
                else:
                    average = 0
                average_liters = average * self.m * self.sample_rate
                total_liters += average_liters
                db_hz = round(average, 4)
                daily_db_liter_by_min = round(total_liters * (60 / seconds), 4)
                db_liter_by_min = round(average_liters * (60 / self.sample_rate), 4)

                print("\t", db_hz, '(hz) average')
                print('\t', db_liter_by_min, '(L/min)')
                print(round(total_liters, 4), "(L) today's total")
                print('-------------------------------------')

                # Write data to the database
                try:
                    with self.db_connection.cursor() as cursor:
                        sql = "INSERT INTO Kegistros(ID, TIEMPO, LITMIN, LITCONS) VALUES('%i', '%s', '%4.2f', '%6.2f' );"
                        data = (int(self.ID), current_time, db_liter_by_min, daily_db_liter_by_min)
                        cursor.execute(sql, data)
                    self.db_connection.commit()
                except pymysql.MySQLError as e:
                    print(f"Error writing to database: {e}")

            except KeyboardInterrupt:
                print('\n CTRL+C - Exiting')
                self.db_connection.close()
                GPIO.cleanup()
                sys.exit()

        GPIO.cleanup()
        self.db_connection.close()
        print('Done')

    def get_avg_daily_consumption(self):
        """
        Get the average daily water consumption from the database.
        """
        try:
            with self.db_connection.cursor() as cursor:
                sql = "SELECT AVG(LITMIN) FROM Kegistros WHERE TIEMPO >= CURDATE() and TIEMPO < (CURDATE()+1)"
                cursor.execute(sql)
                result = cursor.fetchall()
                avg_daily_consumption = result[0][0]
                return avg_daily_consumption
        except pymysql.MySQLError as e:
            print(f"Error querying data: {e}")

    def get_avg_fifteen_consumption(self):
        """
        Get the average water consumption for the last 15 days from the database.
        """
        fifmin = 21600  # 15 days in minutes

        try:
            with self.db_connection.cursor() as cursor:
                sql = "SELECT SUM(LITCONS) FROM Kegistros WHERE DATEDIFF(CURDATE(), DATE_SUB(CURDATE(), INTERVAL 15 DAY))=15"
                cursor.execute(sql)
                result = cursor.fetchall()
                total_consumption = result[0][0]
                avg_fifteen_consumption = total_consumption / fifmin
                return avg_fifteen_consumption
        except pymysql.MySQLError as e:
            print(f"Error querying data: {e}")

    def get_avg_thirty_consumption(self):
        """
        Get the average water consumption for the last 30 days from the database.
        """
        thimin = 43200  # 30 days in minutes

        try:
            with self.db_connection.cursor() as cursor:
                sql = "SELECT SUM(LITCONS) FROM Kegistros WHERE DATEDIFF(CURDATE(), DATE_SUB(CURDATE(), INTERVAL 30 DAY))=30"
                cursor.execute(sql)
                result = cursor.fetchall()
                total_consumption = result[0][0]
                avg_thirty_consumption = total_consumption / thimin
                return avg_thirty_consumption
        except pymysql.MySQLError as e:
            print(f"Error querying data: {e}")

    def get_avg_sixty_consumption(self):
        """
        Get the average water consumption for the last 60 days from the database.
        """
        sixmin = 86400  # 60 days in minutes

        try:
            with self.db_connection.cursor() as cursor:
                sql = "SELECT SUM(LITCONS) FROM Kegistros WHERE DATEDIFF(CURDATE(), DATE_SUB(CURDATE(), INTERVAL 60 DAY))=60"
                cursor.execute(sql)
                result = cursor.fetchall()
                total_consumption = result[0][0]
                avg_sixty_consumption = total_consumption / sixmin
                return avg_sixty_consumption
        except pymysql.MySQLError as e:
            print(f"Error querying data: {e}")

    def show_registration(self, query):
        """
        Show water consumption data based on a user-provided query.
        """
        try:
            cur = self.db_connection.cursor()
            cur.execute(query)
            result = cur.fetchall()
            return result
        except pymysql.MySQLError as e:
            print(f"Error querying data: {e}")

    def start_flow_detection_on_command(self):
        """
        Start detecting flow and write data to the database on command from a Flask webpage.
        """
        time_start = 0
        time_end = 0
        hz = []
        db_good_sample = 0
        db_hz = 0
        db_liter_by_min = 0
        i = 0
        current_time_start = None
        current_time = None

        while True:
            time_start = time.time()
            time_end = time_start + self.sample_rate
            hz = []
            sample_total_time = 0

            current = GPIO.input(self.pin_input)
            edge = current

            # Connection with the Flowmeter and the assignment of values to each variable.
            try:
                while time.time() <= time_end:
                    t = time.time()
                    v = GPIO.input(self.pin_input)
                    if current != v and current == edge:
                        period = t - time_start
                        new_hz = 1 / period
                        hz.append(new_hz)
                        sample_total_time += t - time_start
                        time_start = t

                    current = v

                if i == 0:
                    current_time_start = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                current_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                i += 1

                print('-------------------------------------')
                print('Start:', time.asctime(time.localtime()))

                nb_samples = len(hz)
                if nb_samples > 0:
                    average = sum(hz) / float(len(hz))

                    good_sample = sample_total_time / self.sample_rate
                    db_good_sample = round(good_sample * 100, 4)
                    average = average * good_sample
                else:
                    average = 0
                average_liters = average * self.m * self.sample_rate
                db_liter_by_min = round(average_liters * (60 / self.sample_rate), 4)

            except KeyboardInterrupt:
                print('\n CTRL+C - Exiting')
                self.db_connection.close()
                GPIO.cleanup()
                sys.exit()

            # Wait for command from Flask webpage to stop flow detection and save data
            # ...

        self.stop_flow_detection(current_time, current_time_start, db_liter_by_min)

    def stop_flow_detection(self, current_time, current_time_start, db_liter_by_min):
        """
        Stop detecting flow, calculate the total time and flow rate, and save the data to the database.
        """
        regname = "Registro N.#"

        date_format = "%d/%m/%Y %H:%M:%S"
        start = datetime.strptime(current_time_start, date_format)
        end = datetime.strptime(current_time, date_format)

        time_difference = end - start
        time_difference_in_hours = time_difference.total_seconds() / 3600

        try:
            with self.db_connection.cursor() as cursor:
                sql = "INSERT INTO Flugua (REGISTRO, TIEMPO TOTAL, LITMIN) VALUES('%s', '%s', %.2f);" % (
                    regname, time_difference_in_hours, db_liter_by_min)
                cursor.execute(sql)
            self.db_connection.commit()
        except pymysql.MySQLError as e:
            print(f"Error writing to database: {e}")

# Example usage
flow_meter = FlowMeter("172.32.180.247", "Kestagua", "root", "1234")
flow_meter.connect_to_db()

# Start flow detection and write data to the database continuously
# flow_meter.start_flow_detection()

# Get average water consumption for different time periods
avg_daily_consumption = flow_meter.get_avg_daily_consumption()
avg_fifteen_consumption = flow_meter.get_avg_fifteen_consumption()
avg_thirty_consumption = flow_meter.get_avg_thirty_consumption()
avg_sixty_consumption = flow_meter.get_avg_sixty_consumption()

# Show water consumption data based on a user-provided query
query = "SELECT * FROM Kegistros"
registration_data = flow_meter.show_registration(query)

# Start flow detection on command from a Flask webpage
# flow_meter.start_flow_detection_on_command()