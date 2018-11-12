import json

import pytest

from hello_world import index


@pytest.fixture()
def api_proxy_event():
    """ Generates Http api-proxy Event"""

    return {
        "body": "eyJ0ZXN0IjoiYm9keSJ9",
        "resource": "/{proxy+}",
        "requestContext": {},
        "queryStringParameters": {
            "foo": "bar"
        },
        "httpMethod": "POST",
        "pathParameters": {},
        "headers": {
            "Content-Length": "12",
            "App": "HTTP-Trigger",
            "User-Agent": "Custom User Agent String",
            "Connection": "close",
            "X-Bce-Request-Id": "ee2637aa-4ec7-434e-a210-039203f5c449",
            "Content-Type": "text/plain; charset=utf-8"
        },
        "path": "/test",
        "isBase64Encoded": False
    }

def test_handler(api_proxy_event):
    ret = index.handler(api_proxy_event, "")
    assert ret["statusCode"] == 200
    
    assert "message" in ret["body"]
    
    data = json.loads(ret["body"])
    assert data["message"] == "hello world"
