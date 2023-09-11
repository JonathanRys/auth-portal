import { useState, MouseEvent } from 'react';

import { faBars } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';

import { Outlet } from 'react-router-dom';

import ProtectedElement from '../util/ProtectedElement';

const Spacer = () => {
    return <div></div>
}

const Layout = () => {
    const [menuOpen, setMenuOpen] = useState(false);
    const menuClickHandler = (event: MouseEvent) => {
        event.stopPropagation();
        setMenuOpen(!menuOpen);
    };

    const clickHandler = () => {
        setMenuOpen(false);
    };

    return (
        <div id="background" onClick={clickHandler}>
            <header className="page-title">
                <ProtectedElement defaultElement={<Spacer/>}><div>{/* Spacer for flex layout */}</div></ProtectedElement>
                <div>Phys GPT</div>
                <ProtectedElement defaultElement={<Spacer/>}>
                    <div className="menu-container" onClick={menuClickHandler}>
                        <FontAwesomeIcon className="menu-icon" icon={faBars} />
                        <div className={menuOpen ? '' : 'hidden'} >
                            <div className="menu-background">
                                <ul className="menu-items">
                                    <a href="/update_password"><li>Change password</li></a>
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
        </div>
    )
}

export default Layout