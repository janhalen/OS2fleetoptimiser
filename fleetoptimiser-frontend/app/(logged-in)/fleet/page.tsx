'use client';

import { Inter } from 'next/font/google';
import FleetSimulation from './FleetSimulation';

const inter = Inter({ subsets: ['latin'] });

export default function Page() {
    return <FleetSimulation></FleetSimulation>;
}
