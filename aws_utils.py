from django.template.loader import render_to_string


def render_policy(bucket, account, user):
    vars = {
        "bucket": bucket,
        "account_id": account,
        "user": user
    }
    return render_to_string("s3_policy.json.template", context=vars)


def install_policy(bucket, account, user):
    import boto3
    policy = render_policy(bucket, account, user)
    iam = boto3.client('iam')
    return iam.create_policy(
        PolicyName=f'bucket-{bucket}',
        PolicyDocument=policy
    )
