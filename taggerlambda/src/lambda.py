import logging
import os
from typing import Dict, Any, List

import boto3
from botocore.exceptions import ClientError
from taggercore.config import set_config, Config, Credentials
from taggercore.model import Tag
from taggercore.usecase import perform_tagging, scan_region, scan_global

ORGA_ROLE = os.environ.get('ORGA_ROLE', '')
ACCOUNT_ID = os.environ['ACCOUNT_ID']
ACCOUNT_ROLE = os.environ['ACCOUNT_ROLE']
REGION = os.environ['REGION']
TAG_GLOBAL_RES = os.environ.get('TAG_GLOBAL_RES', 'TRUE').upper()
LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
TAG_MODE = os.environ.get('TAG_MODE', 'ACCOUNT').upper()
TAGS = os.environ.get('TAGS', '')

logger = logging.getLogger()
logger.setLevel(LOGLEVEL)


def lambda_handler(event, context):
    tags = fetch_tags(TAG_MODE)
    credentials = fetch_credentials_for_account_role(ACCOUNT_ROLE)
    set_config(Config(
        credentials=credentials, account_id=ACCOUNT_ID, profile='ignored'
    ))
    regional_resources = scan_region(REGION)
    if TAG_GLOBAL_RES == 'TRUE':
        global_resources = scan_global()
    else:
        global_resources = []
    tagging_result = perform_tagging(regional_resources + global_resources, tags)
    logger.info(tagging_result)


def fetch_tags(tag_mode: str) -> List[Tag]:
    tags = []
    if tag_mode == 'ACCOUNT':
        tags = fetch_tags_for_account(get_organization_credentials(ORGA_ROLE), ACCOUNT_ID)
    elif tag_mode == 'ENV':
        tags = fetch_tags_from_env()
    logger.info(f"Found tags {tags}")
    return tags


def get_organization_credentials(role: str) -> Credentials:
    if role == '':
        raise ConfigurationError(
            "Please provide a valid IAM role ARN via ENV variable ORGA_ROLE"
        )
    sts_client = boto3.client('sts')
    assume_role_response = sts_client.assume_role(
        RoleArn=role,
        RoleSessionName="organization_role")
    return Credentials(
        aws_access_key_id=assume_role_response['Credentials']['AccessKeyId'],
        aws_secret_access_key=assume_role_response['Credentials']['SecretAccessKey'],
        aws_session_token=assume_role_response['Credentials']['SessionToken']
    )


def fetch_tags_for_account(client: Any, account_id: str) -> List[Tag]:
    try:
        tag_response = client.list_tags_for_resource(ResourceId=account_id)
        tags = tag_response['Tags']
        account_tags = []
        for tag in tags:
            account_tags.append(Tag(tag['Key'], tag['Value']))
    except ClientError as e:
        logger.error(f"Failed to retrieve tags for account {account_id}, error {e.response}")
        account_tags = []
    return account_tags


def fetch_tags_from_env() -> List[Tag]:
    tags = []
    for tag in TAGS.split(","):
        try:
            tag_without_whitespace = remove_whitespace(tag)
            key, value = tag_without_whitespace.split("=")
            tags.append(Tag(key, value))
        except ValueError:
            raise ConfigurationError(
                "Please provide tags in the following format: Key=Value and separate them with ,"
            )
    return tags


def remove_whitespace(input_str: str) -> str:
    return input_str.lstrip().rstrip()


def fetch_credentials_for_account_role(role: str) -> Dict[str, str]:
    sts_connection = boto3.client('sts')
    another_account = sts_connection.assume_role(
        RoleArn=role,
        RoleSessionName="cross_acct_lambda"
    )

    access_key = another_account['Credentials']['AccessKeyId']
    secret_key = another_account['Credentials']['SecretAccessKey']
    session_token = another_account['Credentials']['SessionToken']
    return {"aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "aws_session_token": session_token}


class ConfigurationError(Exception):
    pass
