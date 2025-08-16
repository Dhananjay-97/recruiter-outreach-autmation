   git clone https://github.com/your-username/recruiter-outreach-autmation.git
   cd recruiter-outreach-autmation
   ```

2. **Create a virtual environment (recommended):**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: `venv\Scripts\activate`
   ```

3. **Install the required packages:**

   ```bash
   pip install -r requirements.txt
   ```

### Configuration

1. **`recruiters_list.csv`**:
   Create a `recruiters_list.csv` file in the root directory with the following columns: `recruiter_name`, `company_name`, `recruiter_email`.

   Example `recruiters_list.csv`:
   ```csv
   recruiter_name,company_name,recruiter_email
   Jane Doe,Google,jane.doe@google.com
   John Smith,Microsoft,john.smith@microsoft.com
   ```

2. **`email_template.md`**:
   Customize the `email_template.md` file with your desired email content. Use `{{ recruiter_name }}` and `{{ company_name }}` as placeholders, which will be replaced dynamically.

   Example `email_template.md`:
   # recruiter-outreach-autmation