import { ResponsiveHeatMapCanvas } from '@nivo/heatmap';

type HeatMapGroupWithMetaData = {
    x: string;
    y: number;
};

export type heatmapData = {
    id: string;
    data: HeatMapGroupWithMetaData[];
}[];

export default function TimeActivityHeatMap({ data, threshold }: { data: heatmapData; threshold: number }) {
    return (
        <div className="hover:cursor-pointer h-full">
            <ResponsiveHeatMapCanvas
                data={data}
                margin={{ top: 90, right: 150, bottom: 60, left: 50 }}
                valueFormat={'>-.0%'}
                yInnerPadding={0.15}
                axisTop={{
                    tickSize: 5,
                    tickPadding: 5,
                    tickRotation: -90,
                    legend: '',
                    legendOffset: 46,
                }}
                axisRight={{
                    tickSize: 5,
                    tickPadding: 5,
                    tickRotation: 30,
                }}
                axisLeft={null}
                colors={{
                    type: 'sequential',
                    colors: ['#1976d2', '#ffffff'],
                    minValue: 0,
                    maxValue: threshold / 100,
                }}
                emptyColor="#555555"
                enableLabels={true}
                legends={[
                    {
                        anchor: 'bottom',
                        translateX: 0,
                        translateY: 30,
                        length: 400,
                        thickness: 8,
                        direction: 'row',
                        tickPosition: 'after',
                        tickSize: 3,
                        tickSpacing: 4,
                        tickOverlap: false,
                        tickFormat: '>-.0%',
                        title: 'Procentvis udnyttelse →',
                        titleAlign: 'start',
                        titleOffset: 4,
                    },
                ]}
                annotations={[]}
            />
        </div>
    );
}
