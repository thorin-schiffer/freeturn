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
    s3 = boto3.client('s3')
    return s3.put_bucket_policy(
        Bucket=bucket,
        Policy=policy
    )
