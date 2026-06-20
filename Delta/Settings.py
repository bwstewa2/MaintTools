import os
import Delta.DeltaConstants as dc
import pandas as pd

class Settings:
    def __init__(self):
        self.settings = [{
            'pp': str(270)+'\u00b0',
            'ws': '8\"',
            'ds': 1.0, 
            'ia': False,
        }]
    
    # Read in .Settings .csv file
    def read(self):
        try:
            if os.path.exists(dc.SETTING_FILE):
                df = pd.read_csv(dc.SETTING_FILE, keep_default_na=False)
                self.settings = df.to_dict(orient='records')
        except FileNotFoundError:
            print(f"Error: File not found at '{dc.SETTING_FILE}'")
        except Exception as e:
            print(f"An error occurred: {e}")

    # Write out .Settings .csv file
    def write(self):
        try:
            os.system(f'attrib -h "{dc.SETTING_FILE}"')
            df = pd.DataFrame(self.settings, index=[0])
            df.to_csv(dc.SETTING_FILE, index=False)
            os.system(f'attrib +h "{dc.SETTING_FILE}"')
        except FileNotFoundError:
            print(f"Error: File not found at '{dc.SETTING_FILE}'")
        except Exception as e:
            print(f"An error occurred: {e}")

    # Change settings
    def change(self, pp, ws, ds, ia):
        self.settings = {
            'pp': pp,
            'ws': ws,
            'ds': ds, 
            'ia': ia,
        }

    def get(self):
        return self.settings[0]