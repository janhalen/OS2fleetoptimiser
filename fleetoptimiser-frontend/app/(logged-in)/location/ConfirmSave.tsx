import DialogTitle from '@mui/material/DialogTitle';
import Dialog from '@mui/material/Dialog';
import {Button, DialogActions} from "@mui/material";
import {useState} from "react";

export interface ConfirmSaveProps {
    // open: boolean;
    // setOpen: (open: boolean) => void;
    disabled: boolean;
    buttonText: string;
    handleSave: () => void;
}

export function ConfirmSave(props: ConfirmSaveProps) {
    const [open, setOpen] = useState<boolean>(false);
    const { disabled, buttonText, handleSave } = props;

    const handleClose = () => {
        setOpen(false);
    };

    const handleConfirm = () => {
        handleSave()
        setOpen(false);
    };

    return (
        <>
            <Button
                variant="contained"
                color="primary"
                disabled={disabled}
                onClick={() => setOpen(true)}
                >{buttonText}</Button>
            <Dialog onClose={handleClose} open={open}>
                <DialogTitle>Vil du gemme ændringerne?</DialogTitle>
                <DialogActions>
                    <Button variant="contained" color="primary" onClick={handleConfirm} >Ja</Button>
                    <Button variant="outlined" color="secondary" onClick={handleClose}>Nej</Button>
                </DialogActions>
            </Dialog>
            </>
    );
}
