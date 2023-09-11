import { getCookie } from '../util/cookie';
import { Props } from '../types/types'

const ProtectedElement = (props: Props) => {
    const _username = getCookie('username');
    const role = getCookie('role');
    const authKey = getCookie('authKey');
    const sessionKey = getCookie('sessionKey');
    // Check authentication
    if (!(_username && role && authKey && sessionKey)) {
      return <>props.defaultElement</> || null;
    } else {
      // validate against server
    //   console.log('authentication success:', _username, role)
    }
    // Check authorization
    if (!['viewer', 'editor', 'admin'].includes(role)) {
      return <>props.defaultElement</> || null;
    }
    return <>{props.children}</>
}

export default ProtectedElement;
