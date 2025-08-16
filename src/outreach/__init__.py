import pdfplumber
import pandas as pd

class OutreachManager:
    def __init__(self):
        self.recruiters = []

    def load_recruiters(self, file_path):
        
        pdf_path = file_path
        rows = []

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    rows.extend(table)

        # Convert to DataFrame and clean up header
        df = pd.DataFrame(rows[1:], columns=rows[0])
        df.to_csv("recruiters_list.csv", index=False)

        print("Recruiter details extracted and saved to recruiters_list.csv")

        return "recruiters_list.csv"
    
    def send_outreach_email(self, recruiter_email, message):
        pass

    def track_responses(self):
        # Logic to track responses from recruiters
        pass