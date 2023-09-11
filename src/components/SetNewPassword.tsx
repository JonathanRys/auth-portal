import { useState, useEffect, useRef, useContext, FormEvent } from 'react';
import { faCheck, faTimes, faInfoCircle } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';

import { setCookie } from '../util/cookie';
import { isValidEmail, isValidPassword } from '../util/validations';
import AuthContext from '../context/AuthProvider';
import axios from '../api/axios';

import { Navigate, useLocation } from 'react-router-dom';

const SET_NEW_PASSWORD_URL = '/set_new_password';

const SetNewPassword = () => {
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

    const [confirmPassword, setConfirmPassword] = useState('');
    const [matchValid, setMatchValid] = useState(false);
    const [confirmPasswordFocus, setConfirmPasswordFocus] = useState(false);

    const [errMsg, setErrMsg] = useState('');
    // temp until navigation is set up
    const [success, setSuccess] = useState(false);
    const search = useLocation().search;

    useEffect(() => {
        userRef.current.focus();
    }, [])

    useEffect(() => {
        setUserValid(isValidEmail(username))
    }, [username])

    useEffect(() => {
        setPasswordValid(isValidPassword(password))
        setMatchValid(password === confirmPassword)
    }, [password, confirmPassword])

    useEffect(() => setErrMsg(''), [username, password, confirmPassword])

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        switch (true) {
            case !userValid:
            case !isValidEmail(username):
                setErrMsg('Invalid username.');
                return;
            case !passwordValid:
            case !isValidPassword(password):
                setErrMsg('Invalid password.');
                return;
            case !matchValid:
                setErrMsg('Passwords don\'t match.');
                return;
            default:
                const accessKey = new URLSearchParams(search).get('accessKey');

                try {
                    const response = await axios.post(SET_NEW_PASSWORD_URL, 
                        JSON.stringify({
                            username, accessKey, password
                        }), {
                            headers: { 'Content-Type': 'application/json' },
                            withCredentials: true
                        }
                    );

                    if (response?.status !== 200) {
                        throw new Error(`Request failed with status ${response?.status}`);
                    }

                    const authKey = response?.data?.authKey;
                    const sessionKey = response?.data?.sessionKey;
                    const roles = response?.data?.roles;

                    setAuth({ username, roles, sessionKey, authKey })
                    setCookie('username', username);
                    setCookie('roles', roles);
                    if (authKey) {
                        setCookie('authKey', authKey);
                    }
                    if (sessionKey) {
                        setCookie('sessionKey', sessionKey);
                    }

                    setUsername('');
                    setPassword('');
                    setConfirmPassword('');
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
                        setErrMsg('Password reset failed.')
                    }
                    errRef.current.focus();
                }
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
                    <h1>Change password</h1>
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

                        <label htmlFor="confirm-password">
                            Confirm Password:
                            <span className={matchValid && confirmPassword && passwordValid ? 'valid' : 'hidden'}><FontAwesomeIcon icon={faCheck} /></span>
                            <span className={matchValid || !confirmPassword ? 'hidden' : 'invalid'}><FontAwesomeIcon icon={faTimes} /></span>
                        </label>
                        <input
                            type="password"
                            id="confirm-password"
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            required
                            aria-invalid={matchValid ? "false" : "true"}
                            aria-describedby="confirmnote"
                            onFocus={() => setConfirmPasswordFocus(true)}
                            onBlur={() => setConfirmPasswordFocus(false)}
                        />
                        <p id="confirmnote" className={confirmPasswordFocus && !matchValid ? 'instructions'  : 'aria-hidden'}>
                            <FontAwesomeIcon icon={faInfoCircle} />
                            Must match the password input field.
                        </p>

                        <button disabled={!username || !password || !confirmPassword ? true : false}>Set New Password</button>
                        <p>
                            Found your password?<br />
                            <span className="inline">
                                <a href="/login">Sign In</a>
                            </span>
                        </p>
                    </form>
                </section>
            )}
        </>
    )
}

export default SetNewPassword
