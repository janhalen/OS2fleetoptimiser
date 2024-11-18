import { shift } from "@/components/hooks/useGetSettings";
import { getInterval } from "../ShiftNameTranslater";


// Helper function to extract the start time (in minutes from 00:00) from the shift string
const extractTimeInMinutes = (shift: string): number => {
    const timeRegex = /Fra (\d{2}):(\d{2})/;
    const match = shift.match(timeRegex);
    if (match) {
        const hours = parseInt(match[1], 10);
        const minutes = parseInt(match[2], 10);
        return hours * 60 + minutes; // Convert hours and minutes to total minutes
    }
    return 0;
};

// Helper function to assign a priority based on the shift type (Dag, Aften, Nat)
const getShiftPriority = (shift: string): number => {
    if (shift.startsWith('Dag')) return 1;
    if (shift.startsWith('Aften')) return 2;
    if (shift.startsWith('Nat')) return 3;
    return 4; // In case there's an unknown shift type
};

const shiftCompare = (a: string, b: string) => {
    const priorityA = getShiftPriority(a);
    const priorityB = getShiftPriority(b);

    // Primary sorting by shift type (Dag, Aften, Nat)
    if (priorityA !== priorityB) {
        return priorityA - priorityB;
    }

    // Secondary sorting by start time
    const timeA = extractTimeInMinutes(a);
    const timeB = extractTimeInMinutes(b);
    return timeA - timeB;
}


const createColorMap = (shiftNames: Array<string>, colors: Array<string>) => {
    // Convert the set to an array and return it
    const sortedKeys = shiftNames.sort(shiftCompare);

    // Map the sorted keys to an array of objects with their corresponding colors
    return sortedKeys.reduce((acc: Record<string, string>, key, index) => {
        acc[key] = colors[index % colors.length]; // Cycle through the colors array
        return acc;
    }, {});
}

type IdShift = (shift & { id: number });

const getColorMapperFunc = (availableShifts: Array<IdShift> | undefined) => {
    const colors = ['#6baed6', '#4292c6', '#2171b5', '#08519c', '#08306b'];


    // handle case with empty or length 1 available shifts

    if (!availableShifts || availableShifts.length <= 1) {
        return (shiftName: string) => { return colors[0] }
    }

    const shiftNames = availableShifts.map((shift) => getInterval(shift.shift_start, shift.shift_end))
    const colorMap = createColorMap(shiftNames, colors)

    return (shiftName: string) => { return colorMap[shiftName] }
}


export default getColorMapperFunc