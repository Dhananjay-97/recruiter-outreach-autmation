import argparse
import pandas as pd

from outreach import OutreachManager
from utils import ConfigLoader, Logger


def main():
    # Initialize argument parser
    parser = argparse.ArgumentParser(description="Recruiter Outreach Automation Script")
    parser.add_argument("pdf_file_path", help="Path to the PDF file containing recruiter data")
    args = parser.parse_args()

    # Initialize ConfigLoader and Logger
    config = ConfigLoader()
    logger = Logger(__name__)

    # Initialize the OutreachManager
    outreach_manager = OutreachManager(config=config, logger=logger)

    # Load recruiters from a data source
    recruiters_file = outreach_manager.load_recruiters(args.pdf_file_path)

    if recruiters_file:  # Check if loading was successful
        recruiters_df = pd.read_csv(recruiters_file)

        # Send outreach emails to the loaded recruiters
        for index, recruiter in recruiters_df.iterrows():
            email = recruiter['Email'] # Use 'Email' as column name
            name = recruiter['Name'].split()[0] if recruiter['Name'] else "HR" # Get first name
            company = recruiter['Company'] if recruiter['Company'] else "Their Company" # Get company name
            outreach_manager.send_outreach_email(email, name, company) # Changed arguments

        # Track responses from the recruiters
        outreach_manager.track_responses()
    else:
        logger.error("Failed to load recruiter data.  Exiting.")


if __name__ == "__main__":
    main()