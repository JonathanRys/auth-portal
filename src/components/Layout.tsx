import { useState } from 'react';

import { faBars } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';

import { Outlet } from 'react-router-dom';

import ProtectedElement from '../util/ProtectedElement';

const Spacer = () => {
    return <div></div>
}

const Layout = () => {
    const [menuOpen, setMenuOpen] = useState(false);
    const menuClickHandler = () => {
        setMenuOpen(!menuOpen);
    };

    return (
        <>
            <header className="page-title">
                <ProtectedElement defaultElement={<Spacer/>}><div>{/* Spacer for flex layout */}</div></ProtectedElement>
                <div>Phys GPT</div>
                <ProtectedElement defaultElement={<Spacer/>}>
                    <div className="menu-container">
                        <FontAwesomeIcon className="menu-icon" onClick={menuClickHandler} icon={faBars} />
                        <div className={menuOpen ? '' : 'hidden'} >
                            <div className="menu-background">
                                <ul className="menu-items">
                                    <a href="/update_password"><li>Change password</li></a>
                                    <hr/>
                                    <a href="/logout"><li>Logout</li></a>
                                </ul>
                            </div>
                        </div>
                    </div>
                </ProtectedElement>
            </header>
            <main>
                <Outlet />
            </main>
        </>
    )
}

export default Layout