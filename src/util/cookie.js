export const getCookie = (cookie) => {
    const value = document.cookie.split('; ').find(c => c.startsWith(`${cookie}=`))?.split('=')[1]
    if (!value) {
        return localStorage.getItem(cookie)
    }
    return value
}
  
export const setCookie = (key, value) => {
    localStorage.setItem(key, value);
    const cookies = document.cookie.split('; ');
    cookies.push(`${key}=${value}`);
    document.cookie = cookies.join('; ');
    return document.cookie;
}
