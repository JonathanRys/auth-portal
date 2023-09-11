import { useState, useEffect, useRef, useContext, FormEvent } from 'react';

import { setCookie } from '../util/cookie';
import AuthContext from '../context/AuthProvider';
import axios from '../api/axios';
import { Navigate } from 'react-router-dom';

const LOGIN_URL = '/login';

const Login = () => {
    console.log('login loading 1')
    // @ts-ignore
    const { setAuth } = useContext(AuthContext);

    const userRef = useRef<HTMLInputElement>();
    const errRef = useRef<HTMLParagraphElement>();

    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    const [errMsg, setErrMsg] = useState('');
    // temp until navigation is set up
    const [success, setSuccess] = useState(false);

    useEffect(() => {
        userRef?.current.focus();
    }, [])

    useEffect(() => {
        setErrMsg('');
    }, [username, password])
    console.log('login loading 2')

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        console.log('SUBMITTING')

        try {
            try {
                const response = await axios.post(LOGIN_URL, 
                    {
                        "username": username,
                        "password": password
                    }, {
                        withCredentials: true
                    }
                );

                if (response?.status !== 200) {
                    throw new Error(`Request failed with status ${response?.status}`);
                }

                const _role = response?.data?.role
                const _authKey = response?.data?.authKey
                const _sessionKey = response?.data?.sessionKey

                setAuth({ username, _role, _sessionKey, _authKey });
                setCookie('username', username);
                setCookie('role', _role);
                if (_authKey) {
                    setCookie('authKey', _authKey);
                }
                if (_sessionKey) {
                    setCookie('sessionKey', _sessionKey);
                }
            } catch (e) {
                console.log('error', e);
            }

            setUsername('');
            setPassword('');
            setSuccess(true);
        } catch (e) {
            if (e?.response) {
                setErrMsg('No server response');
            } else if (e.response?.status === 409) {
                // missing username or password
                setErrMsg('Missing username or password.');
            } else if (e.response?.status === 401) {
                setErrMsg('Unauthorized.');
            } else {
                setErrMsg('Login failed.');
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
                            onChange={e => setUsername(e.target.value)}
                            value={username}
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
                        <button disabled={!username || !password ? true : false}>Sign In</button>
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
