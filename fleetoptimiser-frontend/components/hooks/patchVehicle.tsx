import AxiosBase from '../AxiosBase';
import { Vehicle } from './useGetVehicles';

const patchVehicle = async (vehicle: Vehicle) => {
    const response = await AxiosBase.patch('configuration/vehicle', vehicle);
    return response.data;
};

export default patchVehicle;
