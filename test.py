import json
import boto3
import operator
from datetime import datetime, timedelta, tzinfo

ACCOUNT = 'process.env.ACCOUNT'

def copy_latest_snapshot():
    client = boto3.client('rds', 'us-east-1')
    backup_client = boto3.client('rds', 'us-west-1')

    response = client.describe_db_snapshots(
        SnapshotType='automated',
        IncludeShared=False,
        IncludePublic=False
    )

    if len(response['DBSnapshots']) == 0:
        raise Exception("No automated snapshots found")

    snapshots_per_project = {}
    for snapshot in response['DBSnapshots']:
        if snapshot['Status'] != 'available':
            continue

    if snapshot['DBInstanceIdentifier'] not in snapshots_per_project.keys():
        snapshots_per_project[snapshot['DBInstanceIdentifier']] = {}

    snapshots_per_project[snapshot['DBInstanceIdentifier']][snapshot['DBSnapshotIdentifier']] = snapshot[
        'SnapshotCreateTime']





    ## if datetime.datetime.today().day = 1:
