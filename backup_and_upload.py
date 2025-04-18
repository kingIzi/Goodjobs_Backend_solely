import subprocess
import os
from datetime import date

from upload_backup_to_s3 import upload_backup_to_s3

# Your existing command for Django dumpdata
command = [
    "/home/ubuntu/goodjobs/goodjobs-backend/venv/bin/python",
    "/home/ubuntu/goodjobs/goodjobs-backend/manage.py",
    "dumpdata"
]

# Execute the Django dumpdata command and capture the output
output = subprocess.check_output(command)

# Specify the file path for the JSON backup
json_backup_file_path = '/home/ubuntu/goodjobs/goodjobs-backend/backup.json'

# Write the output to the JSON backup file
with open(json_backup_file_path, 'wb') as backup_file:
    backup_file.write(output)

# Now perform the mysqldump for your MySQL database
db_username = "yanga"
db_name = "goodjobs"
sql_backup_file_path = "/home/ubuntu/goodjobs/goodjobs-backend/backup.sql"

# Construct the mysqldump command
mysqldump_command = f"mysqldump -u {db_username} -p {db_name} > {sql_backup_file_path}"

# Execute the mysqldump command
# Note: This uses shell=True, which is necessary for I/O redirection, but can be a security risk
# if the parameters are not controlled or validated.
subprocess.check_call(mysqldump_command, shell=True)

# Upload the JSON backup file to AWS S3
# Generate the current date in the format YYYY-MM-DD
current_date = date.today().strftime("%Y-%m-%d")

# Append the current date to the S3 key for JSON backup
json_s3_key = f"backups/{current_date}/backup.json"
upload_backup_to_s3(json_s3_key)

# Upload the SQL backup file to AWS S3
# Append the current date to the S3 key for SQL backup
sql_s3_key = f"backups/{current_date}/backup.sql"
upload_backup_to_s3(sql_s3_key, file_path=sql_backup_file_path)