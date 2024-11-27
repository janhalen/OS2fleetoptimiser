import { TextField } from '@mui/material';
import { createColumnHelper, flexRender, getCoreRowModel, useReactTable } from '@tanstack/react-table';
import { useAppSelector, useAppDispatch } from '@/components/redux/hooks';
import { Vehicle } from '@/components/hooks/useGetVehicles';
import { setSimulationVehicle } from '@/components/redux/SimulationSlice';

export type CarCumulative = {
    vehicle: Vehicle;
    count: number;
    extra: boolean;
};

const columnHelper = createColumnHelper<CarCumulative>();

const Tfield = ({ id }: { id: number }) => {
    const dispatch = useAppDispatch();
    return (
        <TextField
            key={id + 10}
            value={useAppSelector((state) => state.simulation.fleetSimulationSettings.simulation_vehicles.find((c) => c.id === id)?.simulation_count ?? 0)}
            onChange={(e) => {
                if (!isNaN(+e.target.value)) {
                    dispatch(setSimulationVehicle({ id: id, simulation_count: +e.target.value }));
                }
            }}
            inputProps={{ className: 'text-right no-border-bottom', inputMode: 'numeric' }}
            variant="filled"
        ></TextField>
    );
};

const propellantFormat = (vehicle: Vehicle) => {
    if (vehicle.wltp_el) {
        return vehicle.wltp_el.toLocaleString() + ' Wh/km';
    } else if (vehicle.wltp_fossil) {
        return vehicle.wltp_fossil.toLocaleString() + ' km/l';
    } else {
        return 'Intet drivmiddel';
    }
};

const defaultColumns = [
    columnHelper.display({
        id: 'Type',
        header: () => <div className="text-left cartable">Biltype</div>,
        cell: (row) => {
            const fullText = row.row.original.vehicle.make + ' ' + row.row.original.vehicle.model
            const truncatedText = fullText.length > 20 ? fullText.substring(0, 20) + '...' : fullText;
            return (
                <span className={row.row.original.extra ? 'text-blue-500' : ''} title={fullText}>
                    {truncatedText}
                </span>
            );
        },
    }),
    columnHelper.accessor((row) => row.vehicle.omkostning_aar, {
        id: 'Cost',
        header: () => <div className="text-right cartable">DKK/år</div>,
        cell: (row) => <div className="text-right">{row.getValue()?.toLocaleString()}</div>,
    }),
    columnHelper.display({
        id: 'Consumption',
        header: () => <div className="text-right cartable">Forbrug</div>,
        cell: (props) => <div className="text-right">{propellantFormat(props.row.original.vehicle)}</div>,
    }),
    columnHelper.accessor((row) => row.count, {
        id: 'currentCount',
        header: () => <div className="text-right cartable">Nuværende antal</div>,
        cell: (row) => <div className="text-right">{row.getValue()}</div>,
    }),
    columnHelper.display({
        id: 'SimulationCount',
        header: () => <div className="text-right cartable">Simulation antal</div>,
        cell: (cell) => (
            <div className="simantal flex justify-end">
                <Tfield key={cell.row.original.vehicle.id} id={cell.row.original.vehicle.id}></Tfield>
            </div>
        ),
    }),
];

const CarsTable = ({ cars }: { cars: CarCumulative[] }) => {
    const table = useReactTable({
        data: cars,
        columns: defaultColumns,
        getCoreRowModel: getCoreRowModel(),
    });

    return (
        <table className="w-full border-collapse p-2">
            <thead style={{ position: 'sticky', top: '0px', background: '#fff', zIndex: 2 }}>
                {table.getHeaderGroups().map((headerGroup) => (
                    <tr className="border-b" key={headerGroup.id}>
                        {headerGroup.headers.map((header) => (
                            <th key={header.id}>{header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())}</th>
                        ))}
                    </tr>
                ))}
            </thead>
            <tbody>
                {table.getRowModel().rows.map((row) => (
                    <tr className="border-b" key={row.id}>
                        {row.getVisibleCells().map((cell) => (
                            <td className="ct" key={cell.id}>
                                {flexRender(cell.column.columnDef.cell, cell.getContext())}
                            </td>
                        ))}
                    </tr>
                ))}
            </tbody>
            <tfoot className="border-t-2 border-black ct">
                <tr>
                    <td>Total</td>
                    <td></td>
                    <td></td>
                    <td className="text-right px-1">{cars.reduce((acc, curr) => acc + curr.count, 0)}</td>
                    <td className="text-right p-2">
                        {useAppSelector((state) =>
                            state.simulation.fleetSimulationSettings.simulation_vehicles.reduce((acc, curr) => acc + curr.simulation_count, 0)
                        )}
                    </td>
                </tr>
            </tfoot>
        </table>
    );
};

export default CarsTable;
