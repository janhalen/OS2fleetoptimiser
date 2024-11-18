import pandas as pd


def get_emission(entry):
    if any(
        [
            (entry.wltp_fossil == 0 and entry.wltp_el == 0),
            (pd.isna(entry.wltp_fossil) and pd.isna(entry.wltp_el)),
        ]
    ):
        return "0"

    udledning = (
        f"{str(round(entry.wltp_el)).replace('.', ',')} Wh/km"
        if pd.isna(entry.wltp_fossil) or entry.wltp_fossil == 0
        else f"{str(round(entry.wltp_fossil, 1)).replace('.', '.')} km/l"
    )
    return udledning
