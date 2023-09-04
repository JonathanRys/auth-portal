import { useState, useEffect, useRef, useContext } from 'react';

import { setCookie } from '../util/cookie';
import AuthContext from '../context/AuthProvider';
import axios from '../api/axios';
import { Navigate, useSearchParams } from 'react-router-dom';

const CONFIRM_EMAIL_URL = '/confirm_email';

const ConfirmEmail = () => {
    // @ts-ignore
    const { setAuth } = useContext(AuthContext);

    const errRef = useRef<HTMLParagraphElement>();

    const [errMsg, setErrMsg] = useState('');
    const [success, setSuccess] = useState(false);
    const [searchParams] = useSearchParams();

    useEffect(() => {
        const confirm = async () => {
            try {
                console.log('POSTing to', CONFIRM_EMAIL_URL);
                const response = await axios.post(CONFIRM_EMAIL_URL,
                {
                    "accessKey": searchParams.get('accessKey')
                }, {
                    withCredentials: true
                });
        
                setAuth({
                    'user': response?.data?.username, 
                    'sessionKey': response?.data?.sessionKey,
                    'role': response?.data?.role,
                    'authKey': response?.data?.authKey
                });

                setCookie('user', response?.data?.username);
                setCookie('roles', response?.data?.role);
                setCookie('authKey', response?.data?.authKey);
                setCookie('sessionKey', response?.data?.sessionKey);
                setSuccess(true);
            } catch (e) {
                setErrMsg(e.message)
            
                if (e?.response) {
                    setErrMsg('No server response');
                } else if (e.response?.status === 401) {
                    setErrMsg('Unauthorized.');
                } else {
                    setErrMsg('Login Failed.')
                }
            }
        }
        confirm();
    }, [searchParams, setAuth]);

    return (
        <>
            {success ? (
                <Navigate to="/gpt" />
            ) :(
                <section>
                    <p
                        ref={errRef} 
                        className={errMsg ? 'error': 'aria-hidden'}
                        aria-live="assertive">
                        {errMsg}
                    </p>
                    <h1>Email confirmed</h1>
                    <p>Your email has been confiremed.</p>                        

                    <p>Continue?
                        <span className="inline">
                            <a href="/gpt">Phys GPT</a>
                        </span>
                    </p>
                </section>
            )}
        </>
    )
}

export default ConfirmEmail;
