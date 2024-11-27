import { Inter } from 'next/font/google';
import GoalSimulation from './GoalSimulation';

const inter = Inter({ subsets: ['latin'] });

export default function Page() {
    return <GoalSimulation></GoalSimulation>;
}
