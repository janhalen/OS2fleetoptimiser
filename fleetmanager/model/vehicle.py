import datetime

import numpy as np
import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm.query import Query

from fleetmanager.data_access import Cars, FuelTypes, VehicleTypes, engine_creator
from fleetmanager.model.tco_calculator import TCOCalculator

# initialise global mappers
vehicle_mapping = {
    -1: "Ikke tildelt",
    0: "Fossil-bil",
    1: "El-bil",
    2: "El-cykel",
    3: "Cykel",
}


class VehicleModel:
    """General vehicle model. Not directly instantiated but specific vehicle models inherit from it"""

    co2emission_per_km = None  # g/km
    max_distance_per_day = None
    omkostning_aar = None
    location = None
    vcprkm = 0
    qampo_gr = 0
    vehicle_type_number = None
    yearly_set = False
    sub_time = 1

    def __init__(self, name=None, vehicle_id=None):
        self.vehicle_id = vehicle_id
        self.timeslots = []
        self.name = name
        self.days = 0
        self.end_time = datetime.datetime(year=1900, month=1, day=1)
        self.timedelta = datetime.timedelta(minutes=self.sub_time)

    def set_timestamps(self, new_timestamps):
        """Initailize timeslot of vehicle to match timestamps.

        parameters
        ----------
        new_timestamp : array of timestamps
        """
        self.timestamps = new_timestamps

        # initialise timeslots here
        self.timeslots = np.zeros((len(self.timestamps),), dtype=int)
        self.days = (
            (
                self.timestamps[-1].to_timestamp() - self.timestamps[0].to_timestamp()
            ).total_seconds()
            / 3600
            / 24
        )

    def book_trip(self, trip, use_slot=True):
        """Function for trying to book trip on vehicle

        parameters
        ----------
        trip : pandas row with a trip

        returns
        -------
        booked : boolean, True if vehicle is booked on this vehile
        accept : boolean, True if it can accept the type of trip
        available: boolean, True if the vehicle is available in this timeperiod
        """
        # try to book on this vehicle. Returns a tuple with (accept, available). Return value 'accept' is true if
        # the vehicle can perform this trip and 'available' is true if it is available in this

        # test acceptance of trip
        accept = self.accept_trip(trip)
        if use_slot:
            try:
                start_slot = int(trip.start_slot)
            except:
                start_slot = np.NaN

            try:
                end_slot = int(trip.end_slot)
            except:
                end_slot = np.NaN

            if (start_slot is np.NaN) or (end_slot is np.NaN):
                print(f"start_slot={start_slot}, end_slot={end_slot}")
                return False, False, False

            # lookup in timeslots list
            try:
                if any(self.timeslots[start_slot : (end_slot + 1)] > 0):
                    available = False
                else:
                    available = True
            except:
                print(start_slot)
                print(end_slot)
                available = False

            # collect and book
            if accept and available:
                # vehicle accept trip and vehicle available
                self.timeslots[start_slot : (end_slot + 1)] = trip.tripid
                return True, accept, available
            else:
                # vehicle not available or cannot accept trip
                if accept and self.vehicle_type_number in [1, 2, 3]:
                    self.trips.pop(-1)
                    self.milage_left += trip.distance
                if accept and self.vehicle_type_number in [0, 1]:
                    self.counter -= trip.distance
                return False, accept, available
        else:
            available = False
            if trip.start_time > self.end_time:
                #  the car is not booked
                available = True

            if accept and available:
                self.end_time = trip.end_time + self.timedelta
                return True, accept, available
            else:
                if accept and self.vehicle_type_number in [1, 2, 3]:
                    self.trips.pop(-1)
                    self.milage_left += trip.distance
                if accept and self.vehicle_type_number in [0, 1]:
                    self.counter -= trip.distance
                return False, accept, available

    def bypass_book(self, trip, use_slot=True):
        if use_slot:
            start_slot = int(trip.start_slot)
            end_slot = int(trip.end_slot)
            self.timeslots[start_slot : (end_slot + 1)] = trip.tripid
        return True, True, True

    def accept_trip(self, trip):
        """function that returns true if the given type of trip is possible for the vehicle given length, duration,
        milage_left should be overwritten for each type of vehicle

        parameters
        ----------
        trip : pandas row with a trip
        """
        return True

    def percentage_accept(self):
        """
        Method that ensures that bike trips accepted gets as close to the input percentage as possible
        """
        accepted = sum(self.accept_record)
        checked = len(self.accept_record)
        up_or_down = [
            abs(self.percentage - ((accepted + 1) / (checked + 1))),
            abs(self.percentage - ((accepted) / (checked + 1))),
        ]
        closest = np.argsort(up_or_down)
        return True if closest[0] == 0 else False

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.vehicle_id}, name={self.name})"

    @classmethod
    def class_info(self):
        return f"(co2emission_per_km={self.co2emission_per_km}, max_distance_per_day={self.max_distance_per_day}, omkostning_aar={self.omkostning_aar})"

    def print_info(self):
        """Print info. Mostly for debugging"""
        print(self.name)
        print(self.timestamps)
        print(self.timeslots)


