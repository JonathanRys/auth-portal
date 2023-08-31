import Registration from './components/Registration';
import Layout from './components/Layout';
import Login from './components/Login';
import PhysGPT from './components/PhysGPT';
import Unauthorized from './components/Unauthorized';
import NotFound from './components/NotFound';
import './App.css';
import { getCookie } from './util/cookie';
import { Routes, Route, Navigate } from 'react-router-dom'

const user = getCookie('user') ;

const ProtectedRoute = ({ children }) => {
  const user = getCookie('user') ;
  if (!user) {
    return <Navigate to="/" />;
  }
  return children
}

function App() {
  return (
    <Routes>
      <Route path="/" element={ <Layout /> }>
        <Route path="*" element={ <NotFound /> } />
        <Route path="/" element={ user ? <Login /> : <Registration /> } />
        <Route path='login' element={ <Login /> } />
        <Route path='register' element={ <Registration /> } />
        <Route path='gpt' element={ <ProtectedRoute><PhysGPT /></ProtectedRoute> } />
        <Route path='unauthorized' element={ <Unauthorized /> } />
      </Route>
    </Routes>
  );
}

export default App;
