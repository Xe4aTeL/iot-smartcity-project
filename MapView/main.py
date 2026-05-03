import asyncio
import collections
from kivy.app import App
from kivy_garden.mapview import MapMarker, MapView
from kivy.clock import Clock
from datasource import Datasource


class MapViewApp(App):
    def __init__(self, **kwargs):
        super().__init__()
        self.user_id = 1
        self.datasource = Datasource(user_id=self.user_id)

        # Car tracking
        self.car_marker = None
        # FIFO queue keeping exactly the last 50 states
        self.car_road_state_history = collections.deque(maxlen=50)

        # Dictionaries to keep track of static markers by their ID
        self.traffic_lights = {}
        self.parking_spaces = {}
        self.traffic_jam_icons = {}

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
        
        for point_data in new_points:
            agent_type = point_data.agent_type
            
            if agent_type == "car":
                self.handle_car_update(point_data)
            elif agent_type == "traffic_light":
                self.handle_traffic_light_update(point_data)
            elif agent_type == "parking_space":
                self.handle_parking_space_update(point_data)

    def handle_car_update(self, data):
        """
        Оновлює відображення маркера машини на мапі
        :param data: AgentData машини
        """
        if self.car_marker is None:
            self.car_marker = MapMarker(lat=data.latitude, lon=data.longitude, source="images/car.png")
            self.mapview.add_widget(self.car_marker)
        else:
            self.car_marker.lat = data.latitude
            self.car_marker.lon = data.longitude
        
        self.mapview.center_on(data.latitude, data.longitude)

        if data.road_state:
            self.car_road_state_history.append(data.road_state)
            
            if data.road_state == "bump":
                self.set_bump_marker((data.latitude, data.longitude))
            elif data.road_state == "pit":
                self.set_pothole_marker((data.latitude, data.longitude))

    def handle_traffic_light_update(self, data):
        """
        Оновлює відображення маркера світлофору на мапі
        :param data: AgentData світлофора
        """
        status = data.signal_status.lower() if data.signal_status else "red"
        image_source = f"images/traffic_{status}.png"

        if data.user_id in self.traffic_lights:
            self.traffic_lights[data.user_id].source = image_source
        else:
            marker = MapMarker(lat=data.latitude, lon=data.longitude, source=image_source)
            self.traffic_lights[data.user_id] = marker
            self.mapview.add_widget(marker)

        self.handle_traffic_jam(data)

    def handle_parking_space_update(self, data):
        """
        Оновлює відображення маркера паркоміста на мапі
        :param data: AgentData паркоміста
        """
        image_source = "images/parking_theft.png" if data.possible_theft else "images/parking_normal.png" if \
        data.occupancy_status == "Vacant" else "images/parking_occupied.png"
        
        if data.user_id in self.parking_spaces:
            self.parking_spaces[data.user_id].source = image_source
        else:
            marker = MapMarker(lat=data.latitude, lon=data.longitude, source=image_source)
            self.parking_spaces[data.user_id] = marker
            self.mapview.add_widget(marker)

    def handle_traffic_jam(self, data):
        """
        Встановлює маркер для затору
        :param data: AgentData світлофора
        """
        if data.traffic_jam:
            if data.user_id not in self.traffic_jam_icons:
                # Невеликий здвиг
                jam_marker = MapMarker(lat=data.latitude + 0.0001, lon=data.longitude + 0.0001, source="images/jam.png")
                self.traffic_jam_icons[data.user_id] = jam_marker
                self.mapview.add_widget(jam_marker)
        else:
            if data.user_id in self.traffic_jam_icons:
                jam_marker = self.traffic_jam_icons.pop(data.user_id)
                self.mapview.remove_widget(jam_marker)

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
        self.mapview = MapView(zoom=15, lat=50.4501, lon=30.5234) # Kyiv center
        return self.mapview


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(MapViewApp().async_run(async_lib="asyncio"))
    loop.close()
