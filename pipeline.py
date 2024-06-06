import boto3

# Initialize boto3 clients
s3_client = boto3.client('s3')
codepipeline_client = boto3.client('codepipeline')
codebuild_client = boto3.client('codebuild')
iam_client = boto3.client('iam')

# Define the pipeline components
pipeline_name = 'MySamplePipeline'
bucket_name = 'my-source-bucket'
bucket_key = 'source.zip'
build_project_name = 'MyBuildProject'

# Create an S3 bucket if it doesn't exist
s3_client.create_bucket(Bucket=bucket_name)

# Create a CodeBuild project
build_project = codebuild_client.create_project(
    name=build_project_name,
    source={
        'type': 'S3',
        'location': f'{bucket_name}/{bucket_key}',
    },
    environment={
        'type': 'LINUX_CONTAINER',
        'image': 'aws/codebuild/standard:4.0',
        'computeType': 'BUILD_GENERAL1_SMALL',
    },
    serviceRole='<CodeBuildServiceRoleARN>'
)

# Create the pipeline
pipeline = codepipeline_client.create_pipeline(
    pipeline={
        'name': pipeline_name,
        'roleArn': '<PipelineServiceRoleARN>',
        'artifactStore': {
            'type': 'S3',
            'location': bucket_name,
        },
        'stages': [
            {
                'name': 'Source',
                'actions': [
                    {
                        'name': 'SourceAction',
                        'actionTypeId': {
                            'category': 'Source',
                            'owner': 'AWS',
                            'provider': 'S3',
                            'version': '1',
                        },
                        'runOrder': 1,
                        'configuration': {
                            'S3Bucket': bucket_name,
                            'S3ObjectKey': bucket_key,
                            'PollForSourceChanges': 'false',
                        },
                        'outputArtifacts': [
                            {
                                'name': 'SourceArtifact',
                            },
                        ],
                    },
                ],
            },
            {
                'name': 'Build',
                'actions': [
                    {
                        'name': 'BuildAction',
                        'actionTypeId': {
                            'category': 'Build',
                            'owner': 'AWS',
                            'provider': 'CodeBuild',
                            'version': '1',
                        },
                        'runOrder': 1,
                        'configuration': {
                            'ProjectName': build_project_name,
                        },
                        'inputArtifacts': [
                            {
                                'name': 'SourceArtifact',
                            },
                        ],
                        'outputArtifacts': [
                            {
                                'name': 'BuildArtifact',
                            },
                        ],
                    },
                ],
            },
        ],
    }
)

print(f"Pipeline {pipeline_name} created successfully.")
