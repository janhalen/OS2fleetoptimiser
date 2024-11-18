import { ResponsiveLine } from '@nivo/line';

type dataPoint = {
    x: string;
    y: number;
};

type props = {
    data: {
        id: string;
        data: dataPoint[];
    }[];
    yLabel: string;
    color: string;
};

const DateLineGraph = ({ data, yLabel, color }: props) => {
    return (
        <ResponsiveLine
            margin={{ top: 20, right: 20, bottom: 60, left: 80 }}
            animate={true}
            data={data}
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
                return value.toFixed(3).replace('.', ',');
            }}
            axisLeft={{
                legend: yLabel,
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
            enableArea={true}
        />
    );
};

export default DateLineGraph;
