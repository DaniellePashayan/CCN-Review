import generate_dates as gd
from datetime import datetime
import pandas as pd

if __name__ == "__main__":
    GD=gd.DateGenerator(
        start_year=2026,
        end_year=2027,
        hol_list=[    
            datetime(2026, 1, 1),   # New Year's Day
            datetime(2026, 1, 19),  # Martin Luther King Jr. Day
            datetime(2026, 2, 16),  # Presidents' Day
            datetime(2026, 5, 25),  # Memorial Day
            datetime(2026, 7, 3),   # Independence Day (Observed)
            datetime(2026, 9, 7),   # Labor Day
            datetime(2026, 11, 26), # Thanksgiving Day
            datetime(2026, 12, 25), # Christmas Day
            datetime(2027, 1, 1)    # New Year's Day],
        ])
    df = GD.generate()
    df.to_csv("generated_dates.csv", index=False)
    print("Date generation complete. CSV file created: generated_dates.csv")
