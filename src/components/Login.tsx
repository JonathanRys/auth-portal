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
    const [authKey, setAuthKey] = useState('');
    const [role, setRole] = useState('');
    const [errMsg, setErrMsg] = useState('');
    // temp until navigation is set up
    const [success, setSuccess] = useState(false);

    useEffect(() => {
        userRef?.current.focus();
    }, [])

    useEffect(() => {
        setErrMsg('');
    }, [user, password])

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();

        try {
            console.log('POSTing to', LOGIN_URL)
            try {
                const response = await axios.post(LOGIN_URL, 
                    {
                        "username": user,
                        "password": password,
                        "authKey": authKey
                    }, {
                        withCredentials: true
                    }
                );

                console.log('DEBUG:', response)

                if (response?.status !== 200) {
                    throw new Error(`Request failed with status ${response?.status}`);
                }

                setAuthKey(response?.data?.authKey);
                setRole(response?.data?.role);
            } catch (e) {
                console.log('error', e)
            }

            setAuth({ user, password, role, authKey })
            setCookie('user', user);
            setCookie('role', role);
            if (authKey) {
                setCookie('authKey', authKey);
            }

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
                setErrMsg('Login failed.')
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
                        <button disabled={!user || !password ? true : false}>Sign In</button>
                        <div className="login-links">
                            <p>
                                Need an account?<br/>
                                <span className="inline">
                                    <a href="/register">Sign Up</a>
                                </span>
                            </p>
                            <p>
                                <span className="inline">
                                    <a href="/reset_password">Forgot password?</a>
                                </span>
                            </p>
                        </div>
                    </form>
                </section>
            )}
        </>
    )
}

export default Login
