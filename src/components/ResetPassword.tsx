import { useState, useEffect, useRef, FormEvent } from 'react';

import { setCookie } from '../util/cookie';
import axios from '../api/axios';
import { Navigate } from 'react-router-dom';

const RESET_PW_URL = '/reset_password';

const ResetPassword = () => {
    const userRef = useRef<HTMLInputElement>();
    const errRef = useRef<HTMLParagraphElement>();

    const [user, setUser] = useState('');
    const [errMsg, setErrMsg] = useState('');
    // temp until navigation is set up
    const [success, setSuccess] = useState(false);

    useEffect(() => {
        userRef?.current.focus();
    }, [])

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();

        try {
            const response = await axios.post(RESET_PW_URL, 
                {
                    "username": user
                }, {
                    withCredentials: true
                }
            );

            if (response?.status !== 200) {
                throw new Error(`Request failed with status ${response?.status}`);
            }

            setCookie('user', user);
            setSuccess(true);
        } catch (e) {
            if (e?.response) {
                setErrMsg('No server response');
            } else if (e.response?.status === 409) {
                // missing username or password
                setErrMsg('Missing username or password.')
            } else if (e.response?.status === 401) {
                setErrMsg('Unauthorized.');
            } else {
                setErrMsg('Login Failed.')
            }
            errRef?.current.focus();        
        }
    }

    return (
        <>
            {success ? (
                <Navigate to="/login" />
            ) :(
                <section>
                    <p
                        ref={errRef} 
                        className={errMsg ? 'error': 'aria-hidden'}
                        aria-live="assertive">
                        {errMsg}
                    </p>
                    <h1>Reset Password</h1>
                    <form onSubmit={handleSubmit}>
                        <label htmlFor="username">Email:</label>
                            <input 
                                type="email"
                                id="username"
                                ref={userRef}
                                onChange={e => setUser(e.target.value)}
                                value={user}
                                required
                            />
                        <button disabled={!user}>Reset password</button>
                        <p>
                            <span className="inline">
                                <a href="/">Cancel</a>
                            </span>
                        </p>
                    </form>
                </section>
            )}
        </>
    )
}

export default ResetPassword
