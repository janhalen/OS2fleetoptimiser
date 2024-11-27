'use client';

import ToolTip from '@/components/ToolTip';
import Tooltip from '@mui/material/Tooltip';
import { Inter } from 'next/font/google';
import OptimisationSettings from './optimisationSettings';
import ComparisonFleet from './ComparisonFleet';
import { useAppSelector } from '@/components/redux/hooks';
import dayjs from 'dayjs';
import TestVehicleModal from './TestVehiclesModal';
import { Alert, Button, ButtonGroup, Divider, FormControlLabel, Switch } from '@mui/material';
import ResultTable from './ResultTable';
import LoadingOverlay from '../../../components/LoadingOverlay';
import LocationSettings from '../fleet/ShiftSettings';
import { useDispatch } from 'react-redux';
import GoalResultSkeletons from './GoalResultsSkeleton';
import SearchAbortedMessage from './SearchAborted';
import NoTripsError from '../fleet/NoTripsError';
import { compareShifts } from '../fleet/FleetSimulation';
import BikeSettingsModal from '../fleet/BikeSettings';
import SimulationSettingsModal from '../fleet/SimulationSettings';
import useSimulateGoal from '@/components/hooks/useSimulateGoal';
import GoalSimulationResultStats from './GoalSimulationResultStats';
import GoalSimulationYearlyGraphs from './GoalSimulationYearlyGraphs';
import { setIntelligentAllocation, setLimitKm } from '@/components/redux/SimulationSlice';
import SimulationFleet from './SimulationFleet';
import Typography from '@mui/material/Typography';
import NoCarsSelectedMessage from "@/app/(logged-in)/goal/NoCarsSelected";
import TipsAutomatic from "@/app/(logged-in)/goal/TipsBetterSolutionsModal";

type props = {
    goalSimulationId?: string;
};

