from typing import List

import boto3
import pytest
from botocore.exceptions import ClientError
from taggercore.model import Resource, Tag, TaggingResult

from src import ConfigurationError
from src import lambda_handler


@pytest.fixture(scope="module")
def tags() -> List[Tag]:
    yield [
        Tag("Project", "CoolProject"),
        Tag("Owner", "Fritz"),
        Tag("Created", "2020-08-01"),
    ]


@pytest.fixture(scope="module")
def regional_resources(tags) -> List[Resource]:
    yield [
        Resource("arn:aws:sqs:eu-central-1:111111111111:someq", "someq", "queue", tags),
        Resource(
            "arn:aws:sqs:eu-central-1:111111111111:someq2", "someq2", "queue", tags
        ),
        Resource(
            "arn:aws:ec2:eu-central-1:111111111111:security-group/sg-b501f6d0",
            "sg-b501f6d0",
            "security-group",
            tags,
        ),
    ]


@pytest.fixture(scope="module")
def global_resources(tags) -> List[Resource]:
    yield [
        Resource(
            "arn:aws:cloudfront::111111111111:distribution/EMS6KR7IENMDE",
            "EMS6KR7IENMDE",
            "distribution",
            tags,
        ),
        Resource(
            "arn:aws:route53::111111111111:healthcheck/f665452c-bf56-4a43-8b5d-319c3b8d0a70",
            "f665452c-bf56-4a43-8b5d-319c3b8d0a70",
            "healthcheck",
            tags,
        ),
    ]


@pytest.fixture(scope="function")
def env_for_tag_mode_env(monkeypatch):
    config = {
        "ACCOUNT_ID": "111111111111",
        "TAG_MODE": "ENV",
        "TAGS": "Project=Marketing, Owner=Team1",
        "REGION": "eu-central-1",
        "ACCOUNT_ROLE": "arn:aws:iam::111111111111:role/some-role",
    }
    monkeypatch.setenv("ACCOUNT_ID", config["ACCOUNT_ID"])
    monkeypatch.setenv("TAG_MODE", config["TAG_MODE"])
    monkeypatch.setenv("TAGS", config["TAGS"])
    monkeypatch.setenv("REGION", config["REGION"])
    monkeypatch.setenv("ACCOUNT_ROLE", config["ACCOUNT_ROLE"])
    yield config


@pytest.fixture(scope="function")
def env_tag_mode_env_without_global_res(monkeypatch, env_for_tag_mode_env):
    monkeypatch.setenv("TAG_GLOBAL_RES", "FALSE")
    return env_for_tag_mode_env


@pytest.fixture(scope="function")
def env_tag_mode_env_without_tags(monkeypatch, env_for_tag_mode_env):
    monkeypatch.delenv("TAGS")
    return env_for_tag_mode_env


@pytest.fixture(scope="function")
def env_for_tag_mode_account(monkeypatch):
    config = {
        "ACCOUNT_ID": "111111111111",
        "TAG_MODE": "ACCOUNT",
        "REGION": "eu-central-1",
        "ACCOUNT_ROLE": "arn:aws:iam::111111111111:role/some-role",
        "ORGA_ROLE": "arn:aws:iam::222222222222:role/orga-role",
    }
    monkeypatch.setenv("ACCOUNT_ID", config["ACCOUNT_ID"])
    monkeypatch.setenv("TAG_MODE", config["TAG_MODE"])
    monkeypatch.setenv("REGION", config["REGION"])
    monkeypatch.setenv("ACCOUNT_ROLE", config["ACCOUNT_ROLE"])
    monkeypatch.setenv("ORGA_ROLE", config["ORGA_ROLE"])
    yield config


@pytest.fixture(scope="function")
def env_for_tag_mode_account_without_orga_role(monkeypatch, env_for_tag_mode_account):
    monkeypatch.delenv("ORGA_ROLE")
    return env_for_tag_mode_account


@pytest.fixture(scope="module")
def tagging_result(regional_resources, global_resources) -> TaggingResult:
    successful_arns = [resource.arn for resource in regional_resources] + [
        resource.arn for resource in global_resources
    ]
    yield TaggingResult(successful_arns, {})


