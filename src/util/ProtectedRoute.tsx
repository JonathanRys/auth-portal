import { Navigate } from 'react-router-dom'
import { getCookie } from '../util/cookie';
import { Props } from '../types/types'

const ProtectedRoute = ({ children }: Props) => {
    const _username = getCookie('username');
    const role = getCookie('role');
    const authKey = getCookie('authKey');
    const sessionKey = getCookie('sessionKey');
    // Check authentication
    if (!(_username && role && authKey && sessionKey)) {
      return <Navigate to="/" />;
    } else {
      // validate against server
      console.log('authentication success:', _username, role)
    }
    // Check authorization
    if (!['viewer', 'editor', 'admin'].includes(role)) {
      return <Navigate to="/" />;
    }
    return <>{children}</>
}

export default ProtectedRoute
