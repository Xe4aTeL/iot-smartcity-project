from csv import reader
from datetime import datetime
from domain.accelerometer import Accelerometer
from domain.gps import Gps
from domain.gyroscope import Gyroscope
from domain.aggregated_data import AggregatedData
import config


class FileDatasource:
    def __init__(
        self,
        accelerometer_filename: str,
        gps_filename: str,
        gyroscope_filename: str,
    ) -> None:
        self.accelerometer_filename = accelerometer_filename
        self.gps_filename = gps_filename
        self.gyroscope_filename = gyroscope_filename
        self.accelerometer_file = None
        self.gps_file = None
        self.gyroscope_file = None
        self.accelerometer_reader = None
        self.gps_reader = None
        self.gyroscope_reader = None
        
        self.gps_update_interval = 11
        self.read_counter = 0
        self.cached_gps = None
        
        self.accelerometer_data = []
        self.gps_data = []
        self.gyroscope_data = []

    def read(self) -> AggregatedData:
        """Метод повертає дані отримані з датчиків"""
        try:
            accelerometer_row = next(self.accelerometer_reader)
            gyroscope_row = next(self.gyroscope_reader)
            
            if self.read_counter % self.gps_update_interval == 0:
                gps_row = next(self.gps_reader)
                self.cached_gps = Gps(float(gps_row[0]), float(gps_row[1]))
            
            self.read_counter += 1
            
        except StopIteration:
            self.stopReading()
            self.startReading()
            accelerometer_row = next(self.accelerometer_reader)
            gyroscope_row = next(self.gyroscope_reader)
            
            if self.read_counter % self.gps_update_interval == 0:
                gps_row = next(self.gps_reader)
                self.cached_gps = Gps(float(gps_row[0]), float(gps_row[1]))
            
            self.read_counter += 1

        return AggregatedData(
            Accelerometer(int(accelerometer_row[0]), int(accelerometer_row[1]), int(accelerometer_row[2])),
            self.cached_gps,
            Gyroscope(float(gyroscope_row[0]), float(gyroscope_row[1]), float(gyroscope_row[2])),
            datetime.utcnow(),
            config.USER_ID,
        )

    def startReading(self, *args, **kwargs):
        """Метод повинен викликатись перед початком читання даних"""
        self.accelerometer_file = open(self.accelerometer_filename, 'r')
        self.gps_file = open(self.gps_filename, 'r')
        self.gyroscope_file = open(self.gyroscope_filename, 'r')
        
        self.accelerometer_reader = reader(self.accelerometer_file)
        self.gps_reader = reader(self.gps_file)
        self.gyroscope_reader = reader(self.gyroscope_file)
        
        next(self.accelerometer_reader)
        next(self.gps_reader)
        next(self.gyroscope_reader)
        
        self.read_counter = 0
        gps_row = next(self.gps_reader)
        self.cached_gps = Gps(float(gps_row[0]), float(gps_row[1]))

    def stopReading(self, *args, **kwargs):
        """Метод повинен викликатись для закінчення читання даних"""
        if self.accelerometer_file:
            self.accelerometer_file.close()
        if self.gps_file:
            self.gps_file.close()
        if self.gyroscope_file:
            self.gyroscope_file.close()
