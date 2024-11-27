import { Button, Modal } from '@mui/material';
import { useState } from 'react';
import { AiOutlineClose } from 'react-icons/ai';
import BikeForm from '@/components/BikeSettingsForm';
import { useAppSelector } from '@/components/redux/hooks';
import PedalBikeIcon from '@mui/icons-material/PedalBike';
import IconTextCard from "@/components/IconCard";

const BikeSettingsModal = () => {
    const [open, setOpen] = useState<boolean>(false);
    const handleOpen = () => setOpen(true);
    const handleClose = () => setOpen(false);

    const settings = useAppSelector((state) => state.simulation.settings.bike_settings);

    return (
        <>
            <IconTextCard icon={<PedalBikeIcon/>} text="Cykelegenskaber" onClick={handleOpen}/>
            <Modal open={open} onClose={handleClose} className="m-10 overflow-x-scroll mx-auto flex items-center justify-center">
                <div className="relative bg-white p-4 rounded p-8">
                    <div className="flex justify-between pb-2 mb-8">
                        <h1 className="text-2xl">Konfigurér cykelegenskaber</h1>
                        <AiOutlineClose onClick={handleClose} size={30} className="cursor-pointer hover:text-blue-600" />
                    </div>
                    <BikeForm
                        maxTripDistance={settings.max_km_pr_trip}
                        percentTaken={settings.percentage_of_trips}
                        bikeIntervals={settings.bike_slots.map((slot) => ({ start: slot.bike_start, end: slot.bike_end }))}
                        bikeSpeed={settings.bike_speed}
                        electricalBikeSpeed={settings.electrical_bike_speed}
                    />
                </div>
            </Modal>
        </>
    );
};

export default BikeSettingsModal;
