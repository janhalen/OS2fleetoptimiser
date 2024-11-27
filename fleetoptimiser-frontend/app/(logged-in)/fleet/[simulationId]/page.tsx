'use client';

import useGetFleetSimulation from '@/components/hooks/useGetFleetSimulation';
import useGetVehiclesByLocation from '@/components/hooks/useGetVehiclesByLocation';
import {
    addExtraVehicles,
    setCars,
    setEndDate,
    setIntelligentAllocation,
    setLimitKm,
    setLocationId,
    setLocationIds,
    setAllSettings,
    setSimulationVehicles,
    setStartDate,
    fetchSimulationSettings,
} from '@/components/redux/SimulationSlice';
import { useAppDispatch } from '@/components/redux/hooks';
import dayjs from 'dayjs';
import { useEffect, useState } from 'react';
import FleetSimulation from '../FleetSimulation';
import { Button, Skeleton } from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import FleetResultSkeleton from '../FleetResultsSkeleton';
import useGetVehicles from '@/components/hooks/useGetVehicles';
import Typography from '@mui/material/Typography';

export default function Page({ params }: { params: { simulationId: string } }) {
    const [pageLoading, setPageLoading] = useState<boolean>(true);
    const simulation = useGetFleetSimulation(params.simulationId);

    const vehiclesByLocation = useGetVehiclesByLocation({
        startPeriod: dayjs(simulation.data?.result.simulation_options.start_date),
        endPeriod: dayjs(simulation.data?.result.simulation_options.end_date),
        enabled: !!simulation.data,
        selector: (data) => {
            if (simulation.data!.result.simulation_options.location_ids) {
                return data.locations.filter((loc) => simulation.data!.result.simulation_options.location_ids!.includes(loc.id)).flatMap((loc) => loc);
            } else {
                const loc = data.locations.find((loc) => loc.id === simulation.data?.result.simulation_options.location_id);
                return loc ? [loc] : undefined;
            }
        },
    });

    const allVehicles = useGetVehicles();

    const dispatch = useAppDispatch();

    useEffect(() => {
        if (simulation.data && vehiclesByLocation.data && allVehicles.data) {
            const simulationOptions = simulation.data.result.simulation_options;
            const selectedVehicles = vehiclesByLocation.data
                .map((locationVehicles) => locationVehicles.vehicles.filter((vehicle) => simulationOptions.current_vehicles.includes(vehicle.id)))
                .flatMap((vehicle) => vehicle);

            dispatch(fetchSimulationSettings());
            dispatch(setAllSettings(simulationOptions.settings));
            dispatch(setStartDate(simulationOptions.start_date));
            dispatch(setEndDate(simulationOptions.end_date));
            dispatch(setLocationId(simulationOptions.location_id));
            dispatch(setLocationIds(simulationOptions.location_ids ?? []));
            dispatch(setIntelligentAllocation(simulationOptions.intelligent_allocation));
            dispatch(setLimitKm(simulationOptions.limit_km));
            dispatch(setCars(selectedVehicles));
            dispatch(setSimulationVehicles(simulationOptions.simulation_vehicles));
            const extraVehicles = simulationOptions.simulation_vehicles.filter((vehicleId) => !selectedVehicles.find((vehicle) => vehicle.id === vehicleId.id));
            dispatch(addExtraVehicles(allVehicles.data.vehicles.filter((vehicle) => extraVehicles.find((extra) => extra.id === vehicle.id))));
            setPageLoading(false);
        }
    }, [simulation, vehiclesByLocation, allVehicles]);

    return (
        <>
            {pageLoading && (
                <div className="lg:flex lg:justify-between">
                    <div className="mx-2 mb-4 w-1/3 lg:flex-shrink-0 lg:w-[500px]">
                        <Typography variant="h4" className="mb-2">
                            Simuleringsindstillinger
                        </Typography>
                        <Skeleton className="h-8 mb-2 drop-shadow-md" variant="rectangular"></Skeleton>
                        <Skeleton className="h-96 mb-2 drop-shadow-md" variant="rectangular"></Skeleton>
                    </div>
                    <div className="flex-1 mx-2">
                        <div className="mb-2">
                            <Typography variant="h4" className="mb-2">
                                Overblik over simuleringsresultater
                            </Typography>
                            <Button disabled startIcon={<DownloadIcon />} variant="contained">
                                Download resultater
                            </Button>
                        </div>
                        <FleetResultSkeleton></FleetResultSkeleton>
                    </div>
                </div>
            )}
            {!pageLoading && <FleetSimulation initialHistoryId={params.simulationId}></FleetSimulation>}
        </>
    );
}
