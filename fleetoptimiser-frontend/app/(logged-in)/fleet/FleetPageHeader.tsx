export default function FleetPageHeader() {
    return (
        <div className="bg-white p-4 mx-2 mb-4 drop-shadow-md">
            <h1 className="border-b mb-2 pb-2 font-semibold">Manuel simulering</h1>
            <p>
                På denne side kan man som bruger undersøge hvilken indflydelse det har, at tilføje eller fjerne køretøjer til den samlede flåde. Disse ændringer
                kommer til at påvirke de estimerede årlige omkostninger, det estimerede årlige CO2e forbrug, samt hvor mange ture der ikke bliver allokeret.
            </p>
        </div>
    );
}
