from datetime import datetime, timedelta

import pandas as pd

car = {"id": 237, "location": 3}


car_trips = pd.DataFrame(
    [
        {
            "id": 333,
            "start_time": "2022-04-01 00:00:00",
            "end_time": "2022-04-01 01:00:00",
            "start_latitude": 55.66235882000046,
            "start_longitude": 12.587402804812708,
            "end_latitude": 55.67613656023434,
            "end_longitude": 12.568678025715922,
            "car_id": 237,
            "distance": 20,
        },
        {
            "id": 3331,
            "start_time": "2022-04-01 01:30:00",
            "end_time": "2022-04-01 02:00:00",
            "start_latitude": 55.67613656023434,
            "start_longitude": 12.568678025715922,
            "end_latitude": 55.67613656023434,
            "end_longitude": 12.568678025715922,
            "car_id": 237,
            "distance": 20,
        },
        {
            "id": 3332,
            "start_time": "2022-04-01 02:30:00",
            "end_time": "2022-04-01 03:00:00",
            "start_latitude": 55.67613656023434,
            "start_longitude": 12.568678025715922,
            "end_latitude": 55.66235882000046,
            "end_longitude": 12.587402804812708,
            "car_id": 237,
            "distance": 20,
        },
        {
            "id": 3333,
            "start_time": "2022-04-01 21:00:00",
            "end_time": "2022-04-01 22:00:00",
            "start_latitude": 55.67613656023434,
            "start_longitude": 12.568678025715922,
            "end_latitude": 55.66235882000046,
            "end_longitude": 12.587402804812708,
            "car_id": 237,
            "distance": 20,
        },
    ]
)


start_locations = [
    {
        "id": 3,
        "latitude": 55.66235882000046,
        "longitude": 12.587402804812708,
    }
]


frame_trips = pd.DataFrame(
        [
            {
                "id": 1,
                "car_id": 1,
                "start_time": datetime(2022, 4, 1, 0, 0, 0),
                "end_time": datetime(2022, 4, 1, 1, 0, 0),
                "distance": 1,
                "stop_duration": timedelta(minutes=10),
                "start_latitude": 55.66235882000046,
                "start_longitude": 12.587402804812708,
                "end_latitude": 55.66235882000046,
                "end_longitude": 12.587402804812708,
            },
            {
                "id": 2,
                "car_id": 1,
                "start_time": datetime(2022, 4, 1, 1, 10, 0),
                "end_time": datetime(2022, 4, 1, 2, 0, 0),
                "distance": 1,
                "stop_duration": timedelta(minutes=40),
                "start_latitude": 55.66235882000046,
                "start_longitude": 12.587402804812708,
                "end_latitude": 55.66235882000046,
                "end_longitude": 12.587402804812708,
            },
            {
                "id": 3,
                "car_id": 1,
                "start_time": datetime(2022, 4, 1, 2, 40, 0),
                "end_time": datetime(2022, 4, 1, 3, 0, 0),
                "distance": 1,
                "stop_duration": timedelta(minutes=20),
                "start_latitude": 55.66235882000046,
                "start_longitude": 12.587402804812708,
                "end_latitude": 55.66235882000046,
                "end_longitude": 12.587402804812708,
            },
            {
                "id": 4,
                "car_id": 1,
                "start_time": datetime(2022, 4, 1, 13, 40, 0),
                "end_time": datetime(2022, 4, 1, 13, 56, 0),
                "distance": 1,
                "stop_duration": timedelta(minutes=20),
                "start_latitude": 55.66235882000046,
                "start_longitude": 12.587402804812708,
                "end_latitude": 55.66235882000046,
                "end_longitude": 12.587402804812708,
            },
        ]
    )

roundtrip = [
    trip
    for trip in frame_trips.itertuples()
]
