import { createContext, useState } from 'react';
import { Props } from '../types/types'

import { getCookie } from '../util/cookie';


const AuthContext = createContext({});

export const AuthProvider = ({ children }: Props) => {
    const [auth, setAuth] = useState({
        "username": getCookie('username'),
        "role": getCookie('role'),
        "authKey": getCookie('authKey'),
    });

    return (
        <AuthContext.Provider value={{ auth, setAuth }}>
            {children}
        </AuthContext.Provider>
    )
}

export default AuthContext;
