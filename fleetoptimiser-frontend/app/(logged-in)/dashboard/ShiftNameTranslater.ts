export function getInterval(startTimestamp: string, endTimestamp: string): string {
    const [startHour, startMinute, startSecond] = startTimestamp.split(':').map((s) => parseInt(s));
    const [endHour, endMinute, endSecond] = endTimestamp.split(':').map((s) => parseInt(s));

    const startTotalSeconds = startHour * 3600 + startMinute * 60 + startSecond;
    const endTotalSeconds = endHour * 3600 + endMinute * 60 + endSecond;
    let totalSeconds = endTotalSeconds - startTotalSeconds;
    if (totalSeconds < 0) {
        totalSeconds += 24 * 3600;
    }

    const intervals: { [key: string]: number } = {
        'Nat vagt': 0,
        'Dag vagt': 0,
        'Aften vagt': 0,
    };

    let currentTotalSeconds = startTotalSeconds;
    while (totalSeconds > 0) {
        const hour = Math.floor(currentTotalSeconds / 3600);
        if (hour >= 23 || hour < 7) {
            intervals['Nat vagt']++;
        } else if (hour >= 7 && hour < 17) {
            intervals['Dag vagt']++;
        } else if (hour >= 17 && hour < 23) {
            intervals['Aften vagt']++;
        }
        currentTotalSeconds = (currentTotalSeconds + 3600) % (24 * 3600);
        totalSeconds -= 3600;
    }

    let maxInterval: string = '';
    let maxCount: number = 0;
    for (const [interval, count] of Object.entries(intervals)) {
        if (count > maxCount) {
            maxInterval = interval;
            maxCount = count;
        }
    }
    return `${maxInterval}. Fra ${startTimestamp.slice(0, 5)} til ${endTimestamp.slice(0, 5)}`;
}
