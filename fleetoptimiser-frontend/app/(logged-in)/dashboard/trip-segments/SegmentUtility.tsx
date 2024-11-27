interface Segment {
    start_time: string;
    end_time: string;
    distance: number;
}

interface ParkingSegment {
    name: string;
    start_time: string;
    end_time: string;
    parking_time: string;
    accumulated_distance: number;
    distance: number;
}

interface DrivingSegment {
    name: string;
    start_time: string;
    end_time: string;
    driving_time: string;
    accumulated_distance: number;
    distance: number;
}

interface AccumulatedDriving {
    time: string;
    accumulated_distance: number;
}

export function minutesDifference(time1: string, time2: string): number {
    let t1 = new Date(time1);
    let t2 = new Date(time2);
    let delta = (t2.getTime() - t1.getTime()) / 1000;
    return Math.round(delta / 60);
}

export function formatTimeFromISO(isoString: string) {
    const timePart = isoString.split('T')[1].split('.')[0]; // Extracting HH:MM:SS from ISO string
    return timePart;
}

export function generateParkingSegments(segments: Segment[]): ParkingSegment[] {
    let parkingSegments: ParkingSegment[] = [];
    let accumulated_distance = 0;
    for (let i = 0; i < segments.length - 1; i++) {
        accumulated_distance += segments[i].distance;
        parkingSegments.push({
            name: `Parkering ${i + 1}`,
            start_time: segments[i].end_time,
            end_time: segments[i + 1].start_time,
            parking_time: `${minutesDifference(segments[i].end_time, segments[i + 1].start_time)} minutter`,
            accumulated_distance: accumulated_distance,
            distance: 0,
        });
    }
    return parkingSegments;
}

export function generateDrivingSegments(segments: Segment[]): DrivingSegment[] {
    let drivingSegments: DrivingSegment[] = [];
    let accumulated_distance = 0;
    let index = 1;
    for (let segment of segments) {
        accumulated_distance += segment.distance;
        drivingSegments.push({
            name: `Kørsel ${index}`,
            start_time: segment.start_time,
            end_time: segment.end_time,
            driving_time: `${minutesDifference(segment.start_time, segment.end_time)} minutter`,
            accumulated_distance: accumulated_distance,
            distance: segment.distance,
        });
        index += 1;
    }
    return drivingSegments;
}

export function generateAccumulatedDriving(segments: Segment[]): AccumulatedDriving[] {
    let accumulatedDriving: AccumulatedDriving[] = [];
    let accumulated_distance = 0;
    for (let segment of segments) {
        accumulatedDriving.push({
            time: segment.start_time,
            accumulated_distance: accumulated_distance,
        });
        accumulated_distance += segment.distance;
        accumulatedDriving.push({
            time: segment.end_time,
            accumulated_distance: accumulated_distance,
        });
    }
    return accumulatedDriving;
}
