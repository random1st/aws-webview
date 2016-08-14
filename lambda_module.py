from __future__ import print_function

import json

import boto3

s3_client = boto3.client("s3")


def get_template(filename):
    response = s3_client.get_object(
        Bucket='config-data-bucket',
        Key='template/{}'.format(filename)
    )
    return response['Body'].read()


def get_objects_list():
    return [json.loads(
        s3_client.get_object(
            Bucket='config-data-bucket', Key=item['Key']
        )['Body'].read()
    ) for item in s3_client.list_objects_v2(
        Bucket='config-data-bucket', Prefix='data'
    )['Contents'] if item['Key'].endswith('.json')]


def get_object(id):
    response = s3_client.get_object(
        Bucket='config-data-bucket',
        Key='data/{}.json'.format(id)
    )
    return json.load(response['Body'])


def lambda_handler(event, context):
    print "Event received"
    resource = event['path_params']['resource']
    method = event['http_method']
    id = event['path_params'].get('id')

    if resource == 'user' and method=="GET":
        base_template = get_template('base.tpl')
        user_template = get_template('user.tpl')
        if id:
            user = get_object(id)
            return base_template.format(
                body=user_template.format(id=user['id'], name=user['name'])
            )

        else:
            users = get_objects_list()
            return base_template.format(
                body="".join(
                    user_template.format(id=user['id'], name=user['name']) for user
                    in users)
            )
