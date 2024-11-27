from typing import Literal

from celery.states import ALL_STATES
from pydantic import BaseModel, Field, validator

from ..configuration.schemas import SimulationConfiguration
from ..simulation_setup.schemas import LocationVehiclesIn


class GoalSimulationOptions(LocationVehiclesIn):
    location_id: int | None = Field(
        description="Location id of the location that should be simulated"
    )
    location_ids: list[int] | None = Field(
        description="Location ids of multiple selected simulation locations"
    )
    intelligent_allocation: bool | None = Field(
        False,
        description="Should intelligent allocation be used. Optimal "
        "allocation of trips weighed between cost pr km and "
        "emission.",
    )
    limit_km: bool | None = Field(
        False,
        description="Should the simulation stop utilising vehicles when they reach "
        "their allowed km/year according to the lease contract.",
    )
    current_vehicles: list[int] = Field(
        description="Ids of the cars that are selected in the current fleet"
    )
    fixed_vehicles: list[int] = Field(
        [],
        description="Ids of the cars that can only be removed in a solution if "
        "there's an excess capacity in fleet.",
    )
    extra_expense: int | None = Field(
        0,
        description="The extra expense, if any, available in the fleet. "
        "This amount will be added to the expense of the current fleet.",
    )
    co2e_saving: int | None = Field(
        0, description="The percentage save of the current co2e emission"
    )
    prioritisation: int | None = Field(
        5,
        description="The prioritisation between expense - and emission savings. 0-10.",
    )
    test_vehicles: list[int] | None = Field(
        description="Ids of cars that should be tested against. If ids are present"
        ", only these will be available to the search. If no ids, all "
        "vehicles will be present"
    )
    settings: SimulationConfiguration | None

    @validator("co2e_saving")
    def co2e_saving_percentage(cls, v):
        if v is None:
            return 0
        if 0 > v or v > 100:
            raise ValueError("percentage_of_trips should be between 0 and 100")
        return v

    @validator("prioritisation")
    def prioritisation_limit(cls, v):
        if v is None:
            return 5
        if 0 > v or v > 10:
            raise ValueError("percentage_of_trips should be between 0 and 100")
        return v

    @validator("extra_expense")
    def expense_not_null(cls, v):
        if v is None:
            return 0
        return v


class SolutionVehicle(BaseModel):
    id: int = Field(example=1, description="ID of the selected vehicle")
    count: int = Field(
        example=4, description="Count of the vehicle that is in the solution"
    )
    count_difference: int | None = Field(
        example=-2, description="Difference from original count"
    )
    name: str | None
    omkostning_aar: float | None
    emission: str | None


class Solution(BaseModel):
    current_expense: int = Field(
        example=274886,
        description="The total expense of the current fleet with the selected "
        "vehicles and trips",
    )
    simulation_expense: int = Field(
        example=234527, description="The total expense of the solution fleet"
    )
    current_co2e: float = Field(
        example=2.03, description="The emission of the current/actual fleet"
    )
    simulation_co2e: float = Field(
        example=1.684, description="The emission of the solution fleet"
    )
    unallocated: int = Field(description="Number of unallocated trips in the solution")
    vehicles: list[SolutionVehicle] = Field(
        description="The list of vehicles in the solution"
    )
    results: dict | None = Field(description="detailed results of the simulation")


class GoalSimulationResult(BaseModel):
    number_of_trips: int = Field(
        example=54, description="The number of trips in the date range"
    )
    solutions: list[Solution] | None = Field(
        description="The list of solutions found in the search"
    )
    simulation_options: GoalSimulationOptions | None = Field(
        description="The options/settings used in the simulation"
    )
    message: str | None


class GoalSimulationOut(BaseModel):
    id: str
    status: Literal[tuple(ALL_STATES) + ("PROGRESS",)]
    progress: dict | None
    result: GoalSimulationResult | None


class GoalSimulationHistory(BaseModel):
    id: str
    start_date: str
    end_date: str
    location: str
    locations: str | None
    simulation_date: str