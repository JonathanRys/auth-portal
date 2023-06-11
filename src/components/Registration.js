import { useState, useEffect, useRef, useContext } from 'react';
import { faCheck, faTimes, faInfoCircle } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';

import { setCookie } from '../util/cookie';
import AuthContext from '../context/AuthProvider';
import axios from '../api/axios';

const EMAIL_REGEX = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
const PW_REGEX = /^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%]).{8,24}$/;
const REGISTER_URL = '/register';

const Registration = () => {
    const { setAuth } = useContext(AuthContext);

    const userRef = useRef();
    const errRef = useRef();

    const [user, setUser] = useState('');
    const [userValid, setUserValid] = useState(false);
    const [userFocus, setUserFocus] = useState(false);

    const [password, setPassword] = useState('');
    const [passwordValid, setPasswordValid] = useState(false);
    const [passwordFocus, setPasswordFocus] = useState(false);

    const [pwMatch, setPwMatch] = useState('');
    const [matchValid, setMatchValid] = useState(false);
    const [matchFocus, setMatchFocus] = useState(false);

    const [errMsg, setErrMsg] = useState('');
    const [success, setSuccess] = useState();

    useEffect(() => {
        userRef.current.focus();
    }, [])

    useEffect(() => {
        setUserValid(EMAIL_REGEX.test(user))
    }, [user])

    useEffect(() => {
        setPasswordValid(PW_REGEX.test(password))
        setMatchValid(password === pwMatch)
    }, [password, pwMatch])

    useEffect(() => setErrMsg(''), [user, password, pwMatch])

    const handleSubmit = async (e) => {
        e.preventDefault();
        switch (true) {
        case !userValid:
        case !EMAIL_REGEX.test(user):
            setErrMsg('Invalid username.');
            return;
        case !passwordValid:
        case !PW_REGEX.test(password):
            setErrMsg('Invalid password.');
            return;
        case !matchValid:
            setErrMsg('Passwords don\'t match.');
            return;
        default:
            try{
                const response = await axios.post(REGISTER_URL, 
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

                const accessToken = response?.data?.accessToken;
                const roles = response?.data?.roles;

                setAuth({ user, password, roles, accessToken });
                setCookie('user', user);
                setCookie('roles', roles);
                setCookie('accessToken', accessToken);
                
                setSuccess(true);
                // clear inputs
                setUser('');
                setPassword('');
                setPwMatch('');
                return;
                    
            } catch (e) {
                if (!e?.response) {
                    setErrMsg('No response from server.')
                } else if (e.response?.status === 409) {
                    setErrMsg('Username already taken.');
                } else if (e.response?.status >= 500) {
                    setErrMsg('Server error.')
                } else {
                    setErrMsg('Registration Failed.')
                }
                errRef.current.focus();
                return;
            }
        }
    }

    return (
            <>
                {success ? (
                    <section>
                        <p>
                            <a href='/gpt'>Enter</a>
                        </p>
                    </section>
                ) : (<section>
                    <p ref={errRef} className={errMsg ? 'error' : 'aria-hidden'} aria-live="assertive">{errMsg}</p>
                    <h1>Register</h1>
                    <form onSubmit={handleSubmit}>
                        <label htmlFor="username">
                            Email:
                            <span className={userValid ? 'valid' : 'hidden'}><FontAwesomeIcon icon={faCheck} /></span>
                            <span className={userValid || !user ? 'hidden' : 'invalid'}><FontAwesomeIcon icon={faTimes} /></span>
                        </label>
                        <input
                            type="email"
                            id="username"
                            ref={userRef}
                            onChange={(e) => setUser(e.target.value)}
                            required
                            aria-invalid={userValid ? "false" : "true"}
                            aria-describedby="uidnote"
                            onFocus={() => setUserFocus(true)}
                            onBlur={() => setUserFocus(false)}
                        />
                        <p id="uidnote" className={userFocus && user && !userValid ? 'instructions'  : 'aria-hidden'}>
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
                            <span className={matchValid && pwMatch ? 'valid' : 'hidden'}><FontAwesomeIcon icon={faCheck} /></span>
                            <span className={matchValid || !pwMatch ? 'hidden' : 'invalid'}><FontAwesomeIcon icon={faTimes} /></span>
                        </label>
                        <input
                            type="password"
                            id="confirm-password"
                            onChange={(e) => setPwMatch(e.target.value)}
                            required
                            aria-invalid={matchValid ? "false" : "true"}
                            aria-describedby="confirmnote"
                            onFocus={() => setMatchFocus(true)}
                            onBlur={() => setMatchFocus(false)}
                        />
                        <p id="confirmnote" className={matchFocus && !matchValid ? 'instructions'  : 'aria-hidden'}>
                            <FontAwesomeIcon icon={faInfoCircle} />
                            Must match the password input field.
                        </p>
                        <button disabled={!userValid || !passwordValid || !matchValid ? true : false} >Sign Up</button>
                    </form>
                    <p>
                        Already registered?<br />
                        <span className="inline">
                            <a href="/login">Sign In</a>
                        </span>
                    </p>
                </section>
            )}
        </>
    )
}

export default Registration;
