import { ResponsiveLine } from '@nivo/line';
import { getYTicks } from "@/app/(logged-in)/fleet/TripByVehicleType";

type entry = {
    id: string;
    data: {
        x: string; //date
        y: number; //amount
    }[];
};

type props = {
    data: entry[];
};

type Colors = {
    [key: string]: string;
};

const TripByDateGraph = ({ data }: props) => {
    const colors: Colors = { Simulation: '#109cf1', Nuværende: '#52575c' };
    let i = 0;
    const ySums = data.map(simulationType =>
        {return Math.max(...simulationType.data.map(dataEntry => dataEntry.y))}
    )
    const yTicks = getYTicks(ySums)
    return (
        <ResponsiveLine
            data={data}
            colors={(e) => colors[e.id]}
            margin={{ top: 40, right: 40, bottom: 80, left: 60 }}
            xScale={{ type: 'point' }}
            yScale={{
                type: 'linear',
                min: 'auto',
                max: 'auto',
                stacked: false,
                reverse: false,
            }}
            yFormat=" >-.2f"
            axisTop={null}
            axisRight={null}
            axisBottom={{
                tickPadding: 5,
                tickRotation: 40,
                legend: 'Dato',
                legendOffset: 60,
                legendPosition: 'middle',
            }}
            axisLeft={{
                tickSize: 5,
                tickPadding: 5,
                tickRotation: 0,
                legend: 'Antal ture uden køretøj',
                legendOffset: -40,
                legendPosition: 'middle',
                tickValues: yTicks,
            }}
            pointSize={10}
            pointColor={{ theme: 'background' }}
            pointBorderWidth={2}
            pointBorderColor={{ from: 'serieColor' }}
            pointLabelYOffset={-12}
            useMesh={true}
            legends={[
                {
                    anchor: 'top',
                    direction: 'row',
                    justify: false,
                    translateX: 0,
                    translateY: -25,
                    itemsSpacing: 10,
                    itemDirection: 'left-to-right',
                    itemWidth: 80,
                    itemHeight: 20,
                    itemOpacity: 0.75,
                    symbolSize: 12,
                    symbolShape: 'circle',
                    symbolBorderColor: 'rgba(0, 0, 0, .5)',
                    effects: [
                        {
                            on: 'hover',
                            style: {
                                itemBackground: 'rgba(0, 0, 0, .03)',
                                itemOpacity: 1,
                            },
                        },
                    ],
                },
            ]}
        />
    );
};

export default TripByDateGraph;
