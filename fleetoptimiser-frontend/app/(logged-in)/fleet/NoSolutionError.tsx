import { TbCarCrash } from 'react-icons/tb';

type NoSolutionErrorProps = {
    extraMessage?: string | null;
};

const NoSolutionError = ({ extraMessage = null }: NoSolutionErrorProps) => {
    const lastParagraph = typeof extraMessage === 'string' ? extraMessage.split('\n').pop() : null;

    return (
        <div className="flex flex-col justify-center items-center h-80">
            <TbCarCrash className="pb-2" size={100}></TbCarCrash>
            <p>Der blev ikke fundet nogen løsninger</p>
            {lastParagraph && <p>{lastParagraph}</p>}
        </div>
    );
};

export default NoSolutionError;
