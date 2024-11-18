import { Button, Modal } from '@mui/material';
import { AiOutlineClose } from 'react-icons/ai';
import { useState } from 'react';
import { ShiftForm } from '@/components/ShiftSettingsForm';
import { useAppSelector } from '@/components/redux/hooks';
import { shift_settings } from '@/components/hooks/useGetSettings';
import ScheduleIcon from '@mui/icons-material/Schedule';
import IconTextCard from "@/components/IconCard";

type organisedLocationShifts = Record<string, shift_settings>;

const ShiftModal = ({ locationId, buttonText, locationIds }: { locationId?: number; buttonText?: string; locationIds?: number[] }) => {
    const [open, setOpen] = useState<boolean>(false);
    const handleOpen = () => setOpen(true);
    const handleClose = () => setOpen(false);

    const locationIdSettings = useAppSelector(
        (state) =>
            state.simulation.settings.shift_settings.find((shiftSettings) => shiftSettings.location_id === locationId) || {
                location_id: locationId,
                shifts: [],
            }
    );
    const locationIdsSettings = useAppSelector((state) =>
        state.simulation.settings.shift_settings.filter((shiftLocation) => state.simulation.location_ids?.includes(shiftLocation.location_id))
    );
    const locationIdssSettings = useAppSelector((state) => {
        const { location_ids, settings } = state.simulation;

        return (location_ids || []).reduce((acc: organisedLocationShifts, locationId) => {
            const shiftSetting = settings.shift_settings.find((shiftLocation) => shiftLocation.location_id === locationId);

            acc[locationId] = shiftSetting || { location_id: locationId, shifts: [], address: '' };

            return acc;
        }, {});
    });

    let modalContent
    if (locationId) {
        modalContent = locationIdSettings && <ShiftForm locationId={locationId} shifts={locationIdSettings.shifts}></ShiftForm>
    }
    else {
        modalContent = locationIds && locationIds.map((locId) => (
            <div key={'shiftdiv' + locationIdssSettings[locId].location_id} className="my-8">
                <ShiftForm
                    key={'ShiftFormKey' + locationIdssSettings[locId].location_id}
                    locationId={locationIdssSettings[locId].location_id}
                    shifts={locationIdssSettings[locId].shifts}
                    addressName={locationIdssSettings[locId].address}
                    closeIt={handleClose}
                ></ShiftForm>
            </div>
        ))
    }

    return (
        <>
            <IconTextCard icon={<ScheduleIcon/>} text="Vagtlag" onClick={handleOpen}></IconTextCard>
            <Modal open={open} onClose={handleClose} className="m-10 overflow-y-auto mx-auto flex items-center justify-center">
                <div className="relative max-h-[80vh] w-[550px] bg-white rounded p-8 overflow-y-auto">
                    <div className="flex justify-between pb-2 mb-8">
                        <h1 className="text-2xl">Vagtlagsindstillinger</h1>
                        <AiOutlineClose onClick={handleClose} size={30} className="cursor-pointer hover:text-blue-600" />
                    </div>
                    {modalContent}
                </div>
            </Modal>
        </>
    );

};

export default ShiftModal;
