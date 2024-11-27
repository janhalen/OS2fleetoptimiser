'use client';

import React, {createContext, useContext, useState, ReactNode} from 'react';

interface WritePrivilege {
    hasWritePrivilege: boolean;
    setHasWritePrivilege: (value: boolean) => void;
}

const WritePrivilegeContext = createContext<WritePrivilege | undefined>(undefined);

export const useWritePrivilegeContext = () => {
    const context = useContext(WritePrivilegeContext);
    if (context === undefined){
        throw new Error("useWritePrivilegeContext must be used within a WritePrivilegeProvider")
    }
    return context
}

export const WritePrivilegeProvider = ({children} : { children: ReactNode }) => {
    const [hasWritePrivilege, setHasWritePrivilege] = useState<boolean>(false);
    return (
        <WritePrivilegeContext.Provider value={{ hasWritePrivilege, setHasWritePrivilege }}>
            {children}
        </WritePrivilegeContext.Provider>
    )
}
