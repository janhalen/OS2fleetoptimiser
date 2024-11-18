import DialogTitle from '@mui/material/DialogTitle';
import Dialog from '@mui/material/Dialog';
import {Button, DialogActions} from "@mui/material";

export interface ConfirmDeletionProps {
    open: boolean;
    parkingType: string;
    parkingId?: number;
    setOpen: (open: boolean) => void;
    handleDelete: (parkingType: string, parkingId?: number) => void;
}

export function ConfirmDeletion(props: ConfirmDeletionProps) {
    const { setOpen, parkingType, parkingId, handleDelete, open } = props;

    const handleClose = () => {
        setOpen(false);
    };

    const handleConfirm = (parkingType: string, parkingId?: number) => {
        handleDelete(parkingType, parkingId)
        setOpen(false);
    };

    return (
        <Dialog onClose={handleClose} open={open}>
            <DialogTitle>Er du sikker på at du vil slette parkeringspunktet?</DialogTitle>
            <DialogActions>
                <Button variant="contained" color="error" onClick={() => handleConfirm(parkingType, parkingId)} >Ja, Slet</Button>
                <Button variant="contained" color="secondary" onClick={handleClose}>Fortryd</Button>
            </DialogActions>
        </Dialog>
    );
}
