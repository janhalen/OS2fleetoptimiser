'use client';
import { MdManageSearch } from 'react-icons/md';

const AddFilter = () => {
    return (
        <div className="flex flex-col justify-center items-center">
            <MdManageSearch size={80} />
            <p>Vælg et filter; lokation, køretøj, forvaltning eller afdeling</p>
        </div>
    );
};

export default AddFilter;
