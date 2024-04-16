import json
import boto3


def lambda_handler(event, context):
    # TODO implement
    ecr = boto3.client('ecr')
    registryId = ""

    repositories_list = ecr.describe_repositories(
        registryId=registryId,
        maxResults=1000
    )

    for repository in repositories_list['repositories']:
        repositoryName = repository['repositoryName']
        imagesList = ecr.list_images(
            registryId=registryId,
            repositoryName=repositoryName,
            maxResults=1000,
            filter={
                'tagStatus': 'TAGGED'
            }
        )

        for image in imagesList['imageIds']:
            imageTag = image['imageTag']
            imageData = ecr.batch_get_image(
                registryId=registryId,
                repositoryName=repositoryName,
                imageIds=[
                    {
                        'imageTag': imageTag
                    },
                ],
            )
            print("Reuploading: ", repositoryName, ":", imageTag, end=" ")

            replication_info = ecr.describe_image_replication_status(
                repositoryName=repositoryName,
                imageId={
                    'imageTag': imageTag
                },
                registryId=registryId
            )
            replication_status= replication_info['replicationStatuses']
            ## Replication for unreplicated ones
            
            ## doing replication for failed ones
            if len(replication_status) != 0:
                 if replication_status[0]['status'] == "FAILED":
                        for image in imageData['images']:
                            tempTag = imageTag+"-temp"
                            imageManifest = image['imageManifest']
                            ecr.put_image(
                                registryId=registryId,
                                repositoryName=repositoryName,
                                imageManifest=imageManifest,
                                imageTag=tempTag
                            )
                            ecr.batch_delete_image(
                                registryId=registryId,
                                repositoryName=repositoryName,
                                imageIds=[
                                    {
                                        'imageTag': imageTag
                                    },
                                ]
                            )
                            ecr.put_image(
                                registryId=registryId,
                                repositoryName=repositoryName,
                                imageManifest=imageManifest,
                                imageTag=imageTag
                            )
                            ecr.batch_delete_image(
                                registryId=registryId,
                                repositoryName=repositoryName,
                                imageIds=[
                                    {
                                        'imageTag': tempTag
                                    },
                                ]
                            )
            print("OK")


    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
