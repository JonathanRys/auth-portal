import { useState, useEffect, useRef, FormEvent } from 'react';
import { faCheck, faTimes, faInfoCircle } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';

import { setCookie } from '../util/cookie';
import { isValidEmail } from '../util/validations';
import axios from '../api/axios';

const RESET_PW_URL = '/reset_password';

const ResetPassword = () => {
    const userRef = useRef<HTMLInputElement>();
    const errRef = useRef<HTMLParagraphElement>();

    const [username, setUsername] = useState('');
    const [userValid, setUserValid] = useState(false);
    const [userFocus, setUserFocus] = useState(false);

    const [errMsg, setErrMsg] = useState('');
    // temp until navigation is set up
    const [success, setSuccess] = useState(false);

    useEffect(() => {
        userRef.current.focus();
    }, [])

    useEffect(() => {
        setUserValid(isValidEmail(username))
    }, [username])

    useEffect(() => setErrMsg(''), [username])

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        switch (true) {
            case !userValid:
            case !isValidEmail(username):
                setErrMsg('Invalid username.');
                return;
            default:
                try {
                    const response = await axios.post(RESET_PW_URL, 
                        {
                            "username": username
                        }, {
                            withCredentials: true
                        }
                    );

                    if (response?.status !== 200) {
                        throw new Error(`Request failed with status ${response?.status}`);
                    }

                    setCookie('username', username);
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
    }

    return (
        <>
            {success ? (
                <section className="registration">
                    <h1>Password reset email sent</h1>
                    <p>Please check your email for a reset link.</p>
                </section>
            ) :(
                <section className="registration">
                    <p
                        ref={errRef} 
                        className={errMsg ? 'error': 'aria-hidden'}
                        aria-live="assertive">
                        {errMsg}
                    </p>
                    <h1>Reset Password</h1>
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
                        <button disabled={!username}>Reset password</button>
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
