import { useEffect, useContext } from 'react';

import AuthContext from '../context/AuthProvider';
import axios from '../api/axios';
import { Navigate } from 'react-router-dom';
import { getCookie, setCookie } from '../util/cookie';

const LOGOUT_URL = '/logout';

const Logout = () => {
    // @ts-ignore
    const { auth, setAuth } = useContext(AuthContext);

    useEffect(() => {
        const logout = async () => {
            const username: string = auth.username || getCookie('username');
            const authKey: string = auth.authKey || getCookie('authKey');

            const response = await axios.post(LOGOUT_URL,
                {
                    "username": username,
                    "authKey": authKey
                }, {
                    withCredentials: true
                }
            );
            setAuth({ 'user': response?.data?.username })
            // Clear cookies
            setCookie('username', null);
            setCookie('authKey', null);
            setCookie('role', null);
            setCookie('sessionKey', null);
        }
        logout();
    });

    return (
        <Navigate to="/" />
    )
}

export default Logout;
