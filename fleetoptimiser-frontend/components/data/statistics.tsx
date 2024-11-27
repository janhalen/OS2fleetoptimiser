import { Dayjs } from 'dayjs';
import { shift } from '../hooks/useGetSettings';
import { drivingDataResult } from '../hooks/useGetDrivingData';
import AxiosBase from '../AxiosBase';

type DrivingDataFilters = {
    startPeriod: Dayjs | null;
    endPeriod: Dayjs | null;
    locationIds?: number[];
    vehicleIds?: number[];
    departments?: string[];
    forvaltninger?: string[];
    shiftsAggregate?: shift[];
    includeTripSegments?: boolean;
    shiftFilter?: number[];
    asTripSegments?: boolean;
    enabled?: boolean;
    applyShiftFilter?: boolean;
    timeDelta?: boolean;
};

export async function getDrivingData({
    endPeriod,
    startPeriod,
    asTripSegments,
    departments,
    forvaltninger,
    includeTripSegments,
    locationIds,
    shiftFilter,
    shiftsAggregate: shifts,
    timeDelta,
    vehicleIds,
}: DrivingDataFilters): Promise<drivingDataResult> {
    const searchParams = new URLSearchParams();
    if (startPeriod) searchParams.append('start_date', startPeriod?.format('YYYY-MM-DD'));
    if (endPeriod) searchParams.append('end_date', endPeriod?.add(1, 'day').format('YYYY-MM-DD'));
    if (includeTripSegments) searchParams.append('includeTripSegments', includeTripSegments + '');
    if (asTripSegments) searchParams.append('as_segments', asTripSegments + '');
    if (timeDelta) searchParams.append('with_timedelta', timeDelta + '');

    if (forvaltninger) {
        for (const forvaltning of forvaltninger) {
            searchParams.append('forvaltninger', forvaltning);
        }
    }

    if (locationIds) {
        for (const locationId of locationIds) {
            searchParams.append('locations', locationId.toString());
        }
    }

    if (vehicleIds) {
        for (const vehicleId of vehicleIds) {
            searchParams.append('vehicles', vehicleId.toString());
        }
    }

    if (departments) {
        for (const department of departments) {
            searchParams.append('departments', department);
        }
    }

    if (shifts) {
        for (const shift of shifts) {
            searchParams.append('shifts', JSON.stringify(shift));
        }
    }

    if (forvaltninger) {
        for (const forvaltning of forvaltninger) {
            searchParams.append('forvaltninger', forvaltning);
        }
    }

    if (shiftFilter) {
        for (const id of shiftFilter) {
            searchParams.append('shift_filter', id.toString());
        }
    }

    const response = await AxiosBase.get<drivingDataResult>('/statistics/driving-data?' + searchParams.toString());
    return response.data;
}
