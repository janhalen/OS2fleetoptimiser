'use client';

import { useEffect } from 'react';
import { useWritePrivilegeContext } from "@/app/providers/WritePrivilegeProvider";

interface SetWritePrivilegeProps {
    hasPrivilege: boolean;
}

const SetWritePrivilege: React.FC<SetWritePrivilegeProps> = ({ hasPrivilege }) => {
    const { setHasWritePrivilege } = useWritePrivilegeContext();

    useEffect(() => {
        setHasWritePrivilege(hasPrivilege);
    }, [hasPrivilege, setHasWritePrivilege]);

    return null;
};

export default SetWritePrivilege;
