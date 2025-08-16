import os  # Import the os module
import smtplib
import time
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pandas as pd
import pdfplumber

from utils import ConfigLoader, Logger, RateLimiter


class OutreachManager:
    """
    OutreachManager handles recruiter outreach automation, including loading recruiter details from PDF,
    sending personalized outreach emails with resume attachments, and managing email rate limiting.

    Attributes:
        config (ConfigLoader): Configuration loader for environment variables and settings.
        logger (Logger): Logger instance for logging events and errors.
        recruiters (list): List to store recruiter details.
        email_user (str): Email address used for sending outreach emails.
        email_password (str): Password for the email account.
        smtp_server (str): SMTP server address for sending emails.
        smtp_port (int): SMTP server port.
        email_rate_limiter (RateLimiter): Rate limiter for controlling email sending frequency.
        resume_path (str): File path to the resume to be attached in emails.
        template_path (str): File path to the email template.

    Methods:
        load_template():
            Loads the email template from the specified file path.

        load_recruiters(file_path):
            Extracts recruiter details from a PDF file and saves them to a CSV file.

        send_outreach_email(hr_email, hr_name, company_name):
            Sends a personalized outreach email with a resume attachment to a recruiter.

        track_responses():
            Placeholder for tracking recruiter responses.
    """
    def __init__(self, config=None, logger=None):
        self.config = config or ConfigLoader()
        self.logger = logger or Logger(__name__)
        self.recruiters = []
        # Email setup from config
        self.email_user = self.config.get("EMAIL_USER")
        self.email_password = self.config.get("EMAIL_PASSWORD")
        self.smtp_server = self.config.get("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(self.config.get("SMTP_PORT", 587))
        self.email_rate_limiter = RateLimiter(
            calls_per_period=int(self.config.get("EMAIL_CALLS_PER_PERIOD", 10)),
            period=int(self.config.get("EMAIL_PERIOD", 60))
        )
        self.resume_path = self.config.get("RESUME_PATH")
        self.template_path = self.config.get("EMAIL_TEMPLATE_PATH", "email_template.md")  # Default template path

    def load_template(self):
        """Loads the email template from the specified file."""
        try:
            with open(self.template_path, "r", encoding="utf-8") as f:
                template = f.read()
            return template
        except FileNotFoundError:
            self.logger.error(f"Email template file not found at {self.template_path}")
            return None

    def load_recruiters(self, file_path):
        """
        Extracts recruiter details from a PDF file and saves them to a CSV file.

        Args:
            file_path (str): The path to the PDF file containing recruiter information.

        Returns:
            str or None: The path to the generated CSV file ("recruiters_list.csv") if successful, 
            or None if an error occurs.

        Side Effects:
            - Creates a CSV file named "recruiters_list.csv" in the current working directory.
            - Logs information and errors using the class logger.

        Raises:
            None: All exceptions are caught and logged internally.
        """
        try:
            pdf_path = file_path
            rows = []
            first_page = True

            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    table = page.extract_table()
                    if table:
                        if not first_page:
                            table = table[1:]
                        rows.extend(table)
                    first_page = False

            df = pd.DataFrame(rows[1:], columns=['SNo', 'Name', 'Email', 'Title', 'Company'])
            df.to_csv("recruiters_list.csv", index=False)
            self.logger.info("Recruiter details extracted and saved to recruiters_list.csv")
            return "recruiters_list.csv"

        except FileNotFoundError as e:
            self.logger.error(f"PDF file not found: {e}")
            return None
        except pd.errors.EmptyDataError as e:
            self.logger.error(f"Error with recruiter data: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error loading recruiters from PDF: {e}")
            return None

    def send_outreach_email(self, hr_email, hr_name, company_name):
        """
        Sends an outreach email to a recruiter or HR contact with a personalized message and resume attachment.

        Args:
            hr_email (str): The email address of the HR contact or recruiter.
            hr_name (str): The name of the HR contact or recruiter.
            company_name (str): The name of the company to personalize the email content.

        Returns:
            None

        Side Effects:
            - Waits for the email rate limiter before sending.
            - Loads and formats an email template with recruiter and company information.
            - Attaches the resume file to the email.
            - Logs errors if the resume file is not found or if sending the email fails.
            - Logs a success message if the email is sent successfully.
            - Sleeps for 3 seconds after sending the email.

        Raises:
            None directly, but logs exceptions encountered during file handling or email sending.
        """
        self.email_rate_limiter.wait()
        subject = "Seeking Assistance for Suitable Job Opportunity & Referral"

        template = self.load_template()
        if template is None:
            return  # Stop if template loading fails

        # Create a dictionary with the values to replace in the template
        template_vars = {
            "recruiter_name": hr_name,
            "company_name": company_name,
        }

        # Replace the placeholders in the template with the actual values
        body = template.format(**template_vars)  # Use .format instead of f-strings


        msg = MIMEMultipart()
        msg["From"] = self.email_user
        msg["To"] = hr_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        try:
            with open(self.resume_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(self.resume_path)}")  # Use os.path.basename
            msg.attach(part)
        except FileNotFoundError:
            self.logger.error(f"Resume file not found at {self.resume_path}")
            return

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.sendmail(self.email_user, hr_email, msg.as_string())

            self.logger.info(f"Email sent successfully to {hr_name} ({hr_email})")
            time.sleep(3)

        except smtplib.SMTPException as e:
            self.logger.error(f"SMTP error while sending email to {hr_email}: {e}")
        except OSError as e:
            self.logger.error(f"OS error while sending email to {hr_email}: {e}")

    def track_responses(self):
        pass