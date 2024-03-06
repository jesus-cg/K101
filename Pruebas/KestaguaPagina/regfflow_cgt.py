from time import sleep
import time, sys
import RPi.GPIO as GPIO
from datetime import datetime
import pymysql

class WaterFlowMonitor:
    def __init__(self):
        self.db_server = "172.32.180.247"
        self.db_name = "Kestagua"
        self.db_username = "root"
        self.db_password = "1234"
        self.db_connection = None
        self.sample_rate = 2
        self.flow_pin = 8
        self.flow_meter = None
        self.total_liters = 0
        self.seconds = 0
        self.hz = []

    def connect_to_database(self):
        try:
            self.db_connection = pymysql.connect(
                host=self.db_server,
                user=self.db_username,
                passwd=self.db_password,
                db=self.db_name
            )
            print("Connected to the database")
        except pymysql.MySQLError as e:
            print(f"Error connecting to the database: {e}")
            sys.exit(1)

    def setup_flow_meter(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.flow_pin, GPIO.IN)

    def read_flow_meter(self):
        current = GPIO.input(self.flow_pin)
        edge = current

        while time.time() <= self.time_end:
            t = time.time()
            v = GPIO.input(self.flow_pin)

            if current != v and current == edge:
                period = t - self.time_start
                new_hz = 1 / period
                self.hz.append(new_hz)
                self.sample_total_time += t - self.time_start
                self.time_start = t

                if DEBUG:
                    print(round(new_hz, 4))
                    sys.stdout.flush()

            current = v

    def calculate_flow_metrics(self):
        nb_samples = len(self.hz)

        if nb_samples > 0:
            average = sum(self.hz) / float(len(self.hz))
            good_sample = self.sample_total_time / self.sample_rate

            db_good_sample = round(good_sample * 100, 4)
            average = average * good_sample
        else:
            average = 0

        average_liters = average * 0.0021 * self.sample_rate
        self.total_liters += average_liters
        db_hz = round(average, 4)
        db_liter_by_min = round(average_liters * (60 / self.sample_rate), 4)
        daily_db_liter_by_min = round(self.total_liters * (60 / self.seconds), 4)

        return db_hz, db_liter_by_min, daily_db_liter_by_min

    def insert_data_to_database(self, current_time, db_liter_by_min, daily_db_liter_by_min):
        try:
            with self.db_connection.cursor() as cursor:
                sql = "INSERT INTO Kegistros(ID, TIEMPO, LITMIN, LITCONS) VALUES(%i, '%s', %.2f, %.2f);"
                data = (1234, current_time, db_liter_by_min, daily_db_liter_by_min)
                cursor.execute(sql, data)
            self.db_connection.commit()
        except pymysql.MySQLError as e:
            print(f"Error inserting data into the database: {e}")

    def start_monitoring(self):
        self.setup_flow_meter()

        print("Water Flow Detection with YF-S201 Sensor")

        while True:
            self.time_start = time.time()
            self.time_end = self.time_start + self.sample_rate
            self.hz = []
            self.sample_total_time = 0

            self.read_flow_meter()

            print('-------------------------------------')
            print('Current Time:', time.asctime(time.localtime()))

            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            db_hz, db_liter_by_min, daily_db_liter_by_min = self.calculate_flow_metrics()

            print("\t", db_hz, '(hz) average')
            print('\t', db_liter_by_min, '(L/min)')
            print(round(self.total_liters, 4), "(L) today's total")
            print('-------------------------------------')

            self.insert_data_to_database(current_time, db_liter_by_min, daily_db_liter_by_min)

    def stop_monitoring(self):
        GPIO.cleanup()
        self.db_connection.close()
        print('Monitoring Stopped')

if __name__ == "__main__":
    water_flow_monitor = WaterFlowMonitor()
    water_flow_monitor.connect_to_database()
    water_flow_monitor.start_monitoring()
