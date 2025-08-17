import argparse
import pandas as pd

from outreach import OutreachManager
from utils import ConfigLoader, Logger


def main():
    """
    Main function to orchestrate the recruiter outreach automation.
    """
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
        recruiters = recruiters_df.to_dict("records")
        logger.info(f"Loaded {len(recruiters)} recruiter records.")
        outreach_manager.send_emails_concurrently(recruiters)
    else:
        logger.error("Failed to load recruiter data.  Exiting.")


if __name__ == "__main__":
    main()