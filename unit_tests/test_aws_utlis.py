import json
import uuid

import pytest
import boto3
from moto import mock_s3, mock_sts, mock_iam

from aws_utils import install_policy, render_policy


@pytest.fixture(scope='session')
def s3():
    with mock_s3():
        s3 = boto3.client('s3')
        yield s3


@pytest.fixture(scope='session')
def sts():
    with mock_sts():
        sts = boto3.client('sts')
        yield sts


@pytest.fixture(scope='session')
def iam():
    with mock_iam():
        iam = boto3.client('iam')
        yield iam


@pytest.fixture(scope='session')
def bucket(s3):
    conn = boto3.resource('s3')
    return conn.create_bucket(Bucket='bucket')


@pytest.fixture(scope='session')
def user(iam):
    name = str(uuid.uuid4())
    iam.create_user(UserName=name)
    return name


def test_install_s3_policy(bucket, sts, user, s3):
    account_id = sts.get_caller_identity().get('Account')
    install_policy(bucket.name, account_id, f'user/{user}')
    policy = s3.get_bucket_policy(Bucket=bucket.name)
    assert json.loads(policy['Policy']) == json.loads(render_policy(bucket.name, account_id, f'user/{user}'))


def test_reinstall_s3_policy(bucket, sts, user, s3):
    account_id = sts.get_caller_identity().get('Account')
    install_policy(bucket.name, account_id, f'user/{user}')
    s3.get_bucket_policy(Bucket=bucket.name)
    policy = s3.get_bucket_policy(Bucket=bucket.name)
    assert json.loads(policy['Policy']) == json.loads(render_policy(bucket.name, account_id, f'user/{user}'))
