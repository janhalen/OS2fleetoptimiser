import { drivingBook } from '@/components/hooks/useSimulateFleet';
import ToolTip from '@/components/ToolTip';
import TripByVehicleType from './TripByVehicleType';

const TripDistribution = ({ drivingBook }: { drivingBook: drivingBook[] }) => {
    const getTripsByType = (data: drivingBook[], dataType: 'simulation' | 'current') => {
        let max = data.reduce((max, trip) => (trip.distance > max ? trip.distance : max), 0);
        let entries = Array.from(Array(Math.round(max) + 1).keys()).map((n) => ({
            km: n,
            Cykel: 0,
            'El-cykel': 0,
            'El-bil': 0,
            'Fossil-bil': 0,
            'Ikke tildelt': 0,
        }));
        data.forEach((trip) => {
            const km = Math.round(trip.distance);
            const type = dataType === 'simulation' ? trip.simulation_type : trip.current_type;
            switch (type) {
                case 1: {
                    entries[km].Cykel++;
                    break;
                }
                case 2: {
                    entries[km]['El-cykel']++;
                    break;
                }
                case 3: {
                    entries[km]['El-bil']++;
                    break;
                }
                case 4: {
                    entries[km]['Fossil-bil']++;
                    break;
                }
                default: {
                    entries[km]['Ikke tildelt']++;
                    break;
                }
            }
        });

        return entries;
    };

    return (
        <>
            <div className="my-12 ml-1 mr-4 p-12 custom-nav bg-white">
                <h3 className="mt-4 ml-4">
                    Turfordeling for nuværende flåde{' '}
                    <ToolTip>
                        Fordelingen af ture på køretøjstype for den nuværende pulje (faktiske kørsel) i datoperioden. Det vises hvor mange ture i forskellige
                        længder, der er kørt af hhv. cykler, elcykler, elbiler og fossilbiler. Kør musen over for en bar for at se det specifikke antal.
                    </ToolTip>
                </h3>
                <div className="h-96">
                    <TripByVehicleType data={getTripsByType(drivingBook, 'current')} />
                </div>
            </div>
            <div className="my-12 ml-1 mr-4 p-12 custom-nav bg-white">
                <h3 className="mt-4 ml-4">
                    Turfordeling for simuleret flåde
                    <ToolTip>
                        Fordelingen af ture på køretøjstype for den simulerede pulje i datoperioden. Det vises hvor mange ture i forskellige længder, der er
                        kørt af hhv. cykler, elcykler, elbiler og fossilbiler. Kør musen over for en bar for at se det specifikke antal.
                    </ToolTip>
                </h3>
                <div className="h-96">
                    <TripByVehicleType data={getTripsByType(drivingBook, 'simulation')} />
                </div>
            </div>
        </>
    );
};

export default TripDistribution;
