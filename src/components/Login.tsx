import { useState, useEffect, useRef, useContext, FormEvent } from 'react';
import { faCheck, faTimes, faInfoCircle } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';

import { setCookie } from '../util/cookie';
import { isValidEmail, isValidPassword } from '../util/validations';
import AuthContext from '../context/AuthProvider';
import axios from '../api/axios';
import { Navigate } from 'react-router-dom';

const LOGIN_URL = '/login';

const Login = () => {
    // @ts-ignore
    const { setAuth } = useContext(AuthContext);

    const userRef = useRef<HTMLInputElement>();
    const errRef = useRef<HTMLParagraphElement>();

    const [username, setUsername] = useState('');
    const [userValid, setUserValid] = useState(false);
    const [userFocus, setUserFocus] = useState(false);

    const [password, setPassword] = useState('');
    const [passwordValid, setPasswordValid] = useState(false);
    const [passwordFocus, setPasswordFocus] = useState(false);

    const [errMsg, setErrMsg] = useState('');
    // temp until navigation is set up
    const [success, setSuccess] = useState(false);

    useEffect(() => {
        userRef?.current.focus();
    }, [])

    useEffect(() => {
        setUserValid(isValidEmail(username))
    }, [username])

    useEffect(() => {
        setPasswordValid(isValidPassword(password))
    }, [password])

    useEffect(() => {
        setErrMsg('');
    }, [username, password])

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();

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

            setUsername('');
            setPassword('');
            setSuccess(true);
        } catch (e) {
            if (!e?.response) {
                setErrMsg('No server response');
            } else if (e.response?.status === 409) {
                // missing username or password
                setErrMsg('Missing username or password.');
            } else if (e.response?.status === 401) {
                setErrMsg('Unauthorized');
            } else {
                setErrMsg('Login failed');
            }
            errRef?.current.focus();
            return;
        }
    }

    return (
        <>
            {success ? (
                <Navigate to="/gpt" />
            ) :(
                <section className="registration">
                    <p
                        ref={errRef} 
                        className={errMsg ? 'error': 'aria-hidden'}
                        aria-live="assertive">
                        {errMsg}
                    </p>
                    <h1>Sign in</h1>
                    <form onSubmit={handleSubmit}>
                    <label htmlFor="username">
                            Email:
                            <span className={userValid ? 'valid' : 'hidden'}><FontAwesomeIcon icon={faCheck} /></span>
                            <span className={userValid || !username ? 'hidden' : 'invalid'}><FontAwesomeIcon icon={faTimes} /></span>
                        </label>
                        <input
                            type="email"
                            id="username"
                            ref={userRef}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                            aria-invalid={userValid ? "false" : "true"}
                            aria-describedby="uidnote"
                            onFocus={() => setUserFocus(true)}
                            onBlur={() => setUserFocus(false)}
                        />
                        <p id="uidnote" className={userFocus && username && !userValid ? 'instructions'  : 'aria-hidden'}>
                            <FontAwesomeIcon icon={faInfoCircle} />
                            Please enter a valid email address.
                        </p>

                        <label htmlFor="password">
                            Password:
                            <span className={passwordValid ? 'valid' : 'hidden'}><FontAwesomeIcon icon={faCheck} /></span>
                            <span className={passwordValid || !password ? 'hidden' : 'invalid'}><FontAwesomeIcon icon={faTimes} /></span>
                        </label>
                        <input
                            type="password"
                            id="password"
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            aria-invalid={passwordValid ? "false" : "true"}
                            aria-describedby="pwdnote"
                            onFocus={() => setPasswordFocus(true)}
                            onBlur={() => setPasswordFocus(false)}
                        />
                        <p id="pwdnote" className={passwordFocus && !passwordValid ? 'instructions'  : 'aria-hidden'}>
                            <FontAwesomeIcon icon={faInfoCircle} />
                            8 to 24 characters.<br />
                            Must include uppercase and lowercase letters, a number, and at least one special character.<br />
                            Letters, numbers, underscores, hyphens allowed. <br />
                            Allowed special characters: <span aria-label="exclamation mark">!</span><span aria-label="at symbol">@</span><span aria-label="hash">#</span><span aria-label="dollar sign">$</span><span aria-label="percent">%</span>
                        </p>

                        <button disabled={!userValid || !passwordValid ? true : false}>Sign In</button>
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
