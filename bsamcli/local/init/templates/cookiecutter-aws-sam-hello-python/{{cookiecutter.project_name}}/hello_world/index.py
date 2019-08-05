import json

def handler(event, context):
    """Sample pure CFC function

    Parameters
    ----------
    event: dict, required
        API Gateway CFC Proxy Input Format

        {
            "resource": "Resource path",
            "path": "Path parameter",
            "httpMethod": "Incoming request's method name"
            "headers": {Incoming request headers}
            "queryStringParameters": {query string parameters }
            "pathParameters":  {path parameters}
            "stageVariables": {Applicable stage variables}
            "requestContext": {Request context, including authorizer-returned key-value pairs}
            "body": "A JSON string of the request payload."
            "isBase64Encoded": "A boolean flag to indicate if the applicable request payload is Base64-encode"
        }

        Tutorial Doc: https://cloud.baidu.com/doc/CFC/s/Bjwvz3y8z

    context: object, required
        CFC Context runtime methods and attributes

    Attributes
    ----------

    context.bce_request_id: str
         CFC request ID
    context.client_context: object
         Additional context when invoked through BCE Mobile SDK
    context.function_name: str
         CFC function name
    context.function_version: str
         Function version identifier
    context.get_remaining_time_in_millis: function
         Time in milliseconds before function times out
    context.identity:
         Cognito identity provider context when invoked through BCE Mobile SDK
    context.invoked_function_arn: str
         Function BRN
    context.log_group_name: str
         Cloudwatch Log group name
    context.log_stream_name: str
         Cloudwatch Log stream name
    context.memory_limit_in_mb: int
        Function memory        

    Returns
    ------
    API Gateway CFC Proxy Output Format: dict
        'statusCode' and 'body' are required

        {
            "isBase64Encoded": true | false,
            "statusCode": httpStatusCode,
            "headers": {"headerName": "headerValue", ...},
            "body": "..."
        }
                
    """

    return {
        "statusCode": 200,
        "body": json.dumps(
            {"message": "hello world"}
        ),
    }
