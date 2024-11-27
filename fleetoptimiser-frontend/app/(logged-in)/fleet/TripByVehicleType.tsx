import { ResponsiveBar } from '@nivo/bar';

export type entry = {
    km: number;
    Cykel: number;
    'El-cykel': number;
    'El-bil': number;
    'Fossil-bil': number;
    'Ikke tildelt': number;
};

type props = {
    data: entry[];
};

type Colors = {
    [key: string]: string;
};

const TripByVehicleType = ({ data }: props) => {
    // Used to fix the number of labels so they don't overlap
    const valuesToShow = data.map((v, i) => (i % Math.round(data.length / 10) === 0 ? v.km : 0));
    const sumsY = data.map(km => {
        return (Object.keys(km) as Array<keyof entry>).reduce((sum: number, key) => {
            return key !== 'km' ? sum + km[key] : sum;
        }, 0);
    });

    const yTicks = getYTicks(sumsY)
    const colors: Colors = { Cykel: '#40dd7f', 'El-cykel': '#ffbc1f', 'El-bil': '#109cf1', 'Fossil-bil': '#ff6760', 'Ikke tildelt': '#52575c' };

    return (
        <ResponsiveBar
            data={data.sort((a, b) => a.km - b.km)}
            keys={['Cykel', 'El-cykel', 'El-bil', 'Fossil-bil', 'Ikke tildelt']}
            indexBy="km"
            margin={{ top: 10, right: 130, bottom: 50, left: 60 }}
            padding={0.3}
            valueScale={{ type: 'linear' }}
            indexScale={{ type: 'band', round: true }}
            colors={(e) => colors[e.id]}
            defs={[
                {
                    id: 'dots',
                    type: 'patternDots',
                    background: 'inherit',
                    color: '#38bcb2',
                    size: 4,
                    padding: 1,
                    stagger: true,
                },
                {
                    id: 'lines',
                    type: 'patternLines',
                    background: 'inherit',
                    color: '#eed312',
                    rotation: -45,
                    lineWidth: 6,
                    spacing: 10,
                },
            ]}
            borderColor={{
                from: 'color',
                modifiers: [['darker', 1.6]],
            }}
            axisTop={null}
            axisRight={null}
            axisBottom={{
                tickSize: 5,
                tickPadding: 5,
                tickRotation: 0,
                legend: 'Turlængde km',
                legendPosition: 'middle',
                legendOffset: 32,
                format: (v) => (valuesToShow.find((vts) => vts === v) ? v : ''),
            }}
            axisLeft={{
                tickSize: 5,
                tickPadding: 5,
                tickRotation: 0,
                legend: 'Antal ture',
                legendPosition: 'middle',
                legendOffset: -40,
                tickValues: yTicks,
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
                    anchor: 'bottom-right',
                    direction: 'column',
                    justify: false,
                    translateX: 120,
                    translateY: 0,
                    itemsSpacing: 2,
                    itemWidth: 100,
                    itemHeight: 20,
                    itemDirection: 'left-to-right',
                    itemOpacity: 0.85,
                    symbolSize: 20,
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
            role="application"
            ariaLabel="Nivo bar chart demo"
            barAriaLabel={function (e) {
                return e.id + ': ' + e.formattedValue + ' in country: ' + e.indexValue;
            }}
        />
    );
};


export const getYTicks = (sums: number[], maxTicks: number = 5) => {
    const maxAntal = Math.max(...sums);
    if (maxAntal === 0) {
        return [0];
    }
    const increment = Math.ceil((maxAntal) / (maxTicks - 1));
    let ticks = [];
    for (let i = 0; i <= maxAntal; i += increment) {
        ticks.push(i);
    }
    if (!ticks.includes(maxAntal)) {
        ticks.push(maxAntal);
    }
    return ticks;
};


export default TripByVehicleType;
