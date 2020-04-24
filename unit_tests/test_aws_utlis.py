import pytest
import boto3
from moto import mock_s3, mock_sts

from aws_utils import install_policy


@pytest.fixture
def s3():
    with mock_s3():
        s3 = boto3.client('s3')
        yield s3


@pytest.fixture
def sts():
    with mock_sts():
        sts = boto3.client('sts')
        yield sts


@pytest.fixture
def bucket(s3):
    conn = boto3.resource('s3', region_name='eu-central-1')
    return conn.create_bucket(Bucket='bucket')


def test_install_s3_policy(bucket, sts, faker):
    account_id = sts.get_caller_identity().get('Account')
    user = 'root'
    install_policy('bucket', account_id, user)
