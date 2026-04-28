import asyncio
import csv
import json
import websockets
from kivy.app import App
from kivy_garden.mapview import MapMarker, MapView
from kivy.clock import Clock
from lineMapLayer import LineMapLayer
from datasource import Datasource


class MapViewApp(App):
    def __init__(self, **kwargs):
        super().__init__()
        # додати необхідні змінні
        self.user_id = 1
        self.car_marker = None
        self.datasource = Datasource(user_id=self.user_id)

    def on_start(self):
        """
        Встановлює необхідні маркери, викликає функцію для оновлення мапи
        """
        Clock.schedule_interval(self.update, 0.1)

    def update(self, *args):
        """
        Викликається регулярно для оновлення мапи
        """
        new_points = self.datasource.get_new_points()
        
        for lat, lon, road_state in new_points:
            point = (lat, lon)
            
            # Оновлюємо позицію машини
            self.update_car_marker(point)
            
            # Додаємо маркер, якщо виявлено яму або лежачого поліцейського
            if road_state == "bump":
                self.set_bump_marker(point)
            elif road_state == "pit":
                self.set_pothole_marker(point)

    def update_car_marker(self, point):
        """
        Оновлює відображення маркера машини на мапі
        :param point: GPS координати
        """
        lat, lon = point
        
        # Якщо маркер машини ще не створений, створюємо його
        if self.car_marker is None:
            self.car_marker = MapMarker(lat=lat, lon=lon, source="images/car.png")
            self.mapview.add_widget(self.car_marker)
        else:
            self.car_marker.lat = lat
            self.car_marker.lon = lon
        
        self.mapview.center_on(lat, lon)

    def set_pothole_marker(self, point):
        """
        Встановлює маркер для ями
        :param point: GPS координати
        """
        lat, lon = point
        pothole_marker = MapMarker(lat=lat, lon=lon, source="images/pothole.png")
        self.mapview.add_widget(pothole_marker)

    def set_bump_marker(self, point):
        """
        Встановлює маркер для лежачого поліцейського
        :param point: GPS координати
        """
        lat, lon = point
        bump_marker = MapMarker(lat=lat, lon=lon, source="images/bump.png")
        self.mapview.add_widget(bump_marker)

    def build(self):
        """
        Ініціалізує мапу MapView(zoom, lat, lon)
        :return: мапу
        """
        self.mapview = MapView()
        return self.mapview

    def read_accel_data(self, filename):
        """Читає дані акселерометра з CSV-файлу"""
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                x = float(row["X"])
                y = float(row["Y"])
                z = float(row["Z"])
                self.accel_data.append((x, y, z))

    def read_gps_data(self, filename):
        """Читає GPS-координати з CSV-файлу"""
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                lat = float(row["lat"])
                lon = float(row["lon"])
                self.gps_data.append((lat, lon))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(MapViewApp().async_run(async_lib="asyncio"))
    loop.close()
