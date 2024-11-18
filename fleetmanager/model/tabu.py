import datetime
import math
import operator
import time
from itertools import cycle, islice

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sqlalchemy.orm.query import Query

from fleetmanager.data_access.db_engine import engine_creator
from fleetmanager.data_access.dbschema import RoundTrips
from fleetmanager.model.dashfree_utils import get_emission
from fleetmanager.model.vehicle_optimisation import FleetOptimisation

try:
    from fleetmanager.model.exceptions import NoCarsSelected, NoSolutionFound
except Exception as e:
    pass
from fleetmanager.model.model import (
    ConsequenceCalculator,
    FleetManager,
    Simulation,
    Trips,
)
from fleetmanager.model.tco_calculator import TCOCalculator
from fleetmanager.model.trip_generator import extract_peak_day
from fleetmanager.model.vehicle import Unassigned


class TabuSearch:
    """
    Class for handling the tabu search algorithm. Sets a number of parameters before the algorithm can be started
    by calling the "run" method. In addition to the below-mentioned parameters (init), the following attributes are set.

    minimum_cars is calculated in least_viable to find the minimum number of cars needed in the solution
    breakpoint_solution is the solution that is least viable - least number of cars needed in the solution
    total_trips is the whole set of trips selected based on the location id and dates
    slack is not yet used, but is intended as an adjustable parameter to allow solution to have undriven trips below a
        specific distance; max_distance_for_undriven
    bins is not yet used, but will be used when slack is used to bin the undriven trips - will punish trips above the
        threshold heavily
    dummy_trips is used in the least_viable and search to more efficiently search as oposed if this was done on the
        whole set.
    vehicle_properties is used in the tabu search to retrieve the cost/objective of each vehicle based on the eval_km
    cheap_list is an ordered list of the most expensive vehicles first. Used in the least_viable function which assumes
        that the most expensive is the one with the best capacity.
    vehicle2id, id2vehicle, vehicle2type are used in the algortihm all over to enable indexing from unique vehicles to
        an id and vice versa
    best_objective_value will hold the current best_objective_value, is first set in the run_current_setup when the
        current solution is simulated
    report value for holding the search report to be pulled by the frontend.
    """

    def __init__(
        self,
        fleetoptimiser: FleetOptimisation,
        location: int,
        dates,
        eval_km=5000,
        fixed_antal: int = None,
        co2e_goal: int = math.inf,
        expense_goal: int = math.inf,
        weight: int = 5,
        intelligent: bool = False,
        km_aar: bool = False,
        use_timeslots: bool = False,
        settings=None,
        current_vehicles=None,
        engine=None,
    ):
        """
        Sets up the needed attributes for the search.

        Parameters
        ----------
        fleetoptimiser  :   FleetOptimisation class, used to handle the selected vehicles and the available vehicles for
                            the tabu search to select
        location    :   int, location id of the selected location
        dates   :   list of date times, [start time, end time] for the selected simulation period.
                    Defines from when to when the trips will be pulled
        eval_km :   The initial evaluation km. Defines how many kilometer should be the basis for the tco calculation to
                    extract the objective/fitness values, the expense and emission values for the vehicles
        fixed_antal :   int, if minimum number of cars/electrical cars should be fixed
        co2e_goal   :   int, the co2e emission goal, input should be a percentage 0-100, the current co2e will be the basis
                        calculated in run_current_setup
        expense_goal    :   int, the addition og subtractive amount of DKK from the current expense, which will be the basis
                            calculated in run_current_setup
        weight  :   int, the weight between expense and co2e, 5 is defined as balance, 0 prioritises cheaper solutions and
                    10 prioritises cheap co2e solutions.
        intelligent :   bool, should the tabu search use intelligent allocation (Qampo) in the solution simulation
        km_aar  :   bool, should the simulation constrain vehicle booking when the yearly km allowance has been reached.
                    Not available with intelligent simulation.
        """
        self.fallback_undriven = None
        self.fallback_solutions = None
        self.qualified = None
        self.solutions = None
        self.location = location
        self.co2e_goal = co2e_goal
        self.expense_goal = expense_goal
        self.fixed_antal = fixed_antal
        self.weight = weight
        self.intelligent = intelligent
        self.km_aar = km_aar
        self.fleet_optimisation = fleetoptimiser
        self.dates = dates
        self.eval_km = eval_km
        self.settings = settings
        if engine is None:
            self.engine = engine_creator()
        if settings is None:
            self.settings = {}
        self.current_vehicles = current_vehicles
        if current_vehicles is None:
            self.current_vehicles = []
        self.use_timeslots = use_timeslots

        self.minimum_cars = 0
        self.breakpoint_solution = None
        self.total_trips = self.initialise_real()
        if self.total_trips is None:
            return
        if (
            self.settings.get("slack", 0) > 0
            and self.settings.get("max_undriven", 0) > 0
        ):
            self.slack = int(self.settings["slack"])
            self.max_distance_for_undriven = int(self.settings["max_undriven"])
        else:
            self.slack = round(len(self.total_trips.trips) * 0.01)
            if self.slack > 5:
                self.slack = 5
            self.max_distance_for_undriven = 20
        self.bins = list(range(0, self.max_distance_for_undriven + 1, 1)) + [9999]
        self.dummy_trips = self.initialise_trips()
        self.vehicle_properties = self.calculate_vehicle_cost()
        self.cheap_list = self.vehicle_ordered()
        self.vehicle2id, self.id2vehicle, self.vehicle2type = self.mapper()
        self.best_objective_value = None
        self.report = None

    def run(self):
        """
        Method for handling the run of the tabu search. First calls the least_viable to get the least number of
        cars needed in the final solutions. It then gets the initial objective value, which is the current setup.
        The current solution is then "simulated" to get the current expense and co2e in order to calculate the
        expense - and co2e goal. Finally, the "control" method is run, which handles the tabu search and assigns
        the result to report.
        """
        self.least_viable()
        (
            self.best_solution,
            self.best_solution_vehicle_types,
            self.fixed,
        ) = self.start_solution()
        if len(self.fixed) == 0:
            return False
        self.best_objective_value = self.objective_value(self.best_solution)
        self.run_current_setup()
        self.search()
        return True

    def run_current_setup(self):
        """
        Method responsible for running the current setup on the whole selected trip set.
        It will take all the vehicles that were active in the selected time period no matter if they were not selected
        in the simulation setup. This is done in order to get the "real" value, otherwise one could select no vehicles
        and have an expense on 0, which would make it infeasible for the search to improve.

        Initialises the fleet with the active vehicles in the selected time period
        Runs a "real" simulation on the whole trip set
        Calculates the expense - and co2e goal based on the input values
        """
        fm = FleetManager()
        current_solution = fm.vehicle_factory.all_vehicles[
            fm.vehicle_factory.all_vehicles.id.isin(self.current_vehicles)
        ]
        for vehicle in current_solution.index.values:
            setattr(fm.current_fleet, str(vehicle), 1)
        days = (
            (
                self.total_trips.trips.iloc[-1].start_time
                - self.total_trips.trips.iloc[0].start_time
            ).total_seconds()
            / 3600
            / 24
        )
        fm.current_fleet.initialise_fleet(days=days, settings=self.settings)

        cur_results = self.real_simulation(
            fleet=fm.current_fleet,
            small_set=False,
            special_name="current",
            intelligent=False,
        )
        self.cur_result = cur_results
        new_goal_expense = self.expense_goal + cur_results[0]
        new_goal_co2e = (100 - self.co2e_goal) / 100 * cur_results[1]
        self.expense_goal = new_goal_expense
        self.co2e_goal = new_goal_co2e

    def vehicle_ordered(self):
        """
        Orders the vehicle in range specific and most expensive to least expensive. Useful for the least viable function
        as well as ordering the electrical bikes, bikes and unassigned type last.
        """
        weight = {
            vehicle: self.objective_value({vehicle: 1})
            for vehicle in self.vehicle_properties.keys()
        }
        # unique ranges sorted
        unique_ranges = list(
            set(
                map(
                    lambda vehicle: vehicle.get("class").range, self.fleet_optimisation.proper.values()
                )
            )
        )
        unique_ranges = sorted(set([0 if pd.isna(a) else a for a in unique_ranges]), reverse=True)

        # unique ranges to vehicle index sorted
        unique_ranges_index = [
            [str(v.get("class").Index) for v in filter(
                lambda vehicle: 0 == raekkevidde if pd.isna(vehicle.get("class").range) else vehicle.get("class").range == raekkevidde,
                self.fleet_optimisation.proper.values()
            )] for raekkevidde in unique_ranges]

        # local sorting on range groups
        range_weight_sorting = [
            v for b in [
                [a[0] for a in sorted(
                    {index: weight[index] for index in index_group}.items(), key=operator.itemgetter(1), reverse=True
                )] for index_group in unique_ranges_index] for v in b
        ] + ["unassigned"]

        return range_weight_sorting

    def start_solution(self):
        """
        Method for generating the start solution and building the structure for the search.
        Generates a start solution with all the cars that a fixed due to a running lease that does not end before
        the selected time period.

        Returns:
            solution    :   dictionary - id to count of the solution
            vehicle_types   :   dictionary - vehicle type to count of solution
            fixed   :   list - list of n available cars with value that defines how many of that index are fixed in the
                        final solution
        """
        # the start solution must at least include minimum # cars fossil/el, and prefill the "unchangeable"

        # fill in the unchangeable LOCKED
        solution = {}
        for vehicle, vehicle_props in self.fleet_optimisation.proper.items():
            solution[vehicle] = vehicle_props["count"]

        # fill in the rest
        for vehicle in self.vehicle_properties.keys():
            if vehicle not in solution:
                solution[vehicle] = 0

        solution["unassigned"] = 0

        fixed = [solution[self.id2vehicle[k]] for k in range(len(solution))]
        indexes_that_hold_cars = [
            self.vehicle2id[vehicle]
            for vehicle in self.cheap_list
            if self.vehicle2type[vehicle] in ["elbil", "fossilbil"]
        ]

        if len(indexes_that_hold_cars) == 0:
            return {}, {}, []

        self.car_index = indexes_that_hold_cars[-1]

        # check that the start solution adhere to the least viable solution
        while (
            sum(
                [
                    count
                    for vehicle, count in solution.items()
                    if self.vehicle2type[vehicle] in ["fossilbil", "elbil"]
                ]
            )
            < self.minimum_cars
        ):
            solution[self.cheap_list[0]] += 1

        vehicle_types = {
            "cykel": 0,
            "elcykel": 0,
            "elbil": 0,
            "fossilbil": 0,
            "unassigned": 0,
        }
        for vehicle, count in solution.items():
            vehicle_type = self.vehicle2type[vehicle]
            vehicle_types[vehicle_type] += count
        return solution, vehicle_types, fixed

    def calculate_vehicle_cost(self):
        """
        Calculates the vehicle attributes: co2, co2e, cost, obj and expense based on the eval_km.
        Uses the TCOCalculator based on the tool "tco-vaerktoej-motorkoeretoejer" created by POGI.
        In tabu search the objective value is used and based on the weight;
        (normalised cost) + (normalised co2e * weight)

        Returns
        -------
        vehicles_dict   :   a dictionary; id of vehicle to its calculated attributes

        """
        vehicles_dict = {}
        props = []
        vehicles = []
        for vehicle, vehicle_props in self.fleet_optimisation.proper.items():
            vehicle_class = vehicle_props["class"]
            tco = TCOCalculator(
                drivmiddel=vehicle_class.fuel,
                bil_type=vehicle_class.fuel,
                koerselsforbrug=self.eval_km,
                braendstofforbrug=vehicle_class.wltp_fossil,
                elforbrug=vehicle_class.wltp_el,
                diesel_udledning=self.settings.get("diesel_udledning", 2.98),
                hvo_udledning=self.settings.get("hvo_udledning", 0.894),
                benzin_udledning=self.settings.get("benzin_udledning", 2.52),
                el_udledning=self.settings.get("el_udledning", 0.09),
                evalueringsperiode=1,
            )
            co2e, samfund = tco.ekstern_miljoevirkning(sum_it=True)
            expense = vehicle_class.omkostning_aar + tco.driftsomkostning + samfund
            cost = expense / self.eval_km
            co2 = (
                self.eval_km * vehicle_class.co2_pr_km / 1000
                if pd.isna(vehicle_class.co2_pr_km) is False
                else 0
            )
            props.append(
                {
                    "co2": co2,
                    "co2e": co2e,
                    "cost": cost,
                    "obj": max(1, co2e) * max(1, cost),
                    "expense": expense,
                }
            )
            vehicles.append(vehicle)

        cost = [vehicle["cost"] for vehicle in props]
        co2e = [vehicle["co2e"] for vehicle in props]
        scaled = MinMaxScaler().fit_transform([(a, b) for a, b in zip(cost, co2e)])

        shifted = [(v, i[0], i[1]) for v, i in zip(vehicles, scaled)]

        obj = lambda cost_, co2e_, weight: cost_ + (co2e_ * weight)
        # other used score weightings:
        # obj = lambda cost_, co2e_, weight: (cost_ * (10 - weight) + co2e_ * weight) / 10
        # obj = lambda cost_, co2e_, weight: (co2e_ * (10 + weight) + cost_ * (10 - weight)) / 10

        for vkey, cost, co2e in shifted:
            vehicles_dict[vkey] = {
                "norm_cost": cost,
                "norm_co2e": co2e,
                "norm_obj": obj(cost, co2e, self.weight),
            }
        vehicles_dict["unassigned"] = {"norm_obj": 0}
        return vehicles_dict

    def get_expenses(self):
        """
        Method currently unused. Useful for providing product solution to attribute matrix for analytical resolution.
        """
        obj_array, expense_array, co2e_array, cost_array = [], [], [], []
        for k in range(len(self.vehicle_properties)):
            vehicle_properties = self.vehicle_properties[self.id2vehicle[k]]
            obj_array.append(vehicle_properties["obj"])
            expense_array.append(vehicle_properties["expense"])
            co2e_array.append(vehicle_properties["co2e"])
            cost_array.append(vehicle_properties["cost"])
        return (
            np.array(obj_array),
            np.array(expense_array),
            np.array(co2e_array),
            np.array(cost_array),
        )

    def objective_value(self, solution, test=False):
        """
        Method for providing the objective value of specific solution.

        Parameters
        ----------
        solution    :   dictionary of the solution to get the objective value of
        test    :   if the solution also should be tested

        Returns
        -------

        """
        # if slacks becomes editable 'twv' becomes relevant
        twv = 1
        if test:
            neighbour_co2e, neighbour_cost, twv = self.real_simulation(solution)
            solution = {self.id2vehicle[k]: count for k, count in enumerate(solution)}
        elif type(solution) is list:
            solution = {self.id2vehicle[k]: count for k, count in enumerate(solution)}

        n_sum = sum(
            [
                self.vehicle_properties[vehicle]["norm_obj"] * count
                for vehicle, count in solution.items()
                if count > 0
            ]
        )
        return n_sum

    def mapper(self):
        """
        Method for generating mappers used all over the class in order to index the proper vehicle

        Returns
        -------
        vehicle_name_to_id  :   dictionary, name from vehicle_optimisation.FleetOptimisation to the assigned id
        id_to_vehicle_name  :   dictionary, id to the name from vehicle_optimisation.FleetOptimisation
        vehicle2type    :   dictionary, name from vehicle_optimisation.FleetOptimisation to the vehicle type

        """
        vehicle_name_to_id = {
            vehicle_name: k for k, vehicle_name in enumerate(self.cheap_list)
        }

        id_to_vehicle_name = {
            k: vehicle_name for vehicle_name, k in vehicle_name_to_id.items()
        }

        vehicle2type = {
            vehicle_name: vehicle_props["class"].type
            for vehicle_name, vehicle_props in self.fleet_optimisation.proper.items()
        }
        vehicle2type["unassigned"] = "unassigned"
        return vehicle_name_to_id, id_to_vehicle_name, vehicle2type

    def drivability_search(
        self,
        solution,
        down=True,
        old=None,
        numbers_checked=None,
        iteration=0,
        max_iter=100,
        start=0,
        car_index=0,
    ):
        """
        Recursive method to find the least number of cars needed to satisfy the capacity needed for the trips pulled
        Starts with the number of fixed cars on one particular index, checks if the solution satisfies. If yes, choose
        the median number between the current checked and highest value that did not satisfy the need. If no, choose the
        median number between the current checked and the lowest value that did satisfy the need.

        Parameters
        ----------
        solution    :   the solution that should be checked
        down    :   if the next solution should go down
        old :   the previously checked solution
        numbers_checked :   a dictionary holding the number of vehicles and a bool for satisfaction
        iteration   :   number of iterations used to stop searching at max_iter
        max_iter    :   max number of iterations allowed
        start   :   the start solution number - always 0, which yelds a numbers_checked dict {0: False}

        Returns
        -------
        Bool for least viability found, solution for least viability
        """
        iteration += 1
        vehicle = self.cheap_list[car_index]
        if numbers_checked is None:
            numbers_checked = {start: self.driving_checking({vehicle: start})}
        if old is None:
            old = solution[vehicle]
        if down:
            bottom = (
                max(
                    [
                        number
                        for number, viable in numbers_checked.items()
                        if viable is False
                    ]
                    + [0]
                )
                if numbers_checked
                else 0
            )
            numbers = list(range(bottom, solution[vehicle] + 1))
        else:
            numbers = list(range(solution[vehicle], old + 1))

        middle = math.floor(np.median(numbers))
        if middle == old:
            middle += 1
        new_solution = {vehicle: middle}
        drivable = self.driving_checking(new_solution)
        numbers_checked[middle] = drivable

        # found breaking point?
        checked = np.array(list(numbers_checked.keys()))
        checked.sort()
        difference = checked[1:] - checked[:-1]
        terminate = [
            k + 1
            for k, (index, diff) in enumerate(zip(range(len(checked) + 1), difference))
            if diff == 1
            and numbers_checked[checked[index]] is False
            and numbers_checked[checked[index + 1]] is True
        ]

        if terminate:
            chec = checked[terminate[0]]
            while True:
                _, _, twv = self.real_simulation([chec])
                if twv == 0:
                    break
                chec += 1

            new_solution = {vehicle: chec}
            return True, new_solution
        elif iteration > max_iter:
            return False, new_solution

        # check if we should go lower or higher
        if drivable:
            new_solution = self.drivability_search(
                new_solution,
                down=True,
                numbers_checked=numbers_checked,
                iteration=iteration,
                max_iter=max_iter,
                car_index=car_index,
            )
        else:
            old = middle
            new_solution = self.drivability_search(
                new_solution,
                down=False,
                old=old,
                numbers_checked=numbers_checked,
                iteration=iteration,
                max_iter=max_iter,
                car_index=car_index,
            )

        return new_solution

    def least_viable(self):
        """
        Method to control the least viability search to find the minimum vehicles needed to satisfy the number of
        trips. Sets the starts to max_vehicles which is the current number of vehicles based on the time period times
        1.5. If the breakpoint is not found, the minimum cars are set to current number times 1.5.
        """
        # get the number of cars in current solution
        # todo make initial guess, based on current vehicles, not location specifics
        max_vehicles = round(self.fleet_optimisation.location_total * 1.5)
        if self.fixed_antal:
            self.minimum_cars = self.fixed_antal

        # construct the most expensive solution
        most_expensive_solution = {self.cheap_list[0]: max_vehicles}
        # find the minimum number of cars required to handle the driving requirement
        breakpoint_found, self.breakpoint_solution = self.drivability_search(
            most_expensive_solution, start=1
        )
        breakpoint_el_found = None
        if breakpoint_found:
            # the least viable with electrical vehicles
            breakpoint_number = int(list(self.breakpoint_solution.values())[0])
            numbers_checked = {breakpoint_number: False}
            el_index = [
                k
                for k, vehicle_name in enumerate(self.cheap_list)
                if self.vehicle2type[vehicle_name] == "elbil"
            ]
            if el_index:
                most_expensive_solution = {
                    self.cheap_list[el_index[0]]: breakpoint_number + 1
                }

                breakpoint_el_found, breakpoint_el_solution = self.drivability_search(
                    most_expensive_solution,
                    numbers_checked=numbers_checked,
                    car_index=el_index[0],  # the most expensive electrical vehicle
                    down=False,  # start the search by going up
                    iteration=96,  # to limit the search to 4 checks
                )
                if breakpoint_el_found:
                    breakpoint_el_found = int(list(breakpoint_el_solution.values())[0])
            self.minimum_cars = breakpoint_number
        else:
            self.minimum_cars = round(
                len(
                    self.fleet_optimisation.vf.all_vehicles[
                        self.fleet_optimisation.vf.all_vehicles.location.isin(self.location)
                    ]
                )
                * 1.5
            )
        if breakpoint_el_found is None or breakpoint_el_found is False:
            breakpoint_el_found = self.minimum_cars + 3
        self.breakpoint_el_found = breakpoint_el_found

    def driving_checking(self, solution):
        """
        Method called by drivability_search to test the solution. Will use the input solution and test against
        the dummy trip set to efficiently simulate.

        Parameters
        ----------
        solution    :   dict, key: vehicle, value: count

        Returns
        -------
        bool    :   is solution able to satisfy the need with no unallocated trips
        """
        fleet = self.fleet_optimisation.build_fleet_simulation(
            solution, days=1, exception=True
        )
        simulation = Simulation(
            self.dummy_trips,
            fleet,
            None,
            tabu=True,
            intelligent_simulation=self.intelligent,
            timestamps_set=True,
            timeslots=self.use_timeslots,
        )
        if self.use_timeslots:
            simulation.timestamps = self.dummy_trips.timestamps
        simulation.run()
        drivable = (
            False
            if self.calculate_slack(simulation) > 0
            else True
        )
        return drivable

    def calculate_slack(self, simulation, fleet_name="fleetinventory"):
        """
        Method used when calculating the allowed slack. Right now slack is set to 0, however one can allow
        that a specific number of trips below a certain distance length is unallocated. The unallocated trips
        that fall in the last bin will be punished by 10 as opposed to 1 - accounting for 10 unallocated trips.

        Parameters
        ----------
        simulation  :   model.Simulation object - with the trips frame after the simulation has been run
        fleet_name  :   the name of the fleet, in order to index the proper column

        Returns
        -------
        twv     :   int, the number of trips without a vehicle
        """
        twv = simulation.trips.trips[simulation.trips.trips[f"{fleet_name}_type"] == -1]
        if len(twv) > 0:
            # punish longer trips than self.max_distance_for_undriven allows
            tip = twv.groupby(pd.cut(twv.distance, bins=self.bins), observed=False).size()
            bin_length = len(self.bins) - 1
            multiplier = 1 if self.slack == 0 else self.slack
            twv = sum(
                a if k + 1 < bin_length else a * multiplier for k, a in enumerate(tip)
            )
        else:
            twv = 0
        return twv

    def real_simulation(
        self,
        solution=None,
        small_set=True,
        fleet=None,
        special_name=None,
        intelligent=False,
    ):
        """
        Method performing simulation and returning the consequences

        Parameters
        ----------
        solution    :   list, input solution if no fleet is defined, index is vehicle id, value is count.
        small_set   :   bool, if the small dummy_set should be used.
        fleet   :   vehicle.fleetinventory class if solution is none
        special_name    :   string, defining the name and booked column from Simulation.trips.trips
        intelligent :   bool, intelligent simulation (Qampo)

        Returns
        -------
        expense, co2e, number of trips without vehicles
        """
        key = "fle"
        fleet_name = "fleetinventory"
        if special_name:
            key = special_name[:3]
            fleet_name = special_name

        if small_set:
            trip_set = self.dummy_trips
            n = len(trip_set.trips)
        else:
            trip_set = self.total_trips
            n = len(trip_set.trips)
        trip_set.trips["current"] = n * [Unassigned()]
        trip_set.trips["current_type"] = n * [-1]
        trip_set.trips["simulation"] = n * [Unassigned()]
        trip_set.trips["simulation_type"] = n * [-1]
        if pd.isna(fleet):
            days = (
                (
                    self.total_trips.trips.iloc[-1].start_time
                    - self.total_trips.trips.iloc[0].start_time
                ).total_seconds()
                / 3600
                / 24
            )
            solution = {self.id2vehicle[k]: count for k, count in enumerate(solution)}
            fleet = self.fleet_optimisation.build_fleet_simulation(
                solution, name=fleet_name, days=days
            )
        simulation = Simulation(
            trip_set,
            fleet,
            None,
            tabu=True,
            intelligent_simulation=intelligent,
            timestamps_set=True,
            timeslots=self.use_timeslots,
        )

        if self.use_timeslots:
            simulation.timestamps = trip_set.timestamps
        simulation.run()
        setattr(
            simulation.fleet_manager,
            f"{fleet_name}_fleet",
            simulation.fleet_manager.vehicles,
        )
        cq = ConsequenceCalculator(states=[fleet_name], settings=self.settings)
        cq.compute(simulation, None, [0, 1])
        twv = self.calculate_slack(simulation, fleet_name=fleet_name)

        savings_key = cq.consequence_table["keys"].index(
            "Samlet omkostning [kr/år]"
        )
        co2e_key = cq.consequence_table["keys"].index(
            "POGI CO2-ækvivalent udledning [CO2e]"
        )
        savings = cq.consequence_table[f"{key}_values"][savings_key]
        co2e_savings = cq.consequence_table[f"{key}_values"][co2e_key]

        if small_set is False:
            return (savings, co2e_savings, twv)
        return (
            cq.consequence_table[f"{key}_values"][-3],
            cq.consequence_table[f"{key}_values"][-1],
            twv,
        )

    def initialise_real(self):
        """
        Initialises and prepares the whole trip set defined by the location and selected time period

        Returns
        -------
        dataframe of roundtrips
        """
        rt = Trips(dates=self.dates, location=self.location, vehicles=self.current_vehicles, engine=self.engine, shifts=self.settings.get("shifts", None))

        if len(rt.trips) == 0:
            return None
        rt.trips.drop(["current", "current_type", "simulation", "simulation_type"], axis=1, inplace=True)
        rt.trips["tripid"] = rt.trips.index.values
        rt.trips["fleetinventory"] = len(rt.trips) * [Unassigned()]
        rt.trips["fleetinventory_type"] = -np.ones((len(rt.trips),), dtype=int)

        if self.use_timeslots:  # is rarely used and much slower
            time_resolution = pd.Timedelta(minutes=1)
            start_day = rt.trips.start_time.min().date()
            end_day = rt.trips.end_time.max().date() + pd.Timedelta(days=1)
            timestamps = pd.period_range(start_day, end_day, freq=time_resolution)
            rt.set_timestamps(timestamps)
        return rt

    def initialise_trips(self):
        """
        Initialises and prepares a dummy set for efficient search and test
        Pulls the peak day in the selected time period. Assumes that a fleet that can satisfy a peak day would be able
        to satisfy the whole period.

        Returns
        -------
        dataframe of roundtrips for the peak day
        """
        peak_day = extract_peak_day(self.total_trips.trips)
        peak_day["tripid"] = peak_day.index.values
        peak_day["id"] = peak_day.tripid
        peak_day[["start_location_id", "department"]] = 0
        peak_day["fleetinventory"] = len(peak_day) * [Unassigned()]
        peak_day["fleetinventory_type"] = -np.ones((len(peak_day),), dtype=int)
        peak_day[
            [
                "driver_name",
                "car_id",
                "start_latitude",
                "start_longitude",
                "end_latitude",
                "end_longitude",
            ]
        ] = None
        pd_t = Trips(dataset=peak_day)
        if self.use_timeslots:
            time_resolution = pd.Timedelta(minutes=1)
            start_day = pd_t.trips.start_time.min().date()
            end_day = pd_t.trips.end_time.max().date() + pd.Timedelta(days=1)
            timestamps = pd.period_range(start_day, end_day, freq=time_resolution)
            pd_t.set_timestamps(timestamps)

        return pd_t

    def build_tabu_structure(self, allow_removal):
        """
        Essential method for the tabu search that generates a structure to hold all the possible moves.
        For all indexes in the self.fixed list two moves are made; +1 and -1.
        E.g. a database holding 3 unique cars with one fixed car (a car that cannot be removed due to continued lease),
        could look like:
                [0, 0, 1]
        and allow_removal = False
        would yield a tabu structure:
            {
                (0, 1): {"tabu_time": 0, "objective_value": math.inf},
                (0, -1): {"tabu_time": 0, "objective_value": math.inf},
                (1, 1): {"tabu_time": 0, "objective_value": math.inf},
                (1, -1): {"tabu_time": 0, "objective_value": math.inf},
                (2, 1): {"tabu_time": 0, "objective_value": math.inf},
                (2, -1): {"tabu_time": 0, "objective_value": math.inf},
            }

        Parameters
        ----------
        allow_removal   :   bool, is the search allowed to remove vehicles from the fixed. Useful if current solution
                            holds, to the simulation, redundant vehicles, i.e. if there are more vehicles than needed
                            in the current solution to satisfy the need.

        Returns
        -------
        dict of key move (index, +1/-1) value (dict attributes)
        """
        ts = {}
        for k, c in enumerate(self.fixed):
            if allow_removal and c == 0:
                continue
            for a in range(2):
                mov = -1 if a == 0 else 1
                ts[(k, mov)] = {"tabu_time": 0, "objective_value": math.inf}
        return ts

    def get_nabo(self, c_solution, allow_removal=True, min_cars=None):
        """
        Method for generating neighbours to the current solution. I.e. from the tabu structure generate the
        specific solution from the current solution and the move. It checks if the solution satisfies the minimum
        number of cars criteria.

        Parameters
        ----------
        c_solution  :   list, the current solution from which new solutions will be build
        allow_removal   :   bool, is it allowed to remove vehicles from the fixed cars
        min_cars    :   int, the minimum number of cars that should be in the solution

        Returns
        -------
        generator, that yields the possible solutions.

        """
        if min_cars is None:
            min_cars = self.minimum_cars
        min_suffice = lambda sol: sum(sol[: self.car_index + 1]) >= min_cars
        if allow_removal:
            for k, count in enumerate(c_solution):
                if self.fixed[k] == 0:
                    continue
                if count > 0:
                    cop = c_solution.copy()
                    cop[k] -= 1
                    if min_suffice(cop):
                        yield (k, -1), cop
                elif count < self.fixed[k]:  # allow climb again
                    cop = c_solution.copy()
                    cop[k] += 1
                    yield (k, 1), cop
        else:
            for k, count in enumerate(c_solution):
                if count == 0:
                    cop = c_solution.copy()
                    cop[k] = 1
                    yield (k, 1), cop
                else:
                    if k > self.car_index and min_suffice(c_solution) is False:
                        continue
                    if self.fixed[k] == count:
                        cop = c_solution.copy()
                        cop[k] = count + 1
                        yield (k, 1), cop
                    else:
                        for a in range(2):
                            cop = c_solution.copy()
                            mov = -1 if a == 0 else 1
                            cop[k] = count + mov
                            if a:
                                yield (k, mov), cop
                            else:
                                if min_suffice(cop):
                                    yield (k, mov), cop

    def swap_move(self, solution, move):
        """
        Method used to make the move from the solution to the best move selected.

        Parameters
        ----------
        solution    :   list, solution index to number, e.g. [0,0,1,2,1,5,0]
        move    :   tuple, the move from the tabu structure to make, e.g. (5, -1)

        Returns
        -------
        list, the new solution with the move made
        """
        cop = solution.copy()
        cop[move[0]] += move[1]
        return cop

    def tabu_search(self, min_cars=None, add_tenure=0):
        """
        The tabu search algorithm.

        Responsible for search the space for solutions and recording the immediate best solutions.
        From the input min_cars it's calculated if the solutions should prioritise removing or adding vehicles
        to the current solution. From this information, the tabu structure is build and search starts. It's always
        pushed towards a better objective value, and by punishing the unallocated trips it's desired by the search
        to go into spaces where this condition is satisfied.

        For new and better solutions the record is saved, and the time of the move is recorded such that we don't
        fall into the same space over and over again. The move is however allowed if it improves the global best
        objective value.

        Parameters
        ----------
        min_cars    :   the minimum number of cars needed in the generated solutions.

        Returns
        -------
        dict, holding the recorded best solution during the search.
        """
        if min_cars is None:
            min_cars = self.minimum_cars
        best_solution = self.fixed.copy()
        divide = 1 if sum(self.fixed) == 0 else sum(self.fixed)
        allow_remove = True if min_cars < sum(self.fixed) else False
        if min_cars / divide <= 1:
            tenure = min(3, len([a for a in self.fixed if a > 0]))
        else:
            tenure = 3
        tenure += add_tenure

        # todo
        #  diversify the results, more robust objective function, validate free rides; 0 co2e, very cheap/owned,

        # get the structure and possible moves for settings
        tabu_structure = self.build_tabu_structure(allow_remove)
        current_solution = best_solution
        best_objvalue = math.inf
        current_objvalue = best_objvalue

        # save the solutions so we don't have to re-run the obj method
        saved_solutions = dict()
        saved_solutions[tuple(current_solution)] = current_objvalue

        iteration = 1
        stop_iter = 0
        start = time.time()
        while stop_iter < 200 and time.time() - start < 20:
            generated = False
            moves = tabu_structure.keys()

            # reset the moves, so that we don't repeat the same moves
            for move in moves:
                tabu_structure[move]["objective_value"] = math.inf

            # iterate over the possible moves to get it's associated move objective value
            for move, candidate_solution in self.get_nabo(
                current_solution, allow_removal=allow_remove, min_cars=min_cars
            ):
                if move not in tabu_structure:
                    continue
                generated = True

                # skip getting objective value for already checked solutions
                if tuple(candidate_solution) not in saved_solutions:
                    candidate_objvalue = self.objective_value(candidate_solution)
                else:
                    candidate_objvalue = saved_solutions[tuple(candidate_solution)]
                tabu_structure[move]["objective_value"] = candidate_objvalue

            # break if there are no more moves to be made
            if generated is False:
                break

            # check the possible steps
            while True:
                # if no moves are allowed because tabu_time exceeds iteration we increment and break
                if all(
                    [a["objective_value"] == math.inf for a in tabu_structure.values()]
                ):
                    iteration += 1
                    break

                # the best step is selected
                best_move = min(
                    tabu_structure, key=lambda k: tabu_structure[k]["objective_value"]
                )
                move_obj = tabu_structure[best_move]["objective_value"]
                tabu_time = tabu_structure[best_move]["tabu_time"]

                # move is allowed
                if tabu_time < iteration:
                    current_solution = self.swap_move(current_solution, best_move)
                    current_objvalue = move_obj
                    saved_solutions[tuple(current_solution)] = current_objvalue

                    # if we found the best objective value so far we reset the over all iteration
                    if move_obj < best_objvalue:
                        best_solution = current_solution
                        best_objvalue = current_objvalue
                        stop_iter = 0
                    else:
                        stop_iter += 1

                    if current_solution[best_move[0]] > min_cars * 1.2:
                        # if we reach a saturation point of the "best" vehicle, tabu the move for longer
                        tabu_structure[best_move]["tabu_time"] = iteration + 20
                    else:
                        # the move gets added to the tabu list be banning the move for n steps
                        tabu_structure[best_move]["tabu_time"] = iteration + tenure
                    if allow_remove is False:
                        tabu_structure[
                            (best_move[0], 1 if best_move[-1] == -1 else -1)
                        ]["tabu_time"] = (iteration + tenure)
                    iteration += 1
                    break

                # the move is only allowed if the solution beats the current best solution
                else:
                    if move_obj < best_objvalue:
                        current_solution = self.swap_move(current_solution, best_move)
                        current_objvalue = move_obj
                        best_solution = current_solution
                        best_objvalue = current_objvalue
                        saved_solutions[tuple(best_solution)] = best_objvalue
                        stop_iter = 0
                        iteration += 1
                        break
                    else:
                        tabu_structure[best_move]["objective_value"] = math.inf
                        continue

        # return only the solutions that satisfies the minimum number of cars
        saved_solutions = {
            key: value
            for key, value in saved_solutions.items()
            if sum(list(key)[: self.car_index + 1]) >= min_cars
        }
        return saved_solutions

    def search(self):
        """
        Method for controlling the tabu search, which is called 4 times by default.
        It's done in order to "diversify" the search, to have both solutions present that removes vehicles, and
        solutions present that adds vehicles. After running the tabu searches, we iterate over the solutions sorted
        on the best objective values. Then real simulation happens on the whole trip set, if the solution satisfies all
        criteria; minimum cars, expense goal, co2e goal and 0 unallocated trips, the solution is stored. If it doesn't,
        the solution is stored as a fallback solution, in order to provide results in the case that no solution satis-
        fies all criteria.
        To improve efficiency, the tests are stopped after hitting 5 qualified solutions. In addition, it's recorded
        for each solution how many of each vehicle type is used and if the combination satisfied the capacity need.

        Returns
        -------
        list, of the top 5 solutions based on the objective value.

        """
        self.solutions = []
        for k, min_cars in enumerate(
            range(self.minimum_cars - 1, self.breakpoint_el_found + 1)
        ):
            sorted_solutions = sorted(
                self.tabu_search(min_cars, add_tenure=k).items(),
                key=operator.itemgetter(1),
            )
            self.solutions.append(list(set([a[0][:-1] for a in sorted_solutions])))

    def iterate_solutions(self):
        len_solutions = len([a for b in self.solutions for a in b])
        self.fallback_solutions = []  # for saving solutions that exceed the goals
        vehicle_assumption = (
            []
        )  # for saving vehicle type count for skipping previous failed type combinations
        vehicle_approved = (
            []
        )  # for allowing the solution to run if the type combination previously succeeded
        self.fallback_undriven = []  # for saving solutions that have undriven
        self.qualified = []  # the solutions that was successful
        qualification_validation = []
        typtrans = {"fossilbil": 0, "elbil": 1, "elcykel": 2, "cykel": 3}

        for i, solution in enumerate(self.roundrobin(*self.solutions)):
            if any([a > self.minimum_cars * 1.1 for a in solution[self.car_index :]]):
                yield i, len_solutions
                continue

            #  create vehicle type representation to check if solution should be skipped
            type_count = [0, 0, 0, 0]
            for k, count in enumerate(solution):
                typ = self.vehicle2type[self.id2vehicle[k]]
                type_count[typtrans[typ]] += count

            #  stop the search if we found 5 solutions that satisfies the criteria
            if len(self.qualified) == 5:
                break

            #  check if the vehicle type representation failed previously
            if (
                tuple(type_count) in vehicle_assumption
                and tuple(type_count) not in vehicle_approved
            ):
                yield i, len_solutions
                continue
            c_result = self.real_simulation(
                solution, False, intelligent=self.intelligent
            )
            if c_result[-1] > self.slack:
                self.fallback_undriven.append((solution, c_result))
                vehicle_assumption.append(tuple(type_count))
                yield i, len_solutions
                continue
            if c_result[0] > self.expense_goal or c_result[1] > self.co2e_goal:
                self.fallback_solutions.append((solution, c_result))
                yield i, len_solutions
                continue
            vehicle_approved.append(tuple(type_count))
            if solution not in qualification_validation:
                self.qualified.append((solution, c_result))
                qualification_validation.append(solution)
            yield i, len_solutions
        yield len_solutions, len_solutions

    def sort_solutions(self):
        fallback = False
        if len(self.qualified) == 0:
            fallback = True
            self.qualified = self.fallback_solutions
        if len(self.qualified) == 0:
            self.qualified = [a for a in self.fallback_undriven if a[-1][-1] < 5]
            if len(self.qualified) == 0:
                return []

        detailed_solutions = []
        for solution, c_result in self.qualified:
            c = {"omkostning": c_result[0], "co2e": c_result[1], "ukørte": c_result[-1]}

            fleet_counter = {}
            for vid, count in enumerate(solution):
                if count == 0:
                    continue
                vehicle = self.fleet_optimisation.proper[self.id2vehicle[vid]]["class"]
                class_name = " ".join([str(vehicle.make), str(vehicle.model)])
                omkostning_aar = str(vehicle.omkostning_aar)
                udledning = get_emission(vehicle)
                key = f"{class_name}_{udledning}_{omkostning_aar}".lower()
                if key not in fleet_counter:
                    fleet_counter[key] = {
                        "fleet_id": self.id2vehicle[vid],
                        "id": vid,
                        "class_name": class_name,
                        "omkostning_aar": omkostning_aar,
                        "stringified_emission": udledning,
                        "count": 0
                    }
                fleet_counter[key]["count"] += count

            c["flåde"] = list(fleet_counter.values())
            detailed_solutions.append(c)

        max_cost = max([a[0] for (_, a) in self.qualified])
        max_co2e = max([a[1] for (_, a) in self.qualified])
        obj = lambda cost, co2e, weight: cost + (co2e * weight)
        objectives_with_allocation = {
            k: obj(values[0] / max_cost, values[1] / max_co2e, self.weight)
            for k, (_, values) in enumerate(self.qualified)
        }
        if fallback:
            order = np.argsort([a["omkostning"] for a in detailed_solutions])
        else:
            order = [
                a[0]
                for a in sorted(
                    objectives_with_allocation.items(), key=operator.itemgetter(1)
                )
            ]
        report = []
        for k in order[:5]:
            report.append(detailed_solutions[k])

        return report

    @staticmethod
    def roundrobin(*iterables):
        num_active = len(iterables)
        nexts = cycle(iter(it).__next__ for it in iterables)
        while num_active:
            try:
                for next in nexts:
                    yield next()
            except StopIteration:
                # Remove the iterator we just exhausted from the cycle.
                num_active -= 1
                nexts = cycle(islice(nexts, num_active))