class Car(VehicleModel):
    """Class for representing a car"""

    vehicle_type_number = 0
    max_distance_per_day = 9999
    co2emission_per_km = 150
    wltp_fossil = 20
    fuel = "benzin"
    counter = 0
    yearly_allowance = 999999
    yearly_set = False

    def __init__(self, *args, **kwargs):
        """
        initialising a car with its properties from the frame
        calculates a tco average in order to approximate the variable cost pr km used by optimisation algorithms
        """
        super().__init__(*args, **kwargs)

        if pd.isna("co2emission_per_km") is False:
            self.co2emission_per_km = getattr(self, "co2_pr_km")

        tco = TCOCalculator(
            koerselsforbrug=10000,
            drivmiddel=self.fuel,
            bil_type=self.fuel,
            antal=1,
            evalueringsperiode=1,
            fremskrivnings_aar=0,
            braendstofforbrug=self.wltp_fossil,
            elforbrug=0,
            leasingydelse=0,
        )
        self.vcprkm = tco.tco_average / 10000
        self.qampo_gr = tco.ekstern_miljoevirkning(sum_it=True)[0] * 100

        if pd.isna(getattr(self, "km_aar")) is False:
            self.yearly_allowance = getattr(self, "km_aar") * 1.15
            self.yearly_set = True

    def accept_trip(self, trip):
        """
        Returns true if the trip is accepted, and false if the yearly_set is true and the yearly_allowance is exceeded
        """
        if self.yearly_set:
            if (self.counter + trip.distance) / self.days * 365 > self.yearly_allowance:
                return False
        self.counter += trip.distance
        return True


