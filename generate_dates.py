
from datetime import datetime, timedelta
import pandas as pd

class DateGenerator:
    def __init__(self, start_year=2026, end_year=2027, hol_list=None):
        self.start_date = datetime(start_year, 1, 1)
        self.end_date = datetime(end_year, 1, 31)
        self.date_list = []
        self.date_list_str = []
        self.date_df = pd.DataFrame()
        self.last_day_of_months = []
        self.hol_list = hol_list if hol_list is not None else [
            datetime(2026, 1, 1),   # New Year's Day
            datetime(2026, 1, 19),  # Martin Luther King Jr. Day
            datetime(2026, 2, 16),  # Presidents' Day
            datetime(2026, 5, 25),  # Memorial Day
            datetime(2026, 7, 3),   # Independence Day (Observed)
            datetime(2026, 9, 7),   # Labor Day
            datetime(2026, 11, 26), # Thanksgiving Day
            datetime(2026, 12, 25), # Christmas Day
            datetime(2027, 1, 1)    # New Year's Day
        ]

    def generate_dates(self):
        current_date = self.start_date
        while current_date <= self.end_date:
            self.date_list.append(current_date) 
            self.date_list_str.append(current_date.strftime("%m/%d/%Y")) 
            current_date += timedelta(days=1)

        self.date_df = pd.DataFrame(self.date_list, columns=['DateTime'])
        self.date_df['Date'] = self.date_list_str

        # Debug prints
        print(self.start_date)
        print(self.end_date)

    def add_day_of_week(self):
        self.date_df['Day_of_Week'] = self.date_df['DateTime'].apply(lambda x: x.strftime('%A'))
        self.date_df['Day_of_Week_Index'] = self.date_df['DateTime'].dt.weekday

    def check_weekday(self, date):
        day_of_week = date.weekday()
        return day_of_week >= 0 and day_of_week <= 4

    def add_weekday_column(self):
        self.date_df['Weekday?'] = self.date_df['DateTime'].apply(self.check_weekday)

    def add_last_day_of_months(self):
        for i in range(1, 13):
            self.last_day_of_months.append(self.date_df[self.date_df['DateTime'].dt.month == i].iloc[-1]['DateTime'])

        for date in self.last_day_of_months:
            orig_date = date
            if date.weekday() >= 5:
                date = date - timedelta(days=(date.weekday() - 4))
            self.last_day_of_months[self.last_day_of_months.index(orig_date)] = date
        #debug print
        print(self.last_day_of_months)
        def check_eom(date):
            return date in self.last_day_of_months
        self.date_df['End_of_Month?'] = self.date_df['DateTime'].apply(check_eom)

    def check_day_after_hol(self, date):
        return (date + timedelta(days=-1)) in self.hol_list
    
    def generate_file_date(self, date):
        file_date = date + timedelta(days=1)
        
        flag = False
        while not flag:
            holiday = self.check_day_after_hol(file_date)
            eom = file_date in self.last_day_of_months
            weekday = self.check_weekday(file_date)

            if weekday and not holiday and not eom:
                return file_date
            
            file_date += timedelta(days=1)    

    def determine_after_cutoff(self, date):
        if date.weekday() == 4:
            file_date = date + timedelta(days=4)
        else:
            file_date = date + timedelta(days=2)
            
        flag = False
        while not flag:
            holiday = self.check_day_after_hol(file_date)
            eom = file_date in self.last_day_of_months
            weekday = self.check_weekday(file_date)
            if weekday and not holiday and not eom:
                return file_date
            
            file_date += timedelta(days=1)

    def generate(self):
        self.generate_dates()
        self.add_day_of_week()
        self.add_weekday_column()
        self.add_last_day_of_months()
        self.date_df['Holiday?'] = self.date_df['DateTime'].apply(self.check_day_after_hol)
        self.date_df['File Date'] = self.date_df['DateTime'].apply(self.generate_file_date)
        self.date_df['After Cutoff'] = self.date_df['DateTime'].apply(self.determine_after_cutoff)
        self.date_df['Formatted FD'] = self.date_df['File Date'].apply(lambda x: x.strftime('%m/%d/%Y'))
        self.date_df['Formatted Cutoff'] = self.date_df['After Cutoff'].apply(lambda x: x.strftime('%m/%d/%Y'))
        columns_to_drop = ['DateTime', 'File Date', 'After Cutoff','Day_of_Week_Index','Weekday?','End_of_Month?','Holiday?']
        self.date_df.drop(columns=columns_to_drop, inplace=True)
        return self.date_df