type TimeEntry = {
    start_time: Date;
    end_time: Date;
};

export default function alternate(row: TimeEntry, ssh: Date = new Date(0, 0, 1, 7), seh: Date = new Date(0, 0, 1, 15)): number {
    const start_time = new Date(0, 0, 1, row.start_time.getHours(), row.start_time.getMinutes(), row.start_time.getSeconds());
    const end_time = new Date(0, 0, 1, row.end_time.getHours(), row.end_time.getMinutes(), row.end_time.getSeconds());

    const ss = new Date(0, 0, 1, ssh.getHours(), ssh.getMinutes(), ssh.getSeconds());
    const se = new Date(0, 0, 1, seh.getHours(), seh.getMinutes(), seh.getSeconds());

    const zero = 0;
    const aday = 24 * 60 * 60 * 1000;

    let time = 0;

    if (start_time > end_time) {
        // The route runs over midnight
        if (ss > se) {
            // The shift runs over midnight
            if (start_time <= ss && end_time >= se) {
                time = se.getTime() + aday - ss.getTime();
            } else if (start_time <= ss && end_time <= se) {
                time = end_time.getTime() + aday - ss.getTime();
            } else if (start_time >= ss && end_time <= se) {
                time = end_time.getTime() - start_time.getTime();
            } else if (start_time >= ss && end_time >= se) {
                time = se.getTime() + aday - start_time.getTime();
            }
        } else {
            // The shift doesn't run over midnight
            let tran_s = start_time.getTime();
            let tran_e = end_time.getTime() + aday;
            const alt_ss = ss.getTime();
            const alt_es = se.getTime();

            if (alt_es < tran_s) {
                tran_s += aday;
                tran_e += aday;
            }
            if (tran_s >= alt_ss && tran_e >= alt_es) {
                time = alt_es - tran_s;
            } else if (tran_s >= alt_ss && tran_e <= alt_es) {
                time = tran_e - tran_s;
            } else if (tran_s <= alt_ss && tran_e <= alt_es) {
                time = tran_e - alt_ss;
            } else if (tran_s <= alt_ss && tran_e >= alt_es) {
                time = alt_es - alt_ss;
            }
        }
    } else {
        // The route doesn't run over midnight
        if (ss > se) {
            // The shift runs over midnight
            const alt_ss = ss.getTime();
            const alt_es = se.getTime() + aday;
            let tran_s = start_time.getTime();
            let tran_e = end_time.getTime();

            if (tran_e < alt_ss) {
                tran_s += aday;
                tran_e += aday;
            }

            if (tran_s <= alt_ss && tran_e <= alt_es) {
                time = tran_e - alt_ss;
            } else if (tran_s <= alt_ss && tran_e >= alt_es) {
                time = alt_es - alt_ss;
            } else if (tran_s >= alt_ss && tran_e >= alt_es) {
                time = alt_es - tran_s;
            } else if (tran_s >= alt_ss && tran_e <= alt_es) {
                time = tran_e - tran_s;
            }
        } else {
            const start = start_time.getTime();
            const end = end_time.getTime();
            const alt_ss = ss.getTime();
            const alt_es = se.getTime();

            if (start >= alt_ss && end <= alt_es) {
                time = end - start;
            } else if (start >= alt_ss && end >= alt_es) {
                time = alt_es - start;
            } else if (start <= alt_ss && end >= alt_es) {
                time = alt_es - alt_ss;
            } else if (start <= alt_ss && end <= alt_es) {
                time = end - alt_ss;
            }
        }
    }

    if (time < zero) {
        time = zero;
    }
    return time / 1000;
}

export function calculateShiftDuration(start_shift: string, end_shift: string): number {
    const [startHours, startMinutes] = start_shift.split(':').map(Number);
    const [endHours, endMinutes] = end_shift.split(':').map(Number);

    const startDate = new Date();
    startDate.setHours(startHours, startMinutes, 0, 0);

    const endDate = new Date();
    endDate.setHours(endHours, endMinutes, 0, 0);

    if (endDate <= startDate) {
        endDate.setDate(endDate.getDate() + 1);
    }

    return (endDate.getTime() - startDate.getTime()) / 1000;
}

export function splitDayShiftDurations(start_shift: string, end_shift: string): [number, number] {
    const [startHours, startMinutes] = start_shift.split(':').map(Number);
    const [endHours, endMinutes] = end_shift.split(':').map(Number);

    const startDate = new Date();
    startDate.setHours(startHours, startMinutes, 0, 0);

    const endDate = new Date();
    endDate.setHours(endHours, endMinutes, 0, 0);

    const firstDayEnd = new Date(startDate);
    firstDayEnd.setHours(23, 59, 59, 999);

    let firstDayDuration = 0;
    let secondDayDuration = 0;

    if (endDate <= startDate) {
        firstDayDuration = (firstDayEnd.getTime() - startDate.getTime() + 1) / 1000;
        secondDayDuration = (endDate.getTime() - new Date(endDate.setHours(0, 0, 0, 0)).getTime()) / 1000;
    } else {
        firstDayDuration = (endDate.getTime() - startDate.getTime()) / 1000;
    }
    if (!firstDayDuration) {
        firstDayDuration = 0;
    }
    if (!secondDayDuration) {
        secondDayDuration = 0;
    }
    return [firstDayDuration, secondDayDuration];
}

export function getDatesBetween(startDate: string, endDate: string): string[] {
    const start = new Date(startDate);
    const end = new Date(endDate);
    const dates: string[] = [];

    for (let date = new Date(start); date <= end; date.setDate(date.getDate() + 1)) {
        dates.push(date.toLocaleDateString('da-DK'));
    }

    return dates;
}
