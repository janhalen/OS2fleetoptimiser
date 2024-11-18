import axios from 'axios';

const AxiosBase = axios.create({
    baseURL: `${process.env.NODE_ENV === 'development' ? 'http://localhost:3001/' : '/api/fleet/'}`,
});

export default AxiosBase;
