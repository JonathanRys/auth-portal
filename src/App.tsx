import Registration from './components/Registration';
import Layout from './components/Layout';
import Login from './components/Login';
import Logout from './components/Logout';
import SetNewPassword from './components/SetNewPassword';
import ResetPassword from './components/ResetPassword';
import UpdatePassword from './components/UpdatePassword';
import ConfirmEmail from './components/ConfirmEmail'
import PhysGPT from './components/PhysGPT';
import Unauthorized from './components/Unauthorized';
import NotFound from './components/NotFound';
import './App.css';
import { getCookie } from './util/cookie';
import { Routes, Route, Navigate } from 'react-router-dom'
import { Props } from './types/types'
const user = getCookie('user');

const ProtectedRoute = ({ children }: Props) => {
  const user = getCookie('user');
  const role = getCookie('role');
  const authKey = getCookie('authKey');
  // Check authentication
  if (!(user && role && authKey)) {
    return <Navigate to="/" />;
  }
  // Check authorization
  if (!['viewer', 'editor', 'admin'].includes(role)) {
    return <Navigate to="/" />;
  }
  return <>{children}</>
}

function App() {
  return (
    <Routes>
      <Route path="/" element={ <Layout /> }>
        <Route path="*" element={ <NotFound /> } />
        <Route path="/" element={ user ? <Login /> : <Registration /> } />
        <Route path='login' element={ <Login /> } />
        <Route path='register' element={ <Registration /> } />
        <Route path='set_new_password' element={ <SetNewPassword /> } />
        <Route path='reset_password' element={ <ResetPassword /> } />
        <Route path='update_password' element={ <UpdatePassword /> } />
        <Route path='confirm_email' element={ <ConfirmEmail /> } />
        <Route path='logout' element={ <Logout /> } />
        <Route path='gpt' element={
          <ProtectedRoute>
            <PhysGPT />
          </ProtectedRoute> } />
        <Route path='unauthorized' element={ <Unauthorized /> } />
      </Route>
    </Routes>
  );
}

export default App;
