export const errorArray = [
    { id: 0, message: 'WLTP-typen er ikke korrekt udfyldt.' },
    { id: 1, message: 'Ukendt fejl.' },
    { id: 2, message: 'Der er ikke angivet nogen drivmiddeltype.' },
    {
        id: 3,
        message: 'Drivmiddeltypen stemmer ikke overens med den valgte køretøjstype.',
    },
    {
        id: 4,
        message: 'Drivmiddeltypen for den valgte type må ikke indeholde "WLTP_fossil" eller "WLTP_el".',
    },
    { id: 5, message: 'Den valgte drivmiddeltype eksisterer ikke.' },
    { id: 6, message: 'Køretøjstypen eksisterer ikke.' },
    { id: 7, message: 'Leasingtypen eksisterer ikke.' },
    { id: 8, message: 'Lokationen eksisterer ikke.' },
];
export function matchErrors(inputArray: any[]): string[] {
    const errorMessages: string[] = [];
    inputArray.forEach((input: { msg: any }) => {
        const firstDigit = input.msg.match(/^\d+/)?.[0]; // use match() to find the first digit, and optional chaining to handle null/undefined
        if (firstDigit) {
            // check if the firstDigit exists
            const matchedError = errorArray.find((error) => error.id.toString() === firstDigit);
            if (matchedError) {
                errorMessages.push(matchedError.message);
            }
        }
    });

    return errorMessages;
}
