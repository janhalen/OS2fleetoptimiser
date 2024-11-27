import { TbRoadOff } from 'react-icons/tb';

const NoTripsError = () => {
    return (
        <div className="flex flex-col justify-center items-center h-80">
            <TbRoadOff className="pb-2" size={100}></TbRoadOff>
            <p>Der er ingen kørte ture i den valgte periode</p>
        </div>
    );
};

export default NoTripsError;
