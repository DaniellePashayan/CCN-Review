import pandas as pd
import glob
from datetime import date, timedelta
from pathlib import Path
import os

def run():
    def is_file_in_use(file_path):
        """
        Determines if the file is open and Returns boolean. Raises FileNotFoundError if the file does not exist
        :param file_path:
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError

        try:
            path.rename(path)
        except PermissionError:
            return True
        else:
            return False


    def truncate_file_name(file_name):
        """
        Takes the full file path and Returns a truncated file name
        :param file_name:
        """
        short_name = file_name.replace(f"{P1_FILE_PATH}", "").replace(f"{P2_FILE_PATH}", "").replace(f"{ARS_FILE_PATH}", "")
        short_name = short_name.lstrip(f"\\{file_date}\\ ")
        return short_name


    ARS_FILE_PATH = "M:/CPP-Data/AR SUPPORT/SPECIAL PROJECTS/CHARGE CORRECTION BOT/SPREADSHEETS TO SEND TO BOT"
    P1_FILE_PATH = "M:/CPP-Data/Payor 1/Bot CCN"
    P2_FILE_PATH = "M:/CPP-Data/Payer 2/BOTS/Charge Correction Files"

    file_paths = [ARS_FILE_PATH, P1_FILE_PATH, P2_FILE_PATH]

    today = date.today()

    # if today is Friday
    if today.weekday() == 4:
        # set FILE_DATE to today + 3
        file_date = today + timedelta(days=3)
    else:
        # set FILE_DATE to today + 1
        file_date = today + timedelta(days=1)

    last_day_of_month = (file_date.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    if file_date == last_day_of_month:
        # advance to the next day until it's a business day
        while True:
            file_date += timedelta(days=1)
            if file_date.weekday() < 5:
                break

    # format file_date into desired formats
    file_date_plain = file_date.strftime('%m%d%Y')
    file_date_w_spaces = file_date.strftime('%m %d %Y')
    file_date_w_slashes = file_date.strftime('%m/%d/%Y')

    # extract day and month from file_date
    day = file_date.strftime('%d')
    month = file_date.strftime('%m')
    year = file_date.strftime('%Y')

    open_file_list = []
    empty_file_list = []
    files = []
    trunc_file_list = []
    final = []
    rep_name_list = []

    # Creates a LIST containing the file paths for a given file date
    for f in file_paths:
        files += glob.glob(f'{f}/*{file_date_plain}/*.xlsm')
    # print(files)

    # Goes through the File List. Checks if the file is open.
    # If it's not open it attempts to create a list of Pandas DataFrames
    for f in files:
        trunc_file = truncate_file_name(f)
        if is_file_in_use(f) and '~$' not in f:
            open_file_list.append(trunc_file)
        elif '~$' not in f:
            df = pd.read_excel(f, engine="openpyxl")
            if not df.empty:
                final.append(df)
                for _ in range(df.shape[0]):
                    trunc_file_list.append(trunc_file)
                    rep_name_list.append(trunc_file.replace(f" {file_date_w_spaces}.xlsm", ""))
            else:
                empty_file_list.append(trunc_file)
                # print(f"the file {trunc_file} is empty")
        else:
            continue

    # Concatenates the list of DataFrames into a single DataFrame
    final = pd.concat(final)

    # Sets the columns for the DataFrame
    df1 = pd.DataFrame(
        final,
        columns=[
            "Invoice",
            "ClaimReferenceNumber",
            "InvoiceDOS",
            "OriginalDOS",
            "NewDOS",
            "Charge",
            "TotalChg",
            "InvoiceBalance",
            "ProviderName",
            "NewProvider",
            "BillingArea",
            "NewBillingArea",
            "OriginalLocation",
            "NewLocation",
            "Insurance",
            "TXN",
            "OriginalCPT",
            "NewCPT",
            "OriginalDX",
            "NewDX",
            "DxPointers",
            "OriginalModifier",
            "NewModifier",
            "ActionAddRemoveReplace",
            "Reason",
            "STEP",
            "Data",
            "Retrieval_Status",
            "Retrieval_Description"
        ]
    )

    df3 = pd.DataFrame(
        columns=[
        'Invoice',
        'BAR_B_INV.SER_DT,',
        'BAR_B_TXN.SER_DT,',
        'BAR_B_INV.TOT_CHG,',
        'INV_BAL,',
        'PROV__1,',
        'LOC__2,',
        'BAR_B_INV.ORIG_FSC__5,',
        'BAR_B_INV.DX_ONE__3,',
        'DX_TWO__3,',
        'DX_THREE__3,',
        'DX_FOUR__3,',
        'DX_FIVE__3,',
        'DX_SIX__3,',
        'DX_SEVEN__3,',
        'DX_EIGHT__3,',
        'DX_NINE__3,',
        'DX_TEN__3,',
        'BAR_B_INV.DX_ELEVEN__3,',
        'BAR_B_INV.DX_TWELVE__3,',
        'TXN_NUM,',
        'PROC__2,',
        'MOD,',
        'BAR_B_TXN.DX_NUM,',
        'BAR_B_INV.CHG_CORR_FLAG,',
        'BAR_B_INV.CORR_INV_NUM',
        'BAR_B_TXN_LI_PAY.PAY_CODE__2'
        ]
        )

    # Writes the finale DataFrame to a new Excel sheet this becomes the Input File
    OUT_PATH_1 = "M:/CPP-Data/Sutherland RPA/Northwell Process Automation ETM Files/Monthly Reports/Charge Correction/Audits - Files Sent to Bot/"
    OUT_PATH_2 = "M:/CPP-Data/Sutherland RPA/Northwell Process Automation ETM Files/Monthly Reports/Charge Correction/Inputs/"
    
    df1.to_excel(f'{OUT_PATH_1}Northwell_ChargeCorrection_Input_{file_date_plain}.xlsx', index=False)
    with pd.ExcelWriter(f'{OUT_PATH_1}Northwell_ChargeCorrection_Input_{file_date_plain}.xlsx', mode='a', engine='openpyxl') as writer:
        # Write the DataFrame to a new sheet
        df3.to_excel(writer, sheet_name='Sheet2', index=False)
    
    # Create the input reference file
    df2 = df1[["Invoice", "ActionAddRemoveReplace", "Reason", "STEP"]].copy()
    df2["File Name"] = trunc_file_list
    df2["Rep Name"] = rep_name_list
    df2["File Date"] = file_date_w_slashes

    # df2.to_excel(writer2, index=False)
    df2.to_excel(f"{OUT_PATH_2}{year}/{month} {year}/Invoice Numbers and Rep Names {file_date_w_spaces}.xlsx", index=False)

    # output_path = 'C:/Users/denglish2/Desktop/output.txt'
    # Get the path to the desktop directory of the current user
    desktop_path = os.path.expanduser("~/Desktop")

    # Specify the output file name
    output_filename = "OpenOrInUseFilesOutput.txt"

    # Create the full output file path
    output_path = os.path.join(desktop_path, output_filename)
    # open the file in write mode and write the output to it
    with open(output_path, 'w') as f:
        f.write(f"These are the files that are still open: \n{open_file_list}\n")
        f.write(f"These are the files without any entries: \n{empty_file_list}\n")
        
    # open the file for reading and print its contents to the console
    with open(output_path, 'r') as f:
        print(f.read())


if __name__ == '__main__':
    run()
