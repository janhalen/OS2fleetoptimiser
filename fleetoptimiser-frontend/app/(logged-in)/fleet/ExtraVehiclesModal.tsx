import { Button, CircularProgress, Modal } from '@mui/material';
import { useState } from 'react';
import { AiOutlineClose } from 'react-icons/ai';
import ApiError from '@/components/ApiError';
import ExtraVehicleTable from './ExtraVehicleTable';
import { useAppDispatch, useAppSelector } from '@/components/redux/hooks';
import useGetUniqueVehicles from '@/components/hooks/useGetUniqueVehicles';
import { addExtraVehicles, clearExtraVehicles } from '@/components/redux/SimulationSlice';
import { Vehicle } from '@/components/hooks/useGetVehicles';
import CommuteIcon from '@mui/icons-material/Commute';
import IconTextCard from "@/components/IconCard";

const ExtraVehicleModal = () => {
    const [open, setOpen] = useState<boolean>(false);
    const handleOpen = () => setOpen(true);
    const handleClose = () => setOpen(false);
    const dispatch = useAppDispatch();

    const cars = useGetUniqueVehicles();
    const selectedVehicles = useAppSelector((state) => state.simulation.selectedVehicles);

    const filterPreselectedVehicles = (availableVehicles: Vehicle[], selectedVehicles: Vehicle[]) =>
        availableVehicles.filter((v) => {
            // vehicle has omkostning filled and either wltp_el or wltp_fossil if it's not a bike
            const meetsConditions =
                v.omkostning_aar != null && (v.wltp_el != null || v.wltp_fossil != null || ((v.type?.id === 1 || v.type?.id === 2) && v.fuel?.id === 10));

            const isNotSelected = !selectedVehicles.find(
                (car) =>
                    car.make === v.make &&
                    car.model === v.model &&
                    car.omkostning_aar === v.omkostning_aar &&
                    car.wltp_el === v.wltp_el &&
                    car.wltp_fossil === v.wltp_fossil
            );

            return meetsConditions && isNotSelected;
        });

    return (
        <>
            <IconTextCard icon={<CommuteIcon/>} text="Testkøretøjer" onClick={handleOpen}/>
            <Modal open={open} onClose={handleClose} className="m-10 overflow-scroll lg:mx-96">
                <div className="bg-white p-4 w-full ">
                    <div className="flex justify-between border-b pb-2 mb-2">
                        <h1 className="text-2xl">Tilføj køretøjer</h1>
                        <AiOutlineClose onClick={handleClose} size={30} className="cursor-pointer hover:text-blue-600" />
                    </div>

                    {cars.isError && <ApiError retryFunction={cars.refetch}>Køretøjerne kunne ikke hentes.</ApiError>}
                    {cars.isLoading && <CircularProgress />}
                    {cars.data && (
                        <>
                            <div className="flex justify-end">
                                <Button className="mx-2" onClick={() => dispatch(addExtraVehicles(filterPreselectedVehicles(cars.data, selectedVehicles)))}>
                                    Tilføj alle
                                </Button>
                                <Button className="mx-2" onClick={() => dispatch(clearExtraVehicles())}>
                                    Fjern alle
                                </Button>
                            </div>
                            <ExtraVehicleTable cars={filterPreselectedVehicles(cars.data, selectedVehicles)}></ExtraVehicleTable>
                        </>
                    )}
                </div>
            </Modal>
        </>
    );
};

export default ExtraVehicleModal;
