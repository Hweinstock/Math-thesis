from typing import List 
import pandas as pd 
import os

from transit_network.routes import SimpleRoute, GTFSRoute, simplify_route
from transit_network.stops import Stop 
from transit_network.trips import GTFSTrip, simplify_trip
from transit_network.shapes import ShapePoint, get_shapes_from_df

from root_logger import RootLogger


class TransitNetwork:
    
    route_file_headers = ['route_id' ,'route_short_name', 'route_long_name', 'route_type']
    trips_file_headers = ['route_id', 'service_id', 'trip_id', 'direction_id', 'shape_id', 'trip_headsign']
    stop_times_file_headers = ['trip_id', 'arrival_time', 'depature_time', 'stop_id', 'stop_sequence']
    shapes_file_headers = ['shape_id', 'shape_pt_lat', 'shape_pt_lon', 'shape_pt_sequence']

    def __init__(self, routes: List[SimpleRoute]):
        self.routes = routes

    @property
    def trips(self) -> List[GTFSTrip]:
        all_trips = []
        for route in self.routes:
            route_trips = route.trips 
            all_trips += route_trips
        
        return all_trips 
    
    @property
    def stops(self) -> List[Stop]:
        all_stops = {}
        for trip in self.trips:
            for stop in trip.stops:
                if stop not in all_stops:
                    all_stops[stop] = True 
        return list(all_stops.keys())

    @property 
    def ridership(self):
        #413064996.3834995
        #144576773
        #72288386
        return sum([s.ridership for s in self.stops])
    
    def __str__(self):
        num_routes = len(self.routes)
        num_trips = len(self.trips)
        num_stops = len(self.stops)

        return f'(TransitNetwork[routes: {num_routes}, trips: {num_trips}, stops: {num_stops}, ridership: {self.ridership}])'


    def to_gtfs(self, folder='output_gtfs'):

        def rows_to_file(rows, headers, filename):
            df = pd.DataFrame(rows, columns=headers)
            raw_csv_text = df.to_csv(index=False)
            text_file = os.path.join(folder, filename+'.txt')

            RootLogger.log_debug(f'Outputting gtfs file to {text_file} in directory {folder}.')

            with open(text_file, 'w') as output:
                output.write(raw_csv_text)

        if not os.path.exists(folder):
            os.makedirs(folder)

        route_rows = [r.to_gtfs_row() for r in self.routes]
        rows_to_file(route_rows, self.route_file_headers, 'routes')

        trip_rows = [t.to_gtfs_row() for t in self.trips]
        rows_to_file(trip_rows, self.trips_file_headers, 'trips')

        shapes_rows = []
        for trip in self.trips:
            shapes_rows += trip.get_shapes_rows()
        rows_to_file(shapes_rows, self.shapes_file_headers, 'shapes')

        stop_rows = []
        for s in self.stops:
            stop_rows += s.to_gtfs_rows()
        rows_to_file(stop_rows, self.stop_times_file_headers, 'stops')
        



        


def determine_transfers(routes: List[GTFSRoute]):
    # Determine Transfers for each route
    all_stop_transfers = {}
    for route in routes:
        route_stops = route.get_all_stops()
        for stop in route_stops:
            stop_id = stop.get_id()
            # Already seen this stop
            if stop_id in all_stop_transfers:
                stop_obj = all_stop_transfers[stop_id]
                # noticed that stop_id were duplicated. 
                # Wnder if this is because routes in two directions repeat stops on way back?
                if stop_id not in stop_obj.routes:
                    RootLogger.log_info(f'Found transfer at stop {stop_id} on route {route.id}.')
                    stop_obj.add_transfer_route(route.id)
            else:
                all_stop_transfers[stop.id] = stop
                stop.add_transfer_route(route.id)

    return all_stop_transfers
        
def create_network_from_GTFSRoutes(routes: List[GTFSRoute], shapes_df: pd.DataFrame) -> TransitNetwork:

    all_stop_transfers = determine_transfers(routes)

    # Update stop objects so that they all have transfer points set. 
    simple_routes = []
    for route in routes:
        RootLogger.log_info(f'Simplifying trips for route {route.id}')
        new_trips = []
        for trip in route.trips:
            new_stops = [all_stop_transfers[stop[0].get_id()] for stop in trip.stops if all_stop_transfers[stop[0].get_id()].is_transfer()]
            new_stop_ids = [s.get_id() for s in new_stops]

            # We want to add endpoint to the trips
            first_stop = trip.stops[0][0]
            first_stop_id = first_stop.get_id()
            last_stop = trip.stops[-1][0]
            last_stop_id = last_stop.get_id()

            # We check if the id is in the stops because id accounts for parent stops
            if first_stop_id not in new_stop_ids:
                new_stops = [first_stop] + new_stops
            
            if last_stop_id not in new_stop_ids:
                new_stops += [last_stop]

            # Debugging Information
            num_stops = len(trip.stops)
            num_new_stops = len(new_stops)

            if num_new_stops > num_stops:
                RootLogger.log_warning(f'Simplifying trip {trip.id} increased # of stops from {num_stops} to {num_new_stops}')
            else:
                RootLogger.log_debug(f'Trip {trip.id} reduced number of stops from {num_stops} to {num_new_stops}')

            # Shape Information for each trip. 
            shape_id = trip.shape_id
            shape_points = get_shapes_from_df(shapes_df.loc[shapes_df['shape_id'] == shape_id])
            
            RootLogger.log_info(f'Identified {len(shape_points)} shape points for trip {trip.id}.')

            new_trip = simplify_trip(trip, new_stops, route.ridership, shape_points)
            new_trips.append(new_trip)
            

            # move ridership data to the stop level. 
            # assign_ridership_to_stops(new_stops, route.ridership)
            # trip.set_stops(new_stops, shapes_df)
            # trip.stops = new_stops 

        simple_route = simplify_route(route, new_trips)
        simple_routes.append(simple_route)

    return TransitNetwork(simple_routes) 

