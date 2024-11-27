import { useQuery } from '@tanstack/react-query';
import AxiosBase from '../AxiosBase';
import { goalSimulation } from './useSimulateGoal';

export const useGetGoalSimulation = (simulationId: string) => {
    return useQuery(['goal result', simulationId], () => AxiosBase.get<goalSimulation>(`/goal-simulation/simulation/${simulationId}`).then((res) => res.data));
};
