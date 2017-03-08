### RDS Backup Tool
### Copies latest snapshots from east to west.
### 1st of the month snapshots to be kept on 13 month rotation.
### Deletes any long-term backups over 13 months old.

import json
import boto3
import operator
from datetime import datetime, timedelta, tzinfo

ACCOUNT = 'process.env.TEST'

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

    for project in snapshots_per_project:
        sorted_list = sorted(snapshots_per_project[project].items(), key=operator.itemgetter(1), reverse=True)

        copy_name = project + "-" + sorted_list[0][1].strftime("%Y-%m-%d")

        print("Checking if " + copy_name + " is copied")

        try:
            backup_client.describe_db_snapshots(
                DBSnapshotIdentifier=copy_name
            )
        except:
            response = backup_client.copy_db_snapshot(
                SourceDBSnapshotIdentifier='arn:aws:rds:us-east-1:' + ACCOUNT + ':snapshot:' + sorted_list[0][0],
                TargetDBSnapshotIdentifier=copy_name,
                CopyTags=True
            )

            if response['DBSnapshot']['Status'] != "pending" and response['DBSnapshot']['Status'] != "available":
                raise Exception("Copy operation for " + copy_name + " failed!")
            print("Copied " + copy_name)

            continue

        print("Already copied")


def remove_old_snapshots():
    client = boto3.client('rds', 'us-east-1')
    backup_client = boto3.client('rds', 'us-west-1')

    response = backup_client.describe_db_snapshots(
        SnapshotType='manual'
    )

    if len(response['DBSnapshots']) == 0:
        raise Exception("No manual snapshots in us-west-1 found")

    snapshots_per_project = {}
    for snapshot in response['DBSnapshots']:
        if snapshot['Status'] != 'available':
            continue

        if snapshot['DBInstanceIdentifier'] not in snapshots_per_project.keys():
            snapshots_per_project[snapshot['DBInstanceIdentifier']] = {}

        snapshots_per_project[snapshot['DBInstanceIdentifier']][snapshot['DBSnapshotIdentifier']] = snapshot[
            'SnapshotCreateTime']

    for project in snapshots_per_project:
        if len(snapshots_per_project[project]) > 1:
            sorted_list = sorted(snapshots_per_project[project].items(), key=operator.itemgetter(1), reverse=True)
            to_remove = [i[0] for i in sorted_list[1:]]

            for snapshot in to_remove:
                print("Removing " + snapshot)
                backup_client.delete_db_snapshot(
                    DBSnapshotIdentifier=snapshot
                )


def lambda_handler(event, context):
    copy_latest_snapshot()
    remove_old_snapshots()


if __name__ == '__main__':
    lambda_handler(None, None)
