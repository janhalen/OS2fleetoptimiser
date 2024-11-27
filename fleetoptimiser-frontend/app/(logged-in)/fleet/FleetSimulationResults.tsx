import {Button, CircularProgress} from '@mui/material';
import FleetSimulationResultStats from './FleetSimulationResultStats';
import UnallocatedTripsPane from './UnallocatedTripsPane';
import TripDistribution from './TripDistribution';
import NoTripsError from './NoTripsError';
import FleetResultSkeleton from './FleetResultsSkeleton';
import { simulation } from '@/components/hooks/useSimulateFleet';
import AxiosBase from '@/components/AxiosBase';
import DownloadIcon from '@mui/icons-material/Download';
import Typography from '@mui/material/Typography';

type props = {
    simulation?: simulation;
    queryStatus?: string;
};

export default function FleetSimulationResults({ simulation, queryStatus }: props) {
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

    return (
        <div className="flex-1 mx-2 ml-10">
            <div className="mb-4 flex">
                <div className="w-full items-start">
                    <Typography variant="h3">Overblik over simuleringsresultater</Typography>
                </div>
                <div className="w-full items-end">
                    <Button
                        className="float-right"
                        href={`${AxiosBase.getUri()}fleet-simulation/simulation/${simulation?.id}?download=true`}
                        disabled={!simulation}
                        startIcon={<DownloadIcon />}
                        variant="contained"
                        download
                    >
                        Download resultater
                    </Button>
                </div>
            </div>
            {simulation &&( isSimulating(queryStatus) || simulation.status !== "SUCCESS") &&
                <div className="p-10 flex justify-center">
                    <CircularProgress />
                </div>
            }
            {queryStatus === 'SUCCESS' && simulation?.result.driving_book && <NoTripsError />}
            {simulation?.result?.driving_book && (
                <>
                    <div className="mb-6">
                        <FleetSimulationResultStats
                            co2eSavings={simulation.result.co2e_savings}
                            financialSavings={simulation.result.financial_savings}
                            unallocatedTrips={simulation.result.unallocated}
                        />
                    </div>
                    <div style={{ overflow: 'auto', height: '71vh' }}>
                        <UnallocatedTripsPane drivingBook={simulation.result.driving_book} />
                        <TripDistribution drivingBook={simulation.result.driving_book} />
                    </div>
                </>
            )}
        </div>
    );
}
