import { getServerSession } from "next-auth/next";
import {authOptions} from "@/app/authOptions";

export async function checkWritePrivilege() {
    if (process.env.NODE_ENV === 'development') {
        return true
    }
    //@ts-ignore
    const session = await getServerSession(authOptions);
    if (!session){
        return false
    }
    if (!session.user){
        return false
    }
    //@ts-ignore
    return session.user.write_privilege
}
