import AxiosBase from '../AxiosBase';
import { settings } from '../hooks/useGetSettings';

export async function getSettings() {
    const response = await AxiosBase.get<settings>('configuration/simulation-configurations');
    return response.data;
}
