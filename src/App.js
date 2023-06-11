import Registration from './components/Registration';
import Layout from './components/Layout';
import Login from './components/Login';
import PhysGPT from './components/PhysGPT';
import Unauthorized from './components/Unauthorized'
import './App.css';
import { getCookie } from './util/cookie';
import { Routes, Route } from 'react-router-dom'

const user = getCookie('user') ;

function App() {
  return (
    <Routes>
      <Route path="/" element={ <Layout /> }>
        <Route path="/" element={ user ? <Login /> : <Registration /> } />
        <Route path='login' element={ <Login /> } />
        <Route path='register' element={ <Registration /> } />
        <Route path='gpt' element={ <PhysGPT /> } />
        <Route path='unauthorized' element={ <Unauthorized /> } />
      </Route>
    </Routes>
  );
}

export default App;
