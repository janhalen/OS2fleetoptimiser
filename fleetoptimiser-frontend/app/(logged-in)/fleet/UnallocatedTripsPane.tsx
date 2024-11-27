import { drivingBook } from '@/components/hooks/useSimulateFleet';
import ToolTip from '@/components/ToolTip';
import { Button } from '@mui/material';
import dayjs from 'dayjs';
import { useState } from 'react';
import TripByDateGraph from './TripByDateGraph';
import TripsByDayGraph from './TripByDayGraph';

const UnallocatedTripsPane = ({ drivingBook }: { drivingBook: drivingBook[] }) => {
    const [showDays, setShowDays] = useState<boolean>(false);

    const getTripsByDate = (data: drivingBook[]) => {
        let tripsByDate = [
            { id: 'Simulation', data: [] as { x: string; y: number }[] },
            { id: 'Nuværende', data: [] as { x: string; y: number }[] },
        ];
        tripsByDate = data.reduce((acc, cur) => {
            const day = dayjs(cur.start_time).format('YYYY-MM-DD');
            let existingSim = acc[0].data.find((item) => item.x === day);
            let existingCur = acc[1].data.find((item) => item.x === day);
            if (!existingSim) {
                acc[0].data.push({
                    x: day,
                    y: 0,
                });
            }
            if (!existingCur) {
                acc[1].data.push({
                    x: day,
                    y: 0,
                });
            }
            if (cur.current_type === -1) {
                let existing = acc[1].data.find((item) => item.x === day);
                if (existing) existing.y++;
            }
            if (cur.simulation_type === -1) {
                let existing = acc[0].data.find((item) => item.x === day);
                if (existing) existing.y++;
            }
            return acc;
        }, tripsByDate);
        return tripsByDate;
    };

    const getTripsByDay = (data: drivingBook[]) => {
        let tripByDay = [
            {
                day: 'Søndag',
                simulation: 0,
                current: 0,
            },
            {
                day: 'Mandag',
                simulation: 0,
                current: 0,
            },
            {
                day: 'Tirsdag',
                simulation: 0,
                current: 0,
            },
            {
                day: 'Onsdag',
                simulation: 0,
                current: 0,
            },
            {
                day: 'Torsdag',
                simulation: 0,
                current: 0,
            },
            {
                day: 'Fredag',
                simulation: 0,
                current: 0,
            },
            {
                day: 'Lørdag',
                simulation: 0,
                current: 0,
            },
        ];

        tripByDay = data.reduce((acc, cur) => {
            const day = dayjs(cur.start_time).day();
            if (cur.simulation_type === -1) {
                acc[day].simulation++;
            }
            if (cur.current_type === -1) {
                acc[day].current++;
            }
            return acc;
        }, tripByDay);

        // Put sunday at the end for the graph
        const sunday = tripByDay.shift();
        if (sunday) tripByDay.push(sunday);

        return tripByDay;
    };

    return (
        <div className="my-12 ml-1 mr-4 p-12 custom-nav bg-white">
            <ToolTip>
                Overblik over fordelingen af ukørte ture over den valgte datoperiode. Såfremt der er ture, der ikke er blevet kørt vil det vise sig som et
                udsving i nedenstående trendlinje. Der vises en linje for både den nuværende- og den valgte simulerede pulje.
            </ToolTip>
            <Button variant="contained" color="secondary" onClick={(e) => setShowDays(!showDays)}>
                Skift graf
            </Button>
            <div className="h-96">
                {showDays ? <TripsByDayGraph data={getTripsByDay(drivingBook)} /> : <TripByDateGraph data={getTripsByDate(drivingBook)} />}
            </div>
        </div>
    );
};

export default UnallocatedTripsPane;
