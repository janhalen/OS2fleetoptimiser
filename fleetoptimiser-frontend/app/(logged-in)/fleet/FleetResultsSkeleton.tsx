import { Skeleton } from '@mui/material';

const FleetResultSkeleton = () => {
    return (
        <>
            <div className="flex justify-between mb-2">
                <Skeleton variant="rectangular" className="flex-1 drop-shadow-md h-24"></Skeleton>
                <Skeleton variant="rectangular" className="flex-1 mx-2 drop-shadow-md h-24"></Skeleton>
                <Skeleton variant="rectangular" className="flex-1 drop-shadow-md h-24"></Skeleton>
            </div>
            <Skeleton className="h-96 mb-2 drop-shadow-md" variant="rectangular"></Skeleton>
            <Skeleton className="h-96 mb-2 drop-shadow-md" variant="rectangular"></Skeleton>
            <Skeleton className="h-96 drop-shadow-md" variant="rectangular"></Skeleton>
        </>
    );
};

export default FleetResultSkeleton;
