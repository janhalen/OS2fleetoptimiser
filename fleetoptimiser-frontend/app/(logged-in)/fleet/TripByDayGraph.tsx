import { ResponsiveBar } from '@nivo/bar';
import { getYTicks } from "@/app/(logged-in)/fleet/TripByVehicleType";

type entry = {
    day: string;
    simulation: number;
    current: number;
};

type Colors = {
    [key: string]: string;
};

type props = {
    data: entry[];
};

const TripsByDayGraph = ({ data }: props) => {
    const colors: Colors = { simulation: '#109cf1', Nuværende: '#52575c' };

    const sumsY = data.map(dayInWeek => {
        return Math.max(...[dayInWeek.simulation, dayInWeek.current])
    })
    const yTicks = getYTicks(sumsY)

    return (
        <ResponsiveBar
            data={data}
            keys={['simulation', 'Nuværende']}
            indexBy="day"
            margin={{ top: 40, right: 40, bottom: 80, left: 60 }}
            padding={0.3}
            valueScale={{ type: 'linear', min: 0, max: Math.max(...yTicks) }}
            indexScale={{ type: 'band', round: true }}
            colors={(e) => colors[e.id]}
            borderColor={{
                from: 'color',
                modifiers: [['darker', 1.6]],
            }}
            axisTop={null}
            axisRight={null}
            axisBottom={{
                tickSize: 5,
                tickPadding: 5,
                tickRotation: 40,
                legend: 'Dag',
                legendPosition: 'middle',
                legendOffset: 50,
            }}
            axisLeft={{
                tickSize: 5,
                tickPadding: 5,
                tickRotation: 0,
                legend: 'Antal ture uden køretøj',
                legendPosition: 'middle',
                legendOffset: -40,
                tickValues: yTicks
            }}
            labelSkipWidth={12}
            labelSkipHeight={12}
            labelTextColor={{
                from: 'color',
                modifiers: [['darker', 1.6]],
            }}
            legends={[
                {
                    dataFrom: 'keys',
                    anchor: 'top',
                    direction: 'row',
                    justify: false,
                    translateX: 0,
                    translateY: -25,
                    itemsSpacing: 10,
                    itemWidth: 80,
                    itemHeight: 20,
                    itemDirection: 'left-to-right',
                    itemOpacity: 0.75,
                    symbolSize: 12,
                    symbolShape: 'circle',
                    symbolBorderColor: 'rgba(0, 0, 0, .5)',
                    effects: [
                        {
                            on: 'hover',
                            style: {
                                itemOpacity: 1,
                            },
                        },
                    ],
                },
            ]}
        />
    );
};

export default TripsByDayGraph;
