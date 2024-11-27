import useSimulateFleet from '@/components/hooks/useSimulateFleet';
import { useAppDispatch, useAppSelector } from '@/components/redux/hooks';
import CarsTable, { CarCumulative } from './CarsTable';
import { reduceDuplicateVehicles } from '@/components/DuplicateReducer';
import Tooltip from '@mui/material/Tooltip';
import dayjs from 'dayjs';
import { Alert, Button, ButtonGroup, Divider, FormControlLabel, Switch } from '@mui/material';
import { setIntelligentAllocation, setLimitKm } from '@/components/redux/SimulationSlice';
import ShiftModal from './ShiftSettings';
import SimulationSettingsModal from './SimulationSettings';
import BikeSettingsModal from './BikeSettings';
import ExtraVehicleModal from './ExtraVehiclesModal';
import FleetSimulationResults from './FleetSimulationResults';
import Typography from '@mui/material/Typography';
import ToolTip from "@/components/ToolTip";

type props = {
    initialHistoryId?: string;
};

const areShiftsEqual = ({ shifts1, shifts2 }: { shifts1: any; shifts2: any }): boolean => {
    if (shifts1.length !== shifts2.length) {
        return false;
    }

    for (let i = 0; i < shifts1.length; i++) {
        if (shifts1[i].shift_start !== shifts2[i].shift_start || shifts1[i].shift_end !== shifts2[i].shift_end) {
            return false;
        }
    }

    return true;
};

export const compareShifts = (objects: any) => {
    if (objects === undefined || objects.length === 0) {
        return true;
    }
    const referenceShifts = objects[0].shifts;
    for (const object of objects) {
        if (!areShiftsEqual({ shifts1: object.shifts, shifts2: referenceShifts })) {
            return false;
        }
    }

    return true;
};

export default function FleetSimulation({ initialHistoryId }: props) {
    const dispatch = useAppDispatch();
    const simulation = useSimulateFleet(initialHistoryId);

    const fleet = useAppSelector((state) => {
        const current: CarCumulative[] = reduceDuplicateVehicles(state.simulation.selectedVehicles).map((vehicle) => ({
            vehicle: vehicle.vehicle,
            extra: false,
            count: vehicle.count,
        }));
        const extra: CarCumulative[] = reduceDuplicateVehicles(state.simulation.fleetSimulationSettings.extraVehicles).map((vehicle) => ({
            vehicle: vehicle.vehicle,
            extra: true,
            count: 0,
        }));
        return current.concat(extra);
    });
    let locshifts = useAppSelector((state) =>
        state.simulation.settings.shift_settings.filter((shiftLocation) => state.simulation.location_ids?.includes(shiftLocation.location_id))
    );

    return (
        <>
            <div className="lg:flex lg:justify-between">
                <div className="mx-2 mb-4 w-1/3 lg:flex-shrink-0 lg">
                    <Typography variant="h3" className="mb-8">
                        Simuleringsopsætning
                    </Typography>
                    <div className="p-2 bg-white drop-shadow-md mb-2 custom-nav cartable">
                        <p>
                            Valgt simuleringsperiode: {useAppSelector((state) => dayjs(state.simulation.start_date).format('DD-MM-YYYY'))} til{' '}
                            {useAppSelector((state) => dayjs(state.simulation.end_date)).format('DD-MM-YYYY')}{' '}
                        </p>
                    </div>

                    <div className="bg-white drop-shadow-md p-2">
                        <div className="">
                            <div className="w-full">
                                <div className="max-h-24 p-4">
                                    <div className="w-full max-w-128 flex items-center">
                                        <div className="max-w-96">
                                            <span className="font-bold">Optimal tildeling</span><br></br>
                                            <span className="font-medium text-explanation">Aktiver optimal tildeling af køretøjer til rundture for bedre udnyttelse i af din flåde. </span>

                                        </div>
                                        <div className="flex justify-end ml-4">
                                            <Tooltip
                                                title="Anvend intelligent allokering. Vær opmærksom på, at denne type simulering tager væsentlig længere tid. Intelligent allokering bygger på en algoritme der er optimeret til at håndtere 'enkelt-dags-ture', så hvis denne lokation har lange kørsler anbefales denne funktionalitet ikke."
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
                                    <div className="w-full max-w-128 flex items-center">

                                        <div className="max-w-96">
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
                                    <ShiftModal locationIds={useAppSelector((state) => state.simulation.location_ids)} />
                                    <SimulationSettingsModal />
                                    <BikeSettingsModal />
                                    <ExtraVehicleModal />
                                </div>
                            </div>
                        </div>
                        <Divider className="my-2" />
                        <div className="flex justify-center my-6">
                            <Button className="w-64" disabled={!compareShifts(locshifts)} color="success" variant="contained" onClick={() => simulation.startSimulation()}>
                                Simulér
                            </Button>
                            {!compareShifts(locshifts) && 'Vagter er ikke ens' && (
                                <Alert variant="filled" severity="error">
                                    Vagtlag på lokationerne er ikke ens. Opdater dem for at simulere.
                                </Alert>
                            )}
                        </div>
                    </div>

                    <div style={{ paddingTop: '0px', marginTop: '20px', height: '60.9vh', overflow: 'auto' }} className="bg-white drop-shadow-md p-2">
                        <CarsTable cars={fleet}></CarsTable>
                    </div>
                </div>
                <FleetSimulationResults simulation={simulation.query.data}></FleetSimulationResults>
            </div>
        </>
    );
}