class ElectricCar(VehicleModel):
    """Class for representing an electric car"""

    vehicle_type_number = 1
    max_distance_per_day = 500
    co2emission_per_km = 0
    wltp_el = 200
    fuel = "el"
    sleep = 7
    counter = 0
    yearly_allowance = 999999
    yearly_set = False

    def __init__(self, *args, **kwargs):
        """
        initialising a car with its properties from the frame
        calculates a tco average in order to approximate the variable cost pr km used by optimisation algorithms
        """
        super().__init__(*args, **kwargs)

        # simple battery indicator
        if pd.isna(getattr(self, "range")) is False:
            self.max_distance_per_day = getattr(self, "range")
            capacity_decrease = getattr(self, "capacity_decrease")
            if pd.isna(capacity_decrease) is False:
                self.max_distance_per_day = (
                    self.max_distance_per_day * (100 - capacity_decrease) / 100
                )
        if not hasattr(self, "sleep") or self.sleep is None:
            self.sleep = ElectricCar.sleep

        if pd.isna(getattr(self, "km_aar")) is False:
            self.yearly_allowance = getattr(self, "km_aar") * 1.15
            self.yearly_set = True

        self.milage_left = self.max_distance_per_day
        self.trips = []

        tco = TCOCalculator(
            koerselsforbrug=10000,
            drivmiddel="el",
            bil_type="el",
            antal=1,
            evalueringsperiode=1,
            fremskrivnings_aar=0,
            braendstofforbrug=0,
            elforbrug=self.wltp_el,
            leasingydelse=0,
        )
        self.vcprkm = tco.tco_average / 10000
        self.qampo_gr = tco.ekstern_miljoevirkning(sum_it=True)[0] * 100

    def accept_trip(self, trip):
        """
        Returns true if the trip is accepted, and false if its declined
        The electrical car will only accept if the following is true
            distance for trip must be less than milage left
            vehicle must still be idle for at least self.sleep hours pr. 24 hours
        """
        # todo trip related segments determine the acceptance if the trip exceed 24 - sleep hours
        # todo for new rt, check when it was last used..
        segment_trip_check = False
        time_good = True
        if len(self.trips):
            start_of_period = self.trips[0]
            if (trip.start_time - start_of_period[0]).days >= 1:
                # reset the milage and the trips record
                self.milage_left = self.max_distance_per_day
                self.trips = []

        if len(self.trips):
            # check that the car can sleep at least 7 hours from last reset
            # hours when the car has been idle
            idles = [
                (forward[0] - current[1]).total_seconds() / 3600
                for forward, current in zip(
                    self.trips[1:] + [(trip.start_time, None)], self.trips
                )
            ]
            # indication if the route begins before last end
            if any([time < 0 for time in idles]):
                time_good = False
            in_between_wait = sum(idles)
            start = self.trips[0][0]
            timeleft = ((24 * 3600) - (trip.end_time - start).total_seconds()) / 3600
            if in_between_wait + timeleft < self.sleep:
                time_good = False
        else:
            timeleft = ((24 * 3600) - (trip.end_time - trip.start_time).total_seconds()) / 3600
            time_good = timeleft > self.sleep
        # if the trip distance is greater than the milage left or trip duration is longer than max allowed trip duration

        if hasattr(trip, "trip_segments") and trip.distance > self.milage_left or time_good is False:
            segment_trip_check = True
            total_travelled = 0

            temporary_km_left = self.milage_left
            for k, segment in enumerate(trip.trip_segments):
                if temporary_km_left - segment.get("distance") < 0:
                    return False

                temporary_km_left -= segment.get("distance")
                total_travelled += segment.get("distance")
                if k != len(trip.trip_segments) - 1 and (trip.trip_segments[k+1].get("start_time") - segment.get("end_time")).total_seconds() / 3600 > self.sleep:
                    temporary_km_left = self.max_distance_per_day

            self.milage_left = temporary_km_left

        # accept if enough km left on car and update milage_left
        if (self.milage_left - trip.distance > 0 and time_good) or segment_trip_check:
            if self.yearly_set:
                if (
                    self.counter + trip.distance
                ) / self.days * 365 > self.yearly_allowance:
                    return False
            if segment_trip_check is False:
                self.milage_left = self.milage_left - trip.distance
            self.trips.append((trip.start_time, trip.end_time))
            self.counter += trip.distance
            return True
        else:
            # trip is too long to accept or timing not good
            return False


class Bike(VehicleModel):
    """Class for representing a bike"""

    vehicle_type_number = 3
    max_distance_per_day = 20
    co2emission_per_km = 0
    max_distance_pr_trip = 5
    allowed_driving_time_slots = []
    max_time_slot = 0
    percentage = 100
    bike_speed = 8
    skip_kmh_check = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if pd.isna(getattr(self, "range")) is False:
            self.max_distance_per_day = getattr(self, "range")
        # todo update to := notation
        if pd.isna(getattr(self, "bike_speed")) is False:
            self.bike_speed = getattr(self, "bike_speed")
        self.milage_left = self.max_distance_per_day
        self.trips = []
        self.accept_record = []
        self.percentage /= 100

    def accept_trip(self, trip):
        """
        Returns true if the trip is accepted, and false if its declined
        The bike will only accept if the following is true
            distance for trip must be less than milage left
            trip start - and end time must be within the allowed driving slot
        """
        if len(self.trips):
            start_of_period = self.trips[0]
            if (trip.start_time - start_of_period[0]).days >= 1:
                # reset the milage and the trips record
                self.milage_left = self.max_distance_per_day
                self.trips = []

        if (
            trip.end_time - trip.start_time
        ).total_seconds() / 3600 > self.max_time_slot:
            return False
        elif (
            trip.distance < self.max_distance_pr_trip
            and self.milage_left - trip.distance > 0
            and (self.skip_kmh_check or trip["km/h"] < self.bike_speed)
        ):
            for start, end in self.allowed_driving_time_slots:
                if all(
                    [
                        trip.start_time.time() >= start.time(),
                        trip.start_time.time() <= end.time(),
                        trip.end_time.time() <= end.time(),
                        trip.end_time.time() >= start.time(),
                    ]
                ):
                    accepted = self.percentage_accept()
                    self.accept_record.append(accepted)
                    if accepted:
                        self.milage_left = self.milage_left - trip.distance
                        self.trips.append((trip.start_time, trip.end_time))
                        return True
                    else:
                        return False
            return False
        else:
            # trip is too long to accept
            return False


