import datetime

import numpy as np
import pandas as pd

from fleetmanager.model.vehicle import FleetInventory, VehicleFactory


class FleetOptimisation:
    """
    Class used by tabu search to handle the fleet and vehicles in the connected database
    """

    def __init__(self, settings=None, km_aar=False, bike_settings=None):
        """
        Initialises the class with the settings

        Parameters
        ----------
        settings    :   dict, expects; "location": int, "dates": [start, end], "active_vehicles": dict with count
        km_aar  :   bool, if the km_aar on vehicles should be enforced
        """
        self.vf = VehicleFactory()
        self.settings = self.sort_settings(settings)
        self.km_aar = km_aar
        self.bike_settings = bike_settings
        (
            self.active_vehicles,
            self.proper,
        ) = self.get_active_vehicles()
        if len(self.proper) == 0:
            return
        self.location_total = (
            self.vf.all_vehicles[
                self.vf.all_vehicles.location.isin(self.settings["location"])
            ]
            .groupby(["location"])
            .count()
            .id.values[0]
        )

    def sort_settings(self, input_settings):
        """
        loading the settings
        """
        settings = dict(
            optimisation_date=datetime.datetime(year=2027, month=8, day=1),
            location=2,
        )
        if input_settings is not None:
            for key, value in input_settings.items():
                if value is not None:
                    settings[key] = value
        return settings

    def get_active_vehicles(self):
        """
        Method for loading the active vehicles. In order not to exhaust the resources, unique types
        of the vehicles are loaded in the uniquely value. If a car of a type that was removed because it was identical
        to a cheaper one, it's added to the translation dictionary, which bookkeeps the vehicles.

        Returns
        -------
        active_vehicles :   dict holding the currently active vehicles with key: count
        temp    :   dict, holding the unique cars available to the search
        """
        active_vehicles = {}
        temp = {}
        self.translation = {}
        temp_frame = self.vf.all_vehicles.copy()
        temp_frame = temp_frame[
            ((~temp_frame.wltp_fossil.isna()) | (~temp_frame.wltp_el.isna()))
            | (temp_frame.type_id.isin([1, 2]))
        ]
        # todo  FutureWarning: Setting an item of incompatible dtype is deprecated and will raise in a future error of
        #  pandas. Value '0' has dtype incompatible with datetime64[ns], please explicitly cast to a compatible dtype
        #  first. temp_frame.fillna(0, inplace=True)
        for column in temp_frame.columns:
            if temp_frame[column].dtype == 'datetime64[ns]':
                temp_frame[column] = temp_frame[column].fillna(pd.NaT)
            else:
                temp_frame[column] = temp_frame[column].fillna(0)
        uniquely = temp_frame[
            [
                "make",
                "model",
                "type",
                "fuel",
                "wltp_fossil",
                "wltp_el",
                "capacity_decrease",
                "co2_pr_km",
                "range",
                "sleep",
            ]
        ].drop_duplicates()
        for id, unique_car in uniquely.iterrows():
            idx = np.array(
                [
                    list(temp_frame[key] == val)
                    for key, val in unique_car.to_dict().items()
                ]
            )
            c_vehicles = temp_frame[np.all(idx.T, axis=1)]
            qualified = c_vehicles[
                c_vehicles.omkostning_aar == c_vehicles.omkostning_aar.min()
            ]
            indices = qualified.index.values
            class_id = str(indices[0])
            for index in indices:
                self.translation[str(index)] = class_id
            id = str(class_id)
            temp[id] = {"count": 0, "class": None}
            if temp[id]["class"] is None:
                temp[id]["class"] = self.vf.vmapper[id]

        active_vehicle_indexes = [
            vehicle_id for vehicle_id in self.settings["active_vehicles"].keys()
        ]
        indexes_found = temp_frame[temp_frame.id.isin(active_vehicle_indexes)]
        if len(indexes_found) != len(active_vehicle_indexes):
            return {}, {}
        for vehicle, count in self.settings["active_vehicles"].items():
            id = str(temp_frame[temp_frame.id == vehicle].index.values[0])
            if id not in self.translation:
                # adding a vehicle that was removed, because it was more expensive
                self.translation[id] = id
                temp[id] = {"count": 0, "class": self.vf.vmapper[id]}
            translated_id = self.translation[id]
            temp[translated_id]["count"] += count

        if "special_selected" in self.settings:
            if len(self.settings["special_selected"]) > 0:
                only_selected_and_active = {}
                selected_frame = temp_frame[temp_frame.id.apply(lambda x: int(x) in self.settings["special_selected"])]
                for selected_vehicle in selected_frame.itertuples():
                    id_ = str(selected_vehicle.Index)
                    if id_ not in self.translation:
                        self.translation[id_] = id_
                    translated_id = self.translation[id_]
                    only_selected_and_active[translated_id] = {
                        "count": 0,
                        "class": self.vf.vmapper[id_],
                    }

                for vehicle_id, vehicle_settings in temp.items():
                    if vehicle_settings["count"] > 0:
                        only_selected_and_active[vehicle_id] = vehicle_settings
                temp = only_selected_and_active

        return active_vehicles, temp

    def build_fleet_simulation(
        self, solution, name="fleetinventory", days=1, exception=False
    ):
        """
        Method for building and initialising a fleet for simulation

        Parameters
        ----------
        solution    :   dict, solution to build
        name    :   string, name for the fleet

        Returns
        -------
        fleet   :   FleetInventory

        """
        fleet = FleetInventory(self.vf, name=name, settings=self.settings)
        for vehicle in self.proper.keys():
            if vehicle in solution:
                setattr(fleet, vehicle, solution[vehicle])
            else:
                setattr(fleet, vehicle, 0)
        fleet.initialise_fleet(
            km_aar=self.km_aar if exception is False else False,
            bike_settings=self.bike_settings,
            sub_time=self.settings["sub_time"],
            days=days,
            settings=self.settings,
        )
        return fleet
