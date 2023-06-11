import { Outlet } from 'react-router-dom';

const Layout = () => {
    return (
        <>
            <header className="page-title">Phys GPT</header>
            <main>
                <Outlet />
            </main>
        </>
    )
}

export default Layout