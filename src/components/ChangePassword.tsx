import { useState, useEffect, useRef, useContext, FormEvent } from 'react';

import { setCookie } from '../util/cookie';
import AuthContext from '../context/AuthProvider';
import axios from '../api/axios';
import { Navigate } from 'react-router-dom';

const LOGIN_URL = '/login';

const Login = () => {
    // @ts-ignore
    const { setAuth } = useContext(AuthContext);

    const userRef = useRef<HTMLInputElement>();
    const errRef = useRef<HTMLParagraphElement>();

    const [user, setUser] = useState('');
    const [password, setPassword] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [apiKey, setApiKey] = useState('');
    const [roles, setRoles] = useState('');
    const [errMsg, setErrMsg] = useState('');
    // temp until navigation is set up
    const [success, setSuccess] = useState(false);

    useEffect(() => {
        userRef?.current.focus();
    }, [])

    useEffect(() => {
        setErrMsg('');
    }, [user, password, newPassword])

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();

        try {
            console.log('POSTing to', LOGIN_URL)
            const response = await axios.post(LOGIN_URL, 
                {
                    "username": user,
                    "password": password,
                    "new_password": newPassword,
                    "apiKey": apiKey
                }, {
                    withCredentials: true
                }
            );

            console.log('DEBUG:', response)

            if (response?.status !== 200) {
                throw new Error(`Request failed with status ${response?.status}`);
            }

            setApiKey(response?.data?.apiKey);
            setRoles(response?.data?.roles);

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
            errRef?.current.focus();        
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
                        <label htmlFor="new_password">New Password:</label>
                        <input 
                            type="password"
                            id="new_password"
                            onChange={e => setNewPassword(e.target.value)}
                            value={newPassword}
                            required
                        />
                        <button disabled={!user || !password  || !newPassword? true : false}>Update password</button>
                        <p>
                            <span className="inline">
                                <a href="/gpt">Cancel</a>
                            </span>
                        </p>
                    </form>
                </section>
            )}
        </>
    )
}

export default Login
