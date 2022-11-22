from typing import List 

from root_logger import RootLogger

def stop_from_stop_row_data(row):
    id = row['stop_id']
    stop_name = row['stop_name']
    if 'parent_station' in row:
        parent_station = row['parent_station']
    else:
        parent_station = None 
    
    return Stop(id= id, name=stop_name, parent_id=parent_station)


class Stop:

    def __init__(self, id, name, parent_id=None):
        self.id = id 
        self.name = name
        self.parent_id = parent_id
        self.matches_trips = []
        self.routes = []
        self.ridership = 0
    
    def add_transfer_route(self, new_route: str):
        self.routes += [new_route]

    def is_transfer(self):
        if len(self.routes) == 0:
            RootLogger.log_warning(f'Stop {self.id} with parent {self.parent_id} has no routes!')
        return len(self.routes) > 1
    
    def get_id(self):
        if self.parent_id is not None:
            return self.parent_id 
        else:
            return self.id 


    def __str__(self) -> str:
        return f'(stop_id: {self.id}, stop_name: {self.name}, parent_stop: {self.parent_id}, routes: {self.routes})'
    
