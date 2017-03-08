# AWS Lambda Scripts

This is a collection of Lambda Scripts for AWS.

RDSBackup.py
- RDSBackup.py does 3 things
1. Copies latest snapshots from east to west.
2. Keeps the 1st of the month snapshots on a 13 month rotation.
3. Deletes any long-term backups over 13 months old.
