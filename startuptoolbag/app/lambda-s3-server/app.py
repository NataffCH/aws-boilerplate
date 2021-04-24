import boto3
import os
import uuid
from urllib.parse import unquote_plus

bucket_name = os.environ['BUCKET']
s3_client = boto3.client('s3')


def handler(event, context):
    s3 = boto3.resource('s3')

    #Overy simplistic lambda
    item = event["queryStringParameters"]["item"]
    obj = s3.Object(bucket_name, item)
    body = obj.get()['Body'].read()
