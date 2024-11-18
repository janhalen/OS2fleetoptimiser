import { ComputedCell, ResponsiveHeatMapCanvas } from '@nivo/heatmap';
import 'd3-scale-chromatic';
import dayjs from 'dayjs';

export type HeatMapGroupWithMetaData = {
    x: string;
    y: number | null | undefined;
    startDate: dayjs.Dayjs;
    endDate: dayjs.Dayjs;
};

export type heatmapData = {
    id: string;
    data: HeatMapGroupWithMetaData[];
    idInt?: number;
}[];

export const DrivingHeatmapKm = ({
    data,
    maxHeatValue,
    setLocationZoom,
}: {
    data: heatmapData;
    maxHeatValue?: number;
    setLocationZoom: (cell: ComputedCell<HeatMapGroupWithMetaData>) => void;
}) => {
    return (
        <div className="hover:cursor-pointer h-full">
            <ResponsiveHeatMapCanvas
                data={data}
                margin={{ top: 90, right: 150, bottom: 60, left: 50 }}
                valueFormat={(v) => Math.round(v).toLocaleString()}
                yInnerPadding={0.15}
                axisTop={{
                    tickSize: 5,
                    tickPadding: 5,
                    tickRotation: -90,
                    legend: '',
                    legendOffset: 46,
                }}
                label={(props) => props.formattedValue ?? '0'}
                onClick={(cell) => {
                    setLocationZoom(cell);
                }}
                axisLeft={null}
                axisRight={{
                    tickSize: 5,
                    tickPadding: 5,
                    tickRotation: 30,
                }}
                colors={{
                    type: 'sequential',
                    colors: ['#ff4545', '#ffffff'],
                    minValue: 0,
                    maxValue: maxHeatValue,
                }}
                emptyColor="#b6b7b9"
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
                        tickFormat: '>-.2s',
                        title: 'Kørte km →',
                        titleAlign: 'start',
                        titleOffset: 4,
                    },
                ]}
            />
        </div>
    );
};
