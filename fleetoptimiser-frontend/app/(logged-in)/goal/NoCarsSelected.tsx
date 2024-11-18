import { TbCarOff } from "react-icons/tb";

const NoCarsSelectedMessage = () => {
    return (
        <div className="flex flex-col justify-center items-center h-80">
            <TbCarOff className="pb-2" size={100}></TbCarOff>
            <p>Der var ingen valgte biler i simuleringen.</p>
        </div>
    );
};

export default NoCarsSelectedMessage;
