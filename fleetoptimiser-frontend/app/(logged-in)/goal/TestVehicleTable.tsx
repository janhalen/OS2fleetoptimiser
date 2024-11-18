import { useAppDispatch, useAppSelector } from '@/components/redux/hooks';
import { Checkbox } from '@mui/material';
import { createColumnHelper, flexRender, getCoreRowModel, useReactTable, getSortedRowModel } from '@tanstack/react-table';
import { Vehicle } from '@/components/hooks/useGetVehicles';
import {
    addTestVehicle,
    addTestVehicleMeta,
    removeTestVehicle,
    removeTestVehicleMeta
} from '@/components/redux/SimulationSlice';

const columnHelper = createColumnHelper<Vehicle>();

const TestVehicleControl = ({ id, vehicle }: { id: number, vehicle: Vehicle }) => {
    const dispatch = useAppDispatch();
    return (
        <Checkbox
            onChange={(e) => {
                if (id) {
                    if (e.target.checked) {
                        dispatch(addTestVehicle(id));
                        dispatch(addTestVehicleMeta(vehicle));
                    } else {
                        dispatch(removeTestVehicle(id));
                        dispatch(removeTestVehicleMeta(vehicle));
                    }
                }
            }}
            checked={!!useAppSelector((state) => state.simulation.goalSimulationSettings.testVehicles.find((v) => v === id))}
        />
    );
};

const TestVehicleTable = ({ cars }: { cars: Vehicle[] }) => {
    // Can you select vehicles from the current fleet?
    const defaultColumns = [
        columnHelper.display({
            id: 'Type',
            header: () => <div className="text-left">Biltype</div>,
            cell: (props) => <div>{props.row.original.make} {props.row.original.model}</div>,
        }),
        columnHelper.display({
            id: 'Consumption',
            header: () => <div className="text-right">Drivmiddel forbrug</div>,
            cell: (props) => (
                <div className="text-right">
                    {props.row.original.wltp_el
                        ? `${props.row.original.wltp_el} Wh/km`
                        : props.row.original.wltp_fossil
                        ? `${props.row.original.wltp_fossil} km/l`
                        : 'Ikke udfyldt'}
                </div>
            ),
        }),
        columnHelper.accessor((row) => row.omkostning_aar, {
            id: 'Cost',
            header: () => <div className="text-right">Årlige omkostninger (DKK)</div>,
            cell: (row) => <div className="text-right">{row.getValue()}</div>,
        }),
        columnHelper.display({
            id: 'Selector',
            header: 'Vælg',
            cell: (props) => (
                <div className="text-center">
                    <TestVehicleControl id={props.row.original.id} vehicle={props.row.original} />
                </div>
            ),
        }),
    ];

    const table = useReactTable({
        data: cars,
        columns: defaultColumns,
        getCoreRowModel: getCoreRowModel(),
        getSortedRowModel: getSortedRowModel(),
        initialState: {sorting:[{id: 'Cost', desc: false}]},
    });

    return (
        <table className="w-full border-collapse">
            <thead className="border-b">
                {table.getHeaderGroups().map((headerGroup) => (
                    <tr className="border-b" key={headerGroup.id}>
                        {headerGroup.headers.map((header) => (
                            <th className="p-2" key={header.id}>
                                {header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())}
                            </th>
                        ))}
                    </tr>
                ))}
            </thead>
            <tbody>
                {table.getRowModel().rows.map((row) => (
                    <tr className="border-b" key={row.id}>
                        {row.getVisibleCells().map((cell) => (
                            <td className="p-2" key={cell.id}>
                                {flexRender(cell.column.columnDef.cell, cell.getContext())}
                            </td>
                        ))}
                    </tr>
                ))}
            </tbody>
        </table>
    );
};

export default TestVehicleTable;