class TestLambda:
    def test_lambda_in_tag_mode_env(
        self,
        mocker,
        env_for_tag_mode_env,
        regional_resources,
        global_resources,
        tagging_result,
    ):
        mocked_region_scan = mocker.patch("src.tagging_lambda.scan_region")
        mocked_region_scan.return_value = regional_resources

        mocked_global_scan = mocker.patch("src.tagging_lambda.scan_global")
        mocked_global_scan.return_value = global_resources

        mocked_perform_tagging = mocker.patch("src.tagging_lambda.perform_tagging")
        mocked_perform_tagging.return_value = tagging_result

        mocked_boto_client = mocker.patch.object(boto3, "client")
        mocked_boto_client.return_value.assume_role.return_value = {
            "Credentials": {
                "AccessKeyId": "access_key",
                "SecretAccessKey": "secret_key",
                "SessionToken": "token1",
            }
        }

        lambda_handler(None, None)

        mocked_region_scan.assert_called_once_with(env_for_tag_mode_env["REGION"])
        mocked_global_scan.assert_called_once()
        mocked_perform_tagging.assert_called_once()

    def test_lambda_in_tag_mode_env_without_global_res(
        self,
        mocker,
        env_tag_mode_env_without_global_res,
        regional_resources,
        global_resources,
        tagging_result,
    ):
        mocked_region_scan = mocker.patch("src.tagging_lambda.scan_region")
        mocked_region_scan.return_value = regional_resources

        mocked_global_scan = mocker.patch("src.tagging_lambda.scan_global")
        mocked_global_scan.return_value = global_resources

        mocked_perform_tagging = mocker.patch("src.tagging_lambda.perform_tagging")
        mocked_perform_tagging.return_value = tagging_result

        mocked_boto_client = mocker.patch.object(boto3, "client")
        mocked_boto_client.return_value.assume_role.return_value = {
            "Credentials": {
                "AccessKeyId": "access_key",
                "SecretAccessKey": "secret_key",
                "SessionToken": "token1",
            }
        }

        lambda_handler(None, None)

        mocked_region_scan.assert_called_once_with(
            env_tag_mode_env_without_global_res["REGION"]
        )
        mocked_global_scan.assert_not_called()
        mocked_perform_tagging.assert_called_once()

    def test_lambda_in_tag_mode_env_without_tags(self, env_tag_mode_env_without_tags):
        with pytest.raises(ConfigurationError):
            lambda_handler(None, None)

    def test_lambda_in_tag_mode_account(
        self,
        mocker,
        env_for_tag_mode_account,
        regional_resources,
        global_resources,
        tagging_result,
    ):
        mocked_region_scan = mocker.patch("src.tagging_lambda.scan_region")
        mocked_region_scan.return_value = regional_resources

        mocked_global_scan = mocker.patch("src.tagging_lambda.scan_global")
        mocked_global_scan.return_value = global_resources

        mocked_perform_tagging = mocker.patch("src.tagging_lambda.perform_tagging")
        mocked_perform_tagging.return_value = tagging_result

        mocked_boto_client = mocker.patch.object(boto3, "client")
        mocked_boto_client.return_value.assume_role.return_value = {
            "Credentials": {
                "AccessKeyId": "access_key",
                "SecretAccessKey": "secret_key",
                "SessionToken": "token1",
            }
        }
        mocked_list_tags_for_resource = (
            mocked_boto_client.return_value.list_tags_for_resource
        )
        mocked_list_tags_for_resource.return_value = {
            "Tags": [
                {"Key": "Project", "Value": "CRM"},
                {"Key": "Owner", "Value": "Team2"},
            ]
        }
        expected_tags = [Tag("Project", "CRM"), Tag("Owner", "Team2")]

        lambda_handler(None, None)

        mocked_list_tags_for_resource.assert_called_with(
            ResourceId=env_for_tag_mode_account["ACCOUNT_ID"]
        )
        mocked_region_scan.assert_called_once_with(env_for_tag_mode_account["REGION"])
        mocked_global_scan.assert_called_once()
        mocked_perform_tagging.assert_called_once_with(
            regional_resources + global_resources, expected_tags
        )

    def test_lambda_in_tag_mode_account_without_orga_role(
        self, env_for_tag_mode_account_without_orga_role
    ):
        with pytest.raises(ConfigurationError):
            lambda_handler(None, None)

    def test_lambda_in_tag_mode_account_failing_to_fetch_credentials(
        self, mocker, env_for_tag_mode_account
    ):
        mocked_boto_client = mocker.patch.object(boto3, "client")
        mocked_boto_client.return_value.assume_role.side_effect = ClientError(
            operation_name="assume_role",
            error_response={"Error": {"Code": "UnauthorizedException"}},
        )

        with pytest.raises(ClientError):
            lambda_handler(None, None)

    def test_lambda_in_tag_mode_account_failing_to_fetch_tags(
        self, mocker, env_for_tag_mode_account
    ):
        mocked_boto_client = mocker.patch.object(boto3, "client")
        mocked_boto_client.return_value.assume_role.return_value = {
            "Credentials": {
                "AccessKeyId": "access_key",
                "SecretAccessKey": "secret_key",
                "SessionToken": "token1",
            }
        }
        mocked_list_tags_for_resource = (
            mocked_boto_client.return_value.list_tags_for_resource
        )
        mocked_list_tags_for_resource.side_effect = ClientError(
            operation_name="list_tags_for_resource",
            error_response={"Error": {"Code": "UnauthorizedException"}},
        )

        with pytest.raises(ClientError):
            lambda_handler(None, None)
