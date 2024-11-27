import { TbZoomCancel } from 'react-icons/tb';

const SearchAbortedMessage = () => {
    return (
        <div className="flex flex-col justify-center items-center h-80">
            <TbZoomCancel className="pb-2" size={100}></TbZoomCancel>
            <p>Den automatiske simulering blev afbrudt.</p>
        </div>
    );
};

export default SearchAbortedMessage;