class ElectricBike(VehicleModel):
    """Class for representing an electric bike"""

    vehicle_type_number = 2
    max_distance_per_day = 50
    co2emission_per_km = 0
    max_distance_pr_trip = 5
    allowed_driving_time_slots = []
    max_time_slot = 0
    percentage = 100
    electrical_bike_speed = 12
    skip_kmh_check = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if pd.isna(getattr(self, "range")) is False:
            self.max_distance_per_day = getattr(self, "range")
        if pd.isna(getattr(self, "electrical_bike_speed")) is False:
            self.electrical_bike_speed = getattr(self, "electrical_bike_speed")
        self.milage_left = self.max_distance_per_day
        self.trips = []
        self.accept_record = []
        self.percentage /= 100

    def accept_trip(self, trip):
        """
        Returns true if the trip is accepted, and false if its declined
        The bike will only accept if the following is true
            distance for trip must be less than milage left
            trip start - and end time must be within the allowed driving slot
        """
        # accept if enough km left on car
        if len(self.trips):
            start_of_period = self.trips[0]
            if (trip.start_time - start_of_period[0]).days >= 1:
                # reset the milage and the trips record
                self.milage_left = self.max_distance_per_day
                self.trips = []

        if (
            trip.end_time - trip.start_time
        ).total_seconds() / 3600 > self.max_time_slot:
            return False
        elif (
            trip.distance < self.max_distance_pr_trip
            and self.milage_left - trip.distance > 0
            and (self.skip_kmh_check or trip["km/h"] < self.electrical_bike_speed)
        ):
            for start, end in self.allowed_driving_time_slots:
                if all(
                    [
                        trip.start_time.time() >= start.time(),
                        trip.start_time.time() <= end.time(),
                        trip.end_time.time() <= end.time(),
                        trip.end_time.time() >= start.time(),
                    ]
                ):
                    accepted = self.percentage_accept()
                    self.accept_record.append(accepted)
                    if accepted:
                        self.milage_left = self.milage_left - trip.distance
                        self.trips.append((trip.start_time, trip.end_time))
                        return True
                    else:
                        return False
            return False
        else:
            # trip is too long to accept
            return False


class Unassigned(VehicleModel):
    """Class for representing an unassigned vehicle. Used for computing capacity."""

    vehicle_type_number = -1
    max_distance_per_day = 0
    co2emission_per_km = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def accept_trip(self, trip):
        # always accept
        return True


def VehicleClassGenerator(name, vehicle_type=Car):
    """Class used to create vehicle types from a dynamic list of vehicle models"""

    def __init__(self):
        vehicle_type.__init__(self, name[: -len("Class")])

    new_vehicle_class = type(name, (vehicle_type,), {"__init__": __init__})
    return new_vehicle_class


