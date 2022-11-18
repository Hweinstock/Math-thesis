from typing import List
from root_logger import RootLogger

from preprocessing.data import DataBase
import gtfs_kit as gk
from pathlib import Path


class GTFSData(DataBase):

    def __init__(self, filepath, city_name):
        DataBase.__init__(self, filepath, city_name)
        path = Path(filepath)
        self.feed = gk.read_feed(path, dist_units='mi')

    def read_data(self):
        return self.feed
    
    def get_trips_for_route(self, routes: List[str]):
        trips = self.read_data().trips 
        fixed_direction = 0
        trip_ids = {}
        for route in routes:
            # Look at all trips on specified route. 
            # Extract out trip_id
            trip_id_for_route= trips.loc[(trips['route_id'] == route) & (trips['direction_id'] == fixed_direction)]['trip_id'].tolist()
            unique_trip_ids = list(set(trip_id_for_route))
            if unique_trip_ids == []:
                RootLogger.log_warning(f'No trips found for id {route}')
            else:
                RootLogger.log_info(f'Successfully matched {len(unique_trip_ids)} trips to {route}')
            trip_ids[route] = unique_trip_ids
        return trip_ids
        

            
    
    