export default function GoalSimulation({ goalSimulationId }: props) {
    const simulation = useSimulateGoal(goalSimulationId);

    const isSimulating = (status: string | undefined) => {
        switch (status) {
            case 'PENDING':
            case 'STARTED':
            case 'PROGRESS':
                return true;
            default:
                return false;
        }
    };

    const dispatch = useDispatch();
    let locshifts = useAppSelector((state) =>
        state.simulation.settings.shift_settings.filter((shiftLocation) => state.simulation.location_ids?.includes(shiftLocation.location_id))
    );
    return (
        <>
            {simulation.query.data && isSimulating(simulation.query.data?.status) && simulation.running && (
                <LoadingOverlay
                    status={simulation.query.data.status}
                    progress={simulation.query.data.progress.progress * 100}
                    setCancel={simulation.stopSimulation}
                    pendingText={simulation.query.data.progress.task_message}
                />
            )}
            <div className="lg:flex lg:justify-between">
                <div className="mx-2 mb-4 lg:flex-1 lg:min-w-[500px]">
                    <Typography variant="h3" className="mb-4">
                        Optimeringsindstillinger
                    </Typography>
                    <div className="p-2 mb-2 cartable">
                        <p>
                            Valgt simuleringsperiode: {useAppSelector((state) => dayjs(state.simulation.start_date).format('DD-MM-YYYY'))} til{' '}
                            {useAppSelector((state) => dayjs(state.simulation.end_date)).format('DD-MM-YYYY')}{' '}
                        </p>
                    </div>
                    <div className="bg-white drop-shadow-md p-4 mb-2 custom-nav">
                        <OptimisationSettings />
                        <Divider className="my-6" />
                        <div className="w-full">
                            <div className="">
                                <div className="max-h-24 p-4">
                                    <div className="w-full max-w-128 flex items-center">
                                        <div className="w-3/4">
                                            <span className="font-bold">Optimal tildeling</span><br></br>
                                            <span className="font-medium text-explanation">Aktiver optimal tildeling af køretøjer til rundture for bedre udnyttelse i af din flåde. </span>
                                        </div>
                                        <div className="flex justify-end ml-4">
                                            <Tooltip
                                                title="Anvend intelligent alloakering. Vær opmærksom på, at denne type simulering tager væsentlig længere tid. Intelligent allokering bygger på en algoritme der er optimeret til at håndtere 'enkelt-dags-ture', så hvis denne lokation har lange kørsler anbefales denne funktionalitet ikke. "
                                                placement="top"
                                                arrow
                                            >
                                                <FormControlLabel
                                                    control={
                                                        <Switch
                                                            disabled={useAppSelector((state) => state.simulation.limit_km) ? true : false}
                                                            onChange={(e) => dispatch(setIntelligentAllocation(e.target.checked))}
                                                            checked={useAppSelector((state) => state.simulation.intelligent_allocation)}
                                                        />
                                                    }
                                                    label=""
                                                />
                                            </Tooltip>
                                        </div>
                                    </div>

                                </div>
                                <div className="max-h-24 p-4">
                                    <div className="max-w-128 flex items-center">
                                        <div className="w-3/4">
                                            <span className="font-bold">Begræns km/år</span><br></br>
                                            <span className="font-medium text-explanation">Aktiver begrænsning af km for at overholde tilladte km-antal på leasingkontrakten.</span>
                                        </div>
                                        <div className="flex justify-end ml-4">
                                            <Tooltip
                                                title="Vil du anvende begrænsning af kilometer på dine køretøjer ift. antallet af kilometer på leasingaftalen, skal du benytte denne funktionalitet. Kan ikke benyttes sammen med intelligent allokering."
                                                placement="top"
                                                arrow
                                            >
                                                <FormControlLabel
                                                    control={
                                                        <Switch
                                                            disabled={useAppSelector((state) => state.simulation.intelligent_allocation) ? true : false}
                                                            onChange={(e) => dispatch(setLimitKm(e.target.checked))}
                                                            checked={useAppSelector((state) => state.simulation.limit_km)}
                                                        />
                                                    }
                                                    label=""
                                                />
                                            </Tooltip>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div className="flex my-4 p-2">
                                <div className="flex flex-wrap gap-4">
                                    <LocationSettings locationIds={useAppSelector((state) => state.simulation.location_ids)} />
                                    <SimulationSettingsModal />
                                    <BikeSettingsModal />
                                    <TestVehicleModal />
                                </div>
                            </div>
                        </div>
                        <Divider className="my-6"></Divider>
                        <div className="flex justify-center mb-4 max-w-128">
                            {!compareShifts(locshifts) && 'Vagter er ikke ens' && (
                                <Alert variant="filled" severity="error">
                                    Vagtlag på lokationerne er ikke ens. Opdater dem for at simulere.
                                </Alert>
                            )}
                            <Button className="w-64" disabled={!compareShifts(locshifts)} onClick={() => simulation.startSimulation()} variant="contained" color="success">
                                Optimér
                            </Button>
                        </div>
                    </div>
                    <Typography variant="h3" className="mt-8 mb-2">
                        Simuleringsflåde
                        <ToolTip>
                            Flåden som låses i simuleringen. Såfremt kørselsbehovet kan tilfredsstilles med færre køretøjer, vil den automatiske simulering fjerne
                            køretøjer fra puljen.
                        </ToolTip>
                    </Typography>
                    <div className="bg-white drop-shadow-md p-2 mb-2 overflow-y-scroll custom-nav cartable">
                         {/*todo potential bug for historic simulations, assert that antal i beholdning reflects actual count on the selected*/}
                        <SimulationFleet
                            vehicles={useAppSelector((state) => state.simulation.selectedVehicles)}
                            testVehicles={useAppSelector((state) => state.simulation.goalSimulationSettings.testVehiclesMeta)}
                        ></SimulationFleet>
                    </div>
                    <Typography variant="h3" className="mt-8 mb-2">
                        Sammenligningsflåde
                        <ToolTip>
                            Flåden som den automatiske simulering sammenligner med. Flåden er sammenstykket af de køretøjer der har været aktive i den valgte datoperiode.
                        </ToolTip>
                    </Typography>
                    <div className="bg-white drop-shadow-md p-2 overflow-y-scroll custom-nav cartable">
                        <ComparisonFleet vehicles={useAppSelector((state) => state.simulation.selectedVehicles)} />
                    </div>
                </div>
                <div className="flex-1 mx-2 ml-10">
                    <Typography variant="h3" className="mb-8">
                        Fremtidig flådesammensætning
                    </Typography>
                    {simulation.query.data && isSimulating(simulation.query.data?.status) && <GoalResultSkeletons />}
                    {simulation.query.data?.status === 'SUCCESS' &&
                        !simulation.query.data?.result.solutions &&
                        simulation.query.data?.result.message === 'Search aborted.' && <SearchAbortedMessage />}
                    {simulation.query.data?.status === 'SUCCESS' &&
                        !simulation.query.data?.result.solutions &&
                        simulation.query.data?.result.message === 'No cars selected.' && <NoCarsSelectedMessage />}
                    {simulation.query.data?.status === 'SUCCESS' &&
                        !simulation.query.data?.result.solutions &&
                        simulation.query.data?.result.message !== 'Search aborted.' &&
                        simulation.query.data?.result.message !== 'No cars selected.' && <NoTripsError />}
                    {simulation.query.data?.result?.solutions && (
                        <>
                            <GoalSimulationResultStats solution={simulation.query.data.result.solutions[0]} />
                            <GoalSimulationYearlyGraphs solutions={simulation.query.data.result.solutions} />
                            {
                                simulation.query.data.result && (
                                    simulation.query.data.result.solutions.length < 5 ||
                                    simulation.query.data.result.solutions[0].simulation_expense > simulation.query.data.result.solutions[0].current_expense ||
                                    simulation.query.data.result.solutions[0].simulation_co2e > simulation.query.data.result.solutions[0].current_co2e
                                ) &&
                                <TipsAutomatic/>
                            }
                            <ResultTable
                                solutions={simulation.query.data.result.solutions}
                                settings={simulation.query.data.result.simulation_options.settings}
                                goalSimulationId={goalSimulationId ?? simulation.query.data.id}
                            ></ResultTable>
                        </>
                    )}
                </div>
            </div>
        </>
    );
}
