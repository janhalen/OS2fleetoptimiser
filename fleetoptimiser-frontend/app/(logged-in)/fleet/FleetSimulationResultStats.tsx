import ToolTip from '@/components/ToolTip';
import Typography from '@mui/material/Typography';

type SimulationResultStats = {
    unallocatedTrips: number;
    financialSavings: number;
    co2eSavings: number;
};

const FleetSimulationResultStats = ({ co2eSavings, financialSavings, unallocatedTrips }: SimulationResultStats) => {
    return (
        <div className="flex justify-between mb-2">
            <div className="text-center flex-1 bg-white drop-shadow-md p-2 custom-nav">
                <Typography variant="h5">
                    Rundture uden køretøj
                    <ToolTip>
                        Antallet af ture, der ikke blev allokeret et køretøj i simuleringen. Det betyder, at der ikke var køretøjer ledige, der kunne acceptere
                        turen ud fra tidspunkt og distance.
                    </ToolTip>
                    <p className={'text-3xl font-bold ' + (unallocatedTrips > 0 ? 'text-red-500' : 'text-green-500')}>{unallocatedTrips.toLocaleString()}</p>
                </Typography>
            </div>
            <div className="text-center flex-1 bg-white drop-shadow-md mx-12 p-2 custom-nav">
                <Typography variant="h5">
                    Besparelse (DKK/år)
                    <ToolTip>
                        Kroner besparelse/forøgelse af den samlede årlige omkostning for puljen. Dette er de indtastede årlige omkostninger for køretøjerne
                        inkl. drivmiddelforbrug - beregnet ud fra de kørete kilometer i simuleringen.
                    </ToolTip>
                    <p className={'text-3xl font-bold ' + (financialSavings >= 0 ? 'text-green-500' : 'text-red-500')}>{financialSavings.toLocaleString()}</p>
                </Typography>
            </div>
            <div className="text-center flex-1 bg-white drop-shadow-md p-2 custom-nav">
                <Typography variant="h5">
                    Reduktion udledning (Ton CO2e/år)
                    <ToolTip>
                        Den simulerede årlige reduktion/forøgelse i CO2e-udledning. Den faktiske udledning mod den simulerede udledning. Der bruges CO2e for at
                        kunne sammenligne fossil- og elbiler. Beregningsmetoden baserer sig på POGI&apos;s miljøværktøj.
                    </ToolTip>
                </Typography>
                <p className={'text-3xl font-bold ' + (co2eSavings >= 0 ? 'text-green-500' : 'text-red-500')}>{(co2eSavings * -1).toLocaleString()}</p>
            </div>
        </div>
    );
};

export default FleetSimulationResultStats;
