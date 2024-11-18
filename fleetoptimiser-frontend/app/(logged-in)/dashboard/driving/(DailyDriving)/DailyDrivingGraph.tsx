'use client';

import { ResponsiveLine } from '@nivo/line';

type entry = {
    x: string;
    y: number;
};

type props = {
    color: string;
    data: {
        id: string;
        uniqueCars: number;
        data: entry[];
    }[];
    header: string;
};

const DayilyDrivingGraph = ({ color, data, header }: props) => {
    const getFormattedData = () => {
        const lines = [
            {
                id: header,
                data: data[0].data,
            },
        ];
        return lines;
    };

    const getAverage = () => {
        const line = data[0];
        return line.data.reduce((partialSum, a) => partialSum + a.y, 0) / line.data.length;
    };

    return (
        <div>
            <h3>{header}</h3>
            <p>Gennemsnitlig kørsel pr. dag: {Math.round(getAverage()).toLocaleString()} km.</p>
            <p>Antallet af biler der indgår i dataen: {data[0].uniqueCars}</p>
            <div className="h-96">
                <ResponsiveLine
                    margin={{ top: 20, right: 20, bottom: 60, left: 80 }}
                    animate={true}
                    data={getFormattedData()}
                    colors={[color]}
                    xScale={{
                        type: 'time',
                        format: '%Y-%m-%d',
                        useUTC: false,
                        precision: 'day',
                    }}
                    xFormat="time:%Y-%m-%d"
                    yScale={{
                        type: 'linear',
                        stacked: false,
                    }}
                    yFormat={(data) => {
                        const value = data as number;
                        return (+value.toFixed(3)).toLocaleString() + ' km';
                    }}
                    axisLeft={{
                        legend: 'Kilometer',
                        legendOffset: -60,
                        legendPosition: 'middle',
                    }}
                    axisBottom={{
                        format: '%b %d',
                        tickValues: 'every 2 days',
                        legend: 'Dato',
                        legendOffset: 40,
                        legendPosition: 'middle',
                    }}
                    enablePointLabel={false}
                    pointSize={16}
                    pointBorderWidth={1}
                    pointBorderColor={{
                        from: 'color',
                        modifiers: [['darker', 0.3]],
                    }}
                    useMesh={true}
                    enableSlices={false}
                />
            </div>
        </div>
    );
};

export default DayilyDrivingGraph;
