import logging
import os
from typing import Dict, Any, List

import boto3
from botocore.exceptions import ClientError
from taggercore.config import set_config, Config, Credentials
from taggercore.model import Tag
from taggercore.usecase import perform_tagging, scan_region, scan_global

LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper()

logger = logging.getLogger()
logger.setLevel(LOGLEVEL)


def lambda_handler(event, context):
    lambda_config = fetch_lambda_env_config()
    tags = fetch_tags(lambda_config)
    credentials = get_iam_credentials_for_role(lambda_config["ACCOUNT_ROLE"], "ACCOUNT_ROLE_SESSION")
    set_config(
        Config(credentials=credentials, account_id=lambda_config["ACCOUNT_ID"], profile="ignored")
    )
    regional_resources = scan_region(lambda_config["REGION"])
    if lambda_config["TAG_GLOBAL_RES"] == "TRUE":
        global_resources = scan_global()
    else:
        global_resources = []
    tagging_result = perform_tagging(regional_resources + global_resources, tags)
    logger.info(tagging_result)


def fetch_lambda_env_config() -> Dict[str, Any]:
    return {
        "ORGA_ROLE": os.environ.get("ORGA_ROLE", ""),
        "ACCOUNT_ID": os.environ["ACCOUNT_ID"],
        "ACCOUNT_ROLE": os.environ["ACCOUNT_ROLE"],
        "REGION": os.environ["REGION"],
        "TAG_GLOBAL_RES": os.environ.get("TAG_GLOBAL_RES", "TRUE").upper(),
        "TAG_MODE": os.environ.get("TAG_MODE", "ACCOUNT").upper(),
        "TAGS": os.environ.get("TAGS", "")
    }


def fetch_tags(config: Dict[str, Any]) -> List[Tag]:
    tags = []
    tag_mode = config["TAG_MODE"]
    if tag_mode == "ACCOUNT":
        tags = fetch_tags_for_account(
            get_iam_credentials_for_role(config["ORGA_ROLE"], "ORGA_ROLE_SESSION"), config["ACCOUNT_ID"]
        )
        print(tags)
    elif tag_mode == "ENV":
        tags = fetch_tags_from_env(config)
    logger.info(f"Found tags {tags}")
    return tags


def get_iam_credentials_for_role(role: str, session_name: str) -> Credentials:
    if role == "":
        raise ConfigurationError(
            f"Please provide a valid IAM role ARN via ENV variable {session_name.replace('_SESSION', '')}"
        )
    try:
        sts_client = boto3.client("sts")
        assume_role_response = sts_client.assume_role(
            RoleArn=role, RoleSessionName=session_name
        )
    except ClientError as e:
        logger.error(
            f"Failed to retrieve credentials with role {role}, error {e.response}"
        )
        raise e
    return Credentials(
        aws_access_key_id=assume_role_response["Credentials"]["AccessKeyId"],
        aws_secret_access_key=assume_role_response["Credentials"]["SecretAccessKey"],
        aws_session_token=assume_role_response["Credentials"]["SessionToken"],
    )


def fetch_tags_for_account(credentials: Credentials, account_id: str) -> List[Tag]:
    try:
        client = boto3.client('organizations', **credentials)
        tag_response = client.list_tags_for_resource(ResourceId=account_id)
        tags = tag_response["Tags"]
        account_tags = []
        for tag in tags:
            account_tags.append(Tag(tag["Key"], tag["Value"]))
    except ClientError as e:
        logger.error(
            f"Failed to retrieve tags for account {account_id}, error {e.response}"
        )
        raise e
    return account_tags


def fetch_tags_from_env(config: Dict[str, Any]) -> List[Tag]:
    tags = []
    for tag in config["TAGS"].split(","):
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


class ConfigurationError(Exception):
    pass
