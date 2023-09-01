import { useState, useEffect, useRef, useContext, FormEvent } from 'react';

import { setCookie } from '../util/cookie';
import AuthContext from '../context/AuthProvider';
import axios from '../api/axios';

import { Navigate } from 'react-router-dom';

const RESET_PASSWORD_URL = '/reset_password';

const ResetPassword = () => {
    // @ts-ignore
    const { setAuth } = useContext(AuthContext);

    const userRef = useRef<HTMLInputElement>();
    const errRef = useRef<HTMLParagraphElement>();

    const [user, setUser] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [errMsg, setErrMsg] = useState('');
    // temp until navigation is set up
    const [success, setSuccess] = useState(false);

    useEffect(() => {
        userRef.current.focus();
    }, [])

    useEffect(() => {
        setErrMsg('');
    }, [user, password])

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();

        try {
            const response = await axios.post(RESET_PASSWORD_URL, 
                JSON.stringify({
                    user, password
                }), {
                    headers: { 'Content-Type': 'application/json' },
                    withCredentials: true
                }
            );

            if (response?.status !== 200) {
                throw new Error(`Request failed with status ${response?.status}`);
            }

            const apiKey = response?.data?.apiKey;
            const roles = response?.data?.roles;

            setAuth({ user, password, roles, apiKey })
            setCookie('user', user);
            setCookie('roles', roles);
            setCookie('apiKey', apiKey);

            setUser('');
            setPassword('');
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
            errRef.current.focus();
        }
    }

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
                    <h1>Sign in</h1>
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
                        <label htmlFor="password">Password:</label>
                        <input 
                            type="password"
                            id="password"
                            onChange={e => setPassword(e.target.value)}
                            value={password}
                            required
                        />
                        <label htmlFor="password">Confirm password:</label>
                        <input 
                            type="password"
                            id="confirm-password"
                            onChange={e => setConfirmPassword(e.target.value)}
                            value={password}
                            required
                        />
                        <button disabled={!user || !password || !confirmPassword ? true : false}>Set Password</button>
                        <p>
                            Need an account?<br/>
                            <span className="inline">
                                <a href="/register">Sign Up</a>
                            </span>
                        </p>
                    </form>
                </section>
            )}
        </>
    )
}

export default ResetPassword