class VehicleFactory:
    """Class for containing the vehicle types that are used in the simulation"""

    def __init__(self, load_self=True, unique_vehicles=None):
        if load_self:
            self.engine = engine_creator()
            fuel_query = (
                Query([FuelTypes.refers_to, FuelTypes.id.label("fuelId")])
            ).subquery()
            car_query = (
                Query(
                    [
                        FuelTypes.name.label("fuel_name"),
                        fuel_query,
                        Cars,
                        VehicleTypes.name.label("type_name"),
                    ]
                )
                .join(Cars, func.coalesce(Cars.fuel, 10) == fuel_query.c.fuelId)
                .join(FuelTypes, FuelTypes.id == fuel_query.c.refers_to)
                .join(VehicleTypes, Cars.type == VehicleTypes.id)
                .statement
            )
            self.all_vehicles = pd.read_sql(
                car_query,
                self.engine,
            )
            self.all_vehicles["type_id"] = self.all_vehicles.type
            self.all_vehicles.drop(
                ["refers_to", "fuelId", "fuel", "type"], axis=1, inplace=True
            )
            self.all_vehicles["type"] = self.all_vehicles.type_name
            self.all_vehicles["fuel"] = self.all_vehicles.fuel_name

            self.all_vehicles.dropna(subset=["omkostning_aar"], inplace=True)
            # to force weighting in tabu
            self.all_vehicles["range"] = self.all_vehicles.apply(
                lambda row: 9999 if pd.isna(row.range) and row.type == 'fossilbil' else row.range,
                axis=1
            )
            self.unique_vehicles = self.all_vehicles
        else:
            self.unique_vehicles = pd.DataFrame(unique_vehicles)
            self.unique_vehicles = self.unique_vehicles.set_index(self.unique_vehicles.id)

        # type to class mapper
        self.type_mapper = {
            "cykel": Bike,
            "elcykel": ElectricBike,
            "fossilbil": Car,
            "elbil": ElectricCar,
            "Unassigned": Unassigned,
        }

        self.vmapper = {
            str(vehicle.Index): VehicleClassGenerator(
                " ".join(
                    [vehicle.make, "" if pd.isna(vehicle.model) else vehicle.model]
                ).strip(),
                self.type_mapper[vehicle.type],
            )
            for vehicle in self.unique_vehicles.itertuples()
        }

        self.load_options()
        self.vmapper = {
            vehicle_name: vehicle_object
            for vehicle_name, vehicle_object in self.vmapper.items()
        }

    def get_new_vehicle(self, vtype, name, vehicle_id):
        """Function for creating new vehicles

        parameters
        ----------
        vtype : string, vtype as key into vmapper
        name : string, name of vehicle
        vehicle_id : int, id of vehicle
        returns
        -------
        """
        new_vehicle = self.vmapper[vtype]()
        new_vehicle.name = name
        new_vehicle.original_name = vtype
        new_vehicle.vehicle_id = vehicle_id
        return new_vehicle

    def load_options(self):
        """Load options from option file"""

        # loop over selection and push settings to vehicle types
        for vehicle_model in self.unique_vehicles.itertuples():
            for key, data in vehicle_model._asdict().items():
                setattr(self.vmapper[str(vehicle_model.Index)], key, data)

    def __str__(self):
        out = ""
        for key, val in self.vmapper.items():
            out = out + f"{val.__name__}{val.class_info()}\n"
        return out


