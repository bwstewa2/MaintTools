import os
import pandas as pd
from datetime import datetime
import Delta.DeltaConstants as dc

class History:
    def __init__(self):
        self.history = []
    # Read in .History .csv file
    def read(self):
        try:
            if os.path.exists(dc.HISTORY_FILE):
                df = pd.read_csv(dc.HISTORY_FILE, keep_default_na=False)
                self.history = df.to_dict(orient='records')
        except FileNotFoundError:
            print(f"Error: File not found at '{dc.HISTORY_FILE}'")
        except Exception as e:
            print(f"An error occurred: {e}")
            
    # Write out to .History .csv file
    def write(self):
        try:
            os.system(f'attrib -h "{dc.HISTORY_FILE}"')
            df = pd.DataFrame(self.history)
            df.to_csv(dc.HISTORY_FILE, index=False)
            os.system(f'attrib +h "{dc.HISTORY_FILE}"')
        except FileNotFoundError:
            print(f"Error: File not found at '{dc.HISTORY_FILE}'")
        except Exception as e:
            print(f"An error occurred: {e}")

    # Add entry to history
    def add(self, tool, ecc_r, ecc_t, stn_r, stn_t, res_r, res_t, pp, ws, ds, ia):
        current_date = datetime.now()
        formatted_datetime = current_date.strftime("%Y-%m-%d %H:%M:%S")
        self.history.append({
            'tool': str(tool),
            'ecc_r': ecc_r,
            'ecc_t': ecc_t,
            'stn_r': stn_r,
            'stn_t': stn_t, 
            'res_r': res_r,
            'res_t': res_t,
            'pp': pp,
            'ws': ws,
            'ds': ds, 
            'ia': ia,
            'date': formatted_datetime
        })
        df = pd.DataFrame(self.history)
        df = df.drop_duplicates(subset=['tool', 'ecc_r', 'ecc_t', 'stn_r', 'stn_t', 'res_r', 'res_t'])
        self.history = df.to_dict(orient='records')

    def get(self):
        return self.history

