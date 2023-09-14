import { useContext } from 'react';
import { getCookie } from '../util/cookie';
import { Props } from '../types/types'
import AuthContext from '../context/AuthProvider';

const ProtectedElement = (props: Props) => {
  // @ts-ignore
    const { auth } = useContext(AuthContext);
    console.log('auth:', auth)

    const _username = auth.username || getCookie('username');
    const role = auth.role || getCookie('role');
    const authKey = auth.authKey || getCookie('authKey');
    const sessionKey = auth.sessionKey || ('sessionKey');

    // Check authentication
    if (!(_username && role && authKey && sessionKey)) {
      return <>{props.defaultElement}</> || null;
    } else {
      // validate against server
    }
    // Check authorization
    if (!['viewer', 'editor', 'admin'].includes(role)) {
      return <>{props.defaultElement}</> || null;
    }

    if (props.children) {
        return <>{props.children}</>
    }
    return <>{props.defaultElement}</>
}

export default ProtectedElement;
