import { Button, LinearProgress } from '@mui/material';

type props = {
    progress: number;
    status: string;
    setCancel: () => void;
    buttonText?: string;
    pendingText?: string;
};

const LoadingOverlay = ({ progress, status, setCancel, buttonText, pendingText }: props) => {
    console.log("status", status, pendingText, progress)
    return (
        <div style={{ backgroundColor: 'rgba(255, 255, 255, 0.75)', width: '100%', height: '100%', zIndex: '10', top: '0', left: '0', position: 'fixed' }}>
            <div className="fixed z-10 left-0 top-0 bg-opacity-30 overflow-hidden w-full h-full">
                <div className="relative w-1/3 top-1/2 mx-auto">
                    <div className="flex flex-col items-center">
                        <LinearProgress className="mb-2 w-full" variant="determinate" value={progress} />
                        <p>{
                                status === 'PENDING' ?
                                    pendingText ?? 'Starter simulering' :
                                        (pendingText && status !== 'PENDING' ?
                                            pendingText + ' ' + Math.round(progress) + ' %' :
                                                Math.round(progress) + ' %')
                        } </p>
                        <Button className="w-fit" variant="contained" color="error" onClick={() => setCancel()}>
                            {buttonText ?? 'Afbryd simulering'}
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default LoadingOverlay;
