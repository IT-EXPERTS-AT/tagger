# Taggerlambda

## Usage

The lambda function can be deployed via [SAM](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html)

### Prerequisites

SAM needs an S3 bucket, you can create one by running  
`aws s3 mb s3://{BUCKET_NAME} --region {REGION_NAME}`

### Scenarios
#### Cross account deployment with account tags
![](tagging_architecture_cross_account_account_tags.jpg)

The lambda function can be deployed in a management account.  
It fetches tags attached to the Service 1 account, scans the service 1 account and applies the fetched tags to the scanning result.  
Every tag applied to the service 1 account will be attached to the scanned resources.
##### Configuration  
Please specify the following ENV variables in  [template.yaml](template.yml)
```
Environment:
        Variables:
          TAG_MODE: 'ACCOUNT'
          TAGS: '{YOUR_TAGS}' # e.g. Project=Marketing, Owner=Team1
          ACCOUNT_ID: {SERVICE_1_ACCOUNT_ID}
          ORGA_ROLE: 'ORGA_ROLE_ARN'
          ACCOUNT_ROLE: '{ACCOUNT_ROLE_ARN}'
          REGION: '{REGION_NAME}' #e.g. eu-central-1
```
**`ORGA_ROLE`** 

This role needs access to the Organization API.  
Currently, this is only possible by using a role in the master account of the organization.
The role should have the policy: 
`AWSOrganizationsReadOnlyAccess` and a **trust relationship** with the **management** account:
```
{
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": {
           "AWS": "arn:aws:iam::{MANAGEMENT_ACCOUNT_ID}:root"
         },
         "Action": "sts:AssumeRole",
         "Condition": {}
       }
     ]
   }
```
Please replace `{MANAGEMENT_ACCOUNT_ID}` with the AWS account id of your management account.


**`ACCOUNT_ROLE`**

This role needs the following policies:  

AWS managed:  
- `ResourceGroupsandTagEditorFullAccess`
- `ReadOnlyAccess`

Custom:

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "sns:TagResource",
                "lambda:TagResource",
                "iam:TagRole",
                "elasticbeanstalk:AddTags",
                "elasticbeanstalk:ListTagsForResource",
                "es:AddTags",
                "logs:TagLogGroup",
                "dynamodb:TagResource",
                "s3:PutBucketTagging",
                "cloudtrail:AddTags",
                "firehose:TagDeliveryStream",
                "rds:AddTagsToResource",
                "apigateway:PUT",
                "ec2:CreateTags",
                "cloudfront:TagResource",
                "acm:AddTagsToCertificate",
                "elasticache:AddTagsToResource",
                "iam:TagUser",
                "cloudwatch:TagResource",
                "events:TagResource",
                "sqs:TagQueue",
                "kinesis:AddTagsToStream",
                "elasticloadbalancing:AddTags",
                "route53:ChangeTagsForResource",
                "apigateway:POST",
                "elasticmapreduce:AddTags"
            ],
            "Resource": "*"
        }
    ]
}
```

This role needs a trust relationship too: 
```
{
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": {
           "AWS": "arn:aws:iam::{MANAGEMENT_ACCOUNT_ID}:root"
         },
         "Action": "sts:AssumeRole",
         "Condition": {}
       }
     ]
   }
```
Please replace `{MANAGEMENT_ACCOUNT_ID}` with the AWS account id of your management account.


#### Cross account deployment with env tags
![](tagging_architecture_cross_account_env_tags.jpg)

This scenario uses tags configured by the ENV variable `TAGS`.   
Every tag found in the ENV variable will be attached to the scanned resources.

##### Configuration  
Please specify the following ENV variables in  [template.yaml](template.yml)

```
Environment:
        Variables:
          TAG_MODE: 'ENV'
          TAGS: '{YOUR_TAGS}' # e.g. Project=Marketing, Owner=Team1
          ACCOUNT_ID: {SERVICE_1_ACCOUNT_ID}
          ACCOUNT_ROLE: '{ACCOUNT_ROLE_ARN}'
          REGION: '{REGION_NAME}' #e.g. eu-central-1
```

**`ACCOUNT_ROLE`**

Please see use the configuration from [Scenario 1](#cross-account-deployment-with-account-tags)


#### Account deployment


