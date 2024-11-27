'use client';

import ApiError from '@/components/ApiError';
import useGetStatisticsOverview from '@/components/hooks/useGetStatisticsOverview';
import { CircularProgress } from '@mui/material';
import dayjs from 'dayjs';
import React from 'react';
import DateLineGraph from './DateLineGraph';

type Props = {
    startDate?: string;
    endDate?: string;
    locations?: number[];
    forvaltninger?: string[];
};

export default function OverViewGraphs({ endDate, forvaltninger, locations, startDate }: Props) {
    const emissionSeries = useGetStatisticsOverview({
        startPeriod: startDate ? dayjs(startDate) : dayjs().add(-7, 'day'),
        endPeriod: endDate ? dayjs(endDate) : dayjs(),
        dashboard: 'emission',
        locationIds: locations,
        forvaltninger: forvaltninger,
        selector: (data) => {
            return {
                ...data,
                id: 'emission',
            };
        },
    });

    const shareSeries = useGetStatisticsOverview({
        startPeriod: startDate ? dayjs(startDate) : dayjs().add(-7, 'day'),
        endPeriod: endDate ? dayjs(endDate) : dayjs(),
        dashboard: 'share',
        locationIds: locations,
        forvaltninger: forvaltninger,
        selector: (data) => {
            return {
                ...data,
                id: 'share',
            };
        },
    });
    const drivenSeries = useGetStatisticsOverview({
        startPeriod: startDate ? dayjs(startDate) : dayjs().add(-7, 'day'),
        endPeriod: endDate ? dayjs(endDate) : dayjs(),
        dashboard: 'driven',
        locationIds: locations,
        forvaltninger: forvaltninger,
        selector: (data) => {
            return {
                ...data,
                id: 'driven',
            };
        },
    });

    return (
        <>
            <div className="bg-white custom-nav mb-8 p-8 text-center">
                <h2 className="text-lg font-semibold">CO2e udledning (Ton)</h2>
                {emissionSeries.isError && <ApiError retryFunction={emissionSeries.refetch}>Dashboard data kunne ikke hentes</ApiError>}
                {emissionSeries.isLoading && (
                    <div className="p-10 flex justify-center">
                        <CircularProgress />
                    </div>
                )}
                {emissionSeries.data &&
                    (emissionSeries.data.data.length > 0 ? (
                        <div className="h-96">
                            <DateLineGraph data={[emissionSeries.data]} yLabel={'Ton CO2e udledning'} color={'#f47560'}></DateLineGraph>
                        </div>
                    ) : (
                        <p className="m-4">Der er ingen kørselsdata for de valgte filtre.</p>
                    ))}
            </div>
            <div className="bg-white drop-shadow-md mb-4 p-4 text-center">
                <h2 className="text-lg font-semibold">Procentvis kørt i elbil</h2>
                {shareSeries.isError && <ApiError retryFunction={shareSeries.refetch}>Dashboard data kunne ikke hentes</ApiError>}
                {shareSeries.isLoading && (
                    <div className="p-10 flex justify-center">
                        <CircularProgress />
                    </div>
                )}
                {shareSeries.data &&
                    (shareSeries.data.data.length > 0 ? (
                        <div className="h-96">
                            <DateLineGraph data={[shareSeries.data]} yLabel={'Procentvis kørt i elbil'} color={'#2171b5'}></DateLineGraph>
                        </div>
                    ) : (
                        <p className="m-4">Der er ingen kørselsdata for de valgte filtre.</p>
                    ))}
            </div>
            <div className="bg-white drop-shadow-md mb-4 p-4 text-center">
                <h2 className="text-lg font-semibold">Kørte kilometer</h2>
                {drivenSeries.isError && <ApiError retryFunction={drivenSeries.refetch}>Dashboard data kunne ikke hentes</ApiError>}
                {drivenSeries.isLoading && (
                    <div className="p-10 flex justify-center">
                        <CircularProgress />
                    </div>
                )}
                {drivenSeries.data &&
                    (drivenSeries.data.data.length > 0 ? (
                        <div className="h-96">
                            <DateLineGraph data={[drivenSeries.data]} yLabel={'Kørte kilometer'} color={'#61cdbb'}></DateLineGraph>
                        </div>
                    ) : (
                        <p className="m-4">Der er ingen kørselsdata for de valgte filtre.</p>
                    ))}
            </div>
        </>
    );
}
