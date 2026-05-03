from csv import reader
from datetime import datetime
from domain.accelerometer import Accelerometer
from domain.gps import Gps
from domain.gyroscope import Gyroscope
from domain.traffic_light import TrafficLight
from domain.parking_space import ParkingSpace
from domain.aggregated_data import AggregatedData
import config
import random


class FileDatasource:
    def __init__(
        self,
        agent_type: str,
        accelerometer_filename: str,
        gps_filename: str,
        gyroscope_filename: str,
        trafficlight_filename: str,
        parkingspace_filename: str,
    ) -> None:
        self.agent_type = agent_type
        self.pos = (config.LATITUDE, config.LONTITUDE)

        # Filenames
        self.accelerometer_filename = accelerometer_filename
        self.trafficlight_filename = trafficlight_filename
        self.parkingspace_filename = parkingspace_filename
        self.gps_filename = gps_filename
        self.gyroscope_filename = gyroscope_filename

        # File pointers and readers
        self.accelerometer_file = None
        self.accelerometer_reader = None
        self.gps_file = None
        self.gps_reader = None
        self.gyroscope_file = None
        self.gyroscope_reader = None
        self.trafficlight_file = None
        self.trafficlight_reader = None
        self.parkingspace_file = None
        self.parkingspace_reader = None
        
        # For car
        self.gps_update_interval = 11
        self.read_counter = 0
        self.cached_gps = None
        

    def read_car(self) -> AggregatedData:
        """Метод повертає дані отримані з датчиків машини"""
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
            return self.read_car()

        return AggregatedData(
            config.USER_ID,
            self.agent_type,
            datetime.utcnow(),

            Accelerometer(int(accelerometer_row[0]), int(accelerometer_row[1]), int(accelerometer_row[2])),
            self.cached_gps,
            Gyroscope(float(gyroscope_row[0]), float(gyroscope_row[1]), float(gyroscope_row[2])),

            None, None,
        )


    def read_traffic_light(self) -> AggregatedData:
        """Метод повертає дані отримані з датчиків світлофору"""
        try:
            trafficlight_row = next(self.trafficlight_reader)
            
        except StopIteration:
            self.trafficlight_file.seek(0)
            next(self.trafficlight_reader, None)
            trafficlight_row = next(self.trafficlight_reader)

        return AggregatedData(
            config.USER_ID,
            self.agent_type,
            datetime.utcnow(),

            None, None, None,

            TrafficLight(
                    float(self.pos[0]),
                    float(self.pos[1]),
                    int(trafficlight_row[0]),
                    float(trafficlight_row[1]),
                    int(trafficlight_row[2]),
                    str(trafficlight_row[3]),
                ),

            None,
        )


    def read_parking_space(self) -> AggregatedData:
        """Метод повертає дані отримані з датчиків паркомісця"""
        try:
            parkingspace_row = next(self.parkingspace_reader)
            
        except StopIteration:
            self.parkingspace_file.seek(0)
            next(self.parkingspace_reader, None)
            parkingspace_row = next(self.parkingspace_reader)

        return AggregatedData(
            config.USER_ID,
            self.agent_type,
            datetime.utcnow(),

            None, None, None, None,

            ParkingSpace(
                    float(self.pos[0]),
                    float(self.pos[1]),
                    str(parkingspace_row[0]),
                    float(parkingspace_row[1]),
                ),
        )


    def read(self) -> AggregatedData:
        """Метод повертає дані отримані з датчиків машини"""
        if self.agent_type == "car":
            return self.read_car()
        if self.agent_type == "traffic_light":
            return self.read_traffic_light()
        if self.agent_type == "parking_space":
            return self.read_parking_space()


    def skip_random_lines(self, file_reader, max_skip=50):
        skips = random.randint(0, max_skip)
        for _ in range(skips):
            try:
                next(file_reader)
            except StopIteration:
                break


    def startReading(self, *args, **kwargs):
        """Метод повинен викликатись перед початком читання даних"""
        if self.agent_type == "car":
            self.accelerometer_file = open(self.accelerometer_filename, 'r')
            self.gps_file = open(self.gps_filename, 'r')
            self.gyroscope_file = open(self.gyroscope_filename, 'r')
        
            self.accelerometer_reader = reader(self.accelerometer_file)
            self.gps_reader = reader(self.gps_file)
            self.gyroscope_reader = reader(self.gyroscope_file)
        
            next(self.accelerometer_reader, None)
            next(self.gps_reader, None)
            next(self.gyroscope_reader, None)
        
            self.read_counter = 0
            gps_row = next(self.gps_reader)
            self.cached_gps = Gps(float(gps_row[0]), float(gps_row[1]))

        elif self.agent_type == "traffic_light":
            self.trafficlight_file = open(self.trafficlight_filename, 'r')
            self.trafficlight_reader = reader(self.trafficlight_file)
            next(self.trafficlight_reader, None)
            self.skip_random_lines(self.trafficlight_reader)

        elif self.agent_type == "parking_space":
            self.parkingspace_file = open(self.parkingspace_filename, 'r')
            self.parkingspace_reader = reader(self.parkingspace_file)
            next(self.parkingspace_reader, None)
            self.skip_random_lines(self.parkingspace_reader)


    def stopReading(self, *args, **kwargs):
        """Метод повинен викликатись для закінчення читання даних"""
        if self.accelerometer_file:
            self.accelerometer_file.close()
        if self.gps_file:
            self.gps_file.close()
        if self.gyroscope_file:
            self.gyroscope_file.close()
        if self.trafficlight_file:
            self.trafficlight_file.close()
        if self.parkingspace_file:
            self.parkingspace_file.close()
