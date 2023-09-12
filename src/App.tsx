import './App.css';
import Registration from './components/Registration';
import Layout from './components/Layout';
import Login from './components/Login';
import Logout from './components/Logout';
import SetNewPassword from './components/SetNewPassword';
import ResetPassword from './components/ResetPassword';
import UpdatePassword from './components/UpdatePassword';
import ConfirmEmail from './components/ConfirmEmail'
import PhysGPT from './app/PhysGPT';
import Unauthorized from './components/Unauthorized';
import NotFound from './components/NotFound';
import ProtectedRoute from './util/ProtectedRoute';
import { getCookie } from './util/cookie';
import { Routes, Route } from 'react-router-dom'
const username = getCookie('username');

function App() {
  return (
    <Routes>
      <Route path="/" element={ <Layout /> }>
        <Route path="*" element={ <NotFound /> } />
        <Route path="/" element={ username ? <Login /> : <Registration /> } />
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
