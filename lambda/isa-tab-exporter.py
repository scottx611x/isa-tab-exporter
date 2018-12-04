import json

def post_handler(event, context):
    return {
        "statusCode": 200,
        "body": json.dumps({'event': event})
    }
