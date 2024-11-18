'use client';

import { useGetGoalSimulation } from '@/components/hooks/useGetGoalSimulation';
import useGetVehiclesByLocation from '@/components/hooks/useGetVehiclesByLocation';
import {
    addTestVehicles,
    setCars,
    setEndDate,
    setGoalSimulationVehicles,
    setIntelligentAllocation,
    setLimitKm,
    setLocationId,
    setLocationIds,
    setAllSettings,
    setStartDate,
    fetchSimulationSettings, addTestVehiclesMeta
} from '@/components/redux/SimulationSlice';
import { useAppDispatch } from '@/components/redux/hooks';
import dayjs from 'dayjs';
import { useEffect, useState } from 'react';
import GoalSimulation from '../GoalSimulation';
import ToolTip from '@/components/ToolTip';
import GoalResultSkeletons from '../GoalResultsSkeleton';
import { Skeleton } from '@mui/material';
import useGetVehicles from "@/components/hooks/useGetVehicles";

export default function Page({ params }: { params: { simulationId: string } }) {
    const [pageLoading, setPageLoading] = useState<boolean>(true);
    const simulation = useGetGoalSimulation(params.simulationId);
    const vehicles = useGetVehiclesByLocation({
        startPeriod: dayjs(simulation.data?.result.simulation_options.start_date),
        endPeriod: dayjs(simulation.data?.result.simulation_options.end_date),
        enabled: !!simulation.data,
        selector: (data) => {
            if (simulation.data?.result.simulation_options.location_ids) {
                return data.locations.filter((loc) => simulation.data?.result.simulation_options.location_ids?.includes(loc.id)).flatMap((loc) => loc);
            } else {
                const location = data.locations.find((loc) => loc.id === simulation.data?.result.simulation_options.location_id);
                return location ? [location] : undefined;
            }
        },
    });

    const dispatch = useAppDispatch();
    const allVehicles = useGetVehicles();
    useEffect(() => {
        if (simulation.data && vehicles.data) {
            const simulationOptions = simulation.data.result.simulation_options;

            const selectedVehicles = vehicles.data
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
            dispatch(setGoalSimulationVehicles(simulationOptions.fixed_vehicles));
            dispatch(addTestVehicles(simulationOptions.test_vehicles));
            dispatch(addTestVehiclesMeta(allVehicles.data?.vehicles.filter((vehicle) => simulationOptions.test_vehicles.includes(vehicle.id))));
            setPageLoading(false);
        }
    }, [simulation, vehicles, allVehicles]);

    return (
        <>
            {pageLoading && (
                <>
                    <div className="bg-white p-4 mx-2 mb-4 drop-shadow-md">
                        <h1 className="border-b mb-2 pb-2 font-semibold">Automatisk simulering</h1>
                        <p>På denne side kan man som bruger anmode AI modulet om at komme med forslag til nye flådesammensætninger</p>
                    </div>
                    <div className="lg:flex lg:justify-between">
                        <div className="mx-2 mb-4 lg:flex-1 lg:min-w-[500px]">
                            <h2 className="text-3xl mb-2">Optimeringsindstillinger</h2>
                            <Skeleton className="h-8 mb-2 drop-shadow-md" variant="rectangular"></Skeleton>
                            <Skeleton className="h-96 mb-2 drop-shadow-md" variant="rectangular"></Skeleton>
                            <h2 className="text-3xl mb-2">
                                Simuleringsflåde
                                <ToolTip>
                                    Flåden som låses i simuleringen. Såfremt kørselsbehovet kan tilfredsstilles med færre køretøjer, vil den automatiske simulering fjerne
                                    køretøjer fra puljen.
                                </ToolTip>
                            </h2>
                            <Skeleton className="h-96 mb-2 drop-shadow-md" variant="rectangular"></Skeleton>
                            <h2 className="text-3xl mb-2">
                                Sammenligningsflåde
                                <ToolTip>
                                    Flåden som den automatiske simulering sammenligner med. Flåden er sammenstykket af de køretøjer der har været aktive i den valgte
                                    datoperiode.
                                </ToolTip>
                            </h2>
                            <Skeleton className="h-96 mb-2 drop-shadow-md" variant="rectangular"></Skeleton>
                        </div>
                        <div className="flex-1 mx-2">
                            <h2 className="text-3xl mb-2">Fremtidig flådesammensætning</h2>
                            <GoalResultSkeletons></GoalResultSkeletons>
                        </div>
                    </div>
                </>
            )}
            {/*todo reflect the simulation configuration on the historic simulation*/}
            {!pageLoading && <GoalSimulation goalSimulationId={params.simulationId}></GoalSimulation>}
        </>
    );
}