class FleetInventory:
    """Class for containing a fleet of vehicles.

    parameters
    ----------
    models: available models type model.VehicleFactoryd
    name: string, name of the fleet, typically 'simulation' or 'current'
    """

    def __init__(self, models, name="fleetinventory", settings=None):
        self.models = models

        self.name = name
        self.vehicle_types = []
        self.sort_index = {}
        self.set_count()
        self.initialise_fleet(settings=settings)

    def set_count(self):
        for vehicle_name in self.models.vmapper.keys():
            setattr(self, vehicle_name, 0)
            self.vehicle_types.append(vehicle_name)

    def set_sort_index(self, name=None):
        sort_names = [name] if name else self.sort_index.keys()
        for unique_vehicle in sort_names:
            index_start, index_end = self.sort_index.get(unique_vehicle, (None, None))
            order = np.argsort(
                list(
                    map(
                        lambda vehicle:
                        0 if vehicle.typeid not in [3, 4] else vehicle.counter,
                        self.vehicles[index_start:index_end]
                    )
                )
            )
            self.vehicles[index_start:index_end] = [self.vehicles[index_start:index_end][il] for il in order]

    def initialise_fleet(
        self, km_aar=False, bike_settings=None, sub_time=1, days=1, settings=None
    ):
        """
        Initialise fleet by sorting on co2e priority, this results in vehicles being loaded in the following order
        bike, electical bike (wltp), electrical car (wltp), car (wltp)
        """
        if settings is None and hasattr(self, "settings"):
            settings = getattr(self, "settings")
        elif settings is None:
            settings = {}

        # vehicle type id for later reference
        vehicle_type_ids = []

        # clear list of vehicles
        self.vehicles = []
        sorting = []
        qampo_gr = []
        vcprkm = []
        el_udledning = settings.get("el_udledning", 0.09)
        benzin_udledning = settings.get("benzin_udledning", 2.52)
        diesel_udledning = settings.get("diesel_udledning", 2.98)
        hvo_udledning = settings.get("hvo_udledning", 0.894)

        for vehicle_name, vehicle_object in self.models.vmapper.items():
            if all(
                [pd.isna(vehicle_object.wltp_fossil), pd.isna((vehicle_object.wltp_el))]
            ):
                qampo_gr.append(0)
                vcprkm.append(0)
                sorting.append(vehicle_name)
                vehicle_type_ids.append(vehicle_object.type_id)
                continue
            qmpgr = TCOCalculator(
                drivmiddel=vehicle_object.fuel,
                bil_type=vehicle_object.fuel,
                koerselsforbrug=10000,
                braendstofforbrug=vehicle_object.wltp_fossil,
                elforbrug=vehicle_object.wltp_el,
                evalueringsperiode=1,
                fremskrivnings_aar=0,
                antal=1,
                leasingydelse=0
                if pd.isna(vehicle_object.omkostning_aar)
                else vehicle_object.omkostning_aar,
                diesel_udledning=diesel_udledning,
                benzin_udledning=benzin_udledning,
                el_udledning=el_udledning,
                hvo_udledning=hvo_udledning
            )
            vcprkm.append(qmpgr.tco_average / 10000)
            qampo_gr.append(qmpgr.ekstern_miljoevirkning(sum_it=True)[0] * 100)
            sorting.append(vehicle_name)
            vehicle_type_ids.append(vehicle_object.type_id)

        sorl = np.lexsort((vcprkm, qampo_gr))
        vnamesorted = [sorting[a] for a in sorl]
        typesorted = [vehicle_type_ids[a] for a in sorl]

        for vehicle_name, k, typeid in zip(vnamesorted, sorl, typesorted):
            for n in range(getattr(self, vehicle_name)):
                v = self.models.get_new_vehicle(
                    vtype=vehicle_name,
                    name=f"{vehicle_name}_{n+1}",
                    vehicle_id=self.get_total(),
                )
                if n == 0 and self.name != 'current':
                    start_index = len(self.vehicles)

                if km_aar is False:
                    v.yearly_set = False
                if bike_settings is not None:
                    for key, value in bike_settings.items():
                        setattr(v, key, value)
                    bike_speed = bike_settings.get("bike_speed")
                    electrical_bike_speed = bike_settings.get("electrical_bike_speed")

                    setattr(v, "bike_speed", 8 if pd.isna(bike_speed) else bike_speed)
                    setattr(v, "electrical_bike_speed", 12 if pd.isna(electrical_bike_speed) else electrical_bike_speed)

                setattr(v, "sub_time", sub_time)
                setattr(v, "timedelta", datetime.timedelta(minutes=sub_time))
                setattr(v, "days", days)
                setattr(v, "typeid", typeid)
                self.vehicles.append(v)

                if n + 1 == getattr(self, vehicle_name) and self.name != "current":
                    self.sort_index[vehicle_name] = (start_index, start_index + n + 1)

    def copy_bike_fleet(self, name="fleetinventory"):
        """
        Convenience function used in intelligent simulation for copying only the bike fleet as the Qampo algorithms
        does not accept bikes and electrical bikes
        """
        bikes = {}
        for vehicle in self.vehicles:
            if vehicle.vehicle_type_number not in [2, 3]:
                continue
            vehicle_name = str(vehicle.Index)
            if vehicle_name not in bikes:
                bikes[vehicle_name] = 0
            bikes[vehicle_name] += 1
        new_fleetinventory = FleetInventory(self.models, name=name)
        for vehicle_name, count in bikes.items():
            setattr(new_fleetinventory, vehicle_name, count)
        new_fleetinventory.initialise_fleet()
        return new_fleetinventory

    def print_timetable(self):
        """Print timetable for fleet. Mostly for debugging."""

        print(f"Timetable for fleet: {self.name}")
        print(f"{'Timestamp':>20}", end="")
        for v in self:
            print(f"{v.name[:2]+v.name[-2:]:>6}", end="")
        print("")

        for i, t in enumerate(self.timestamps):
            print(f"{str(t):>20}", end="")

            for v in self:
                tripid = v.timeslots[i]
                if tripid == 0:
                    tripid = "."
                print(f"{tripid:>6}", end="")
            print("")

    def get_total(self):
        return len(self.vehicles)

    def set_timestamps(self, timestamps):
        """set timestamps for all vehicles"""
        self.timestamps = timestamps

        # loop over all vehicles and set the timestamps
        for v in self.__iter__():
            v.set_timestamps(self.timestamps)

    def __iter__(self):
        # iterator that first traverses bikes, ebikes, ecars and then cars
        yield from self.vehicles
