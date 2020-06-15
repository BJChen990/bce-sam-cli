-- Tutorial Doc: https://cloud.baidu.com/doc/CFC/s/Bjwvz3y8z
-- @param {Object} event - CFC Http Trigger Input Format
-- @param {string} event.resource - Resource path.
-- @param {string} event.path - Path parameter.
-- @param {string} event.httpMethod - Incoming request's method name.
-- @param {Object} event.headers - Incoming request headers.
-- @param {Object} event.queryStringParameters - query string parameters.
-- @param {Object} event.pathParameters - path parameters.
-- @param {Object} event.requestContext - Request context
-- @param {Object} event.body - A JSON string of the request payload.
-- @param {boolean} event.body.isBase64Encoded - A boolean flag to indicate if the applicable request payload is Base64-encode
-- @param {Object} context
-- @param {string} context.functionName - CFC function name.
-- @param {string} context.memoryLimitInMB - Function memory.
-- @param {string} context.functionVersion - Function version identifier.
-- @param {string} context.invokeid - CFC invoke ID.
-- @param {string} context.functionbrn - Function BRN.
-- @param {string} context.clientContext - client Context.

-- @returns {Object} object - CFC Proxy Output Format
-- @returns {boolean} object.isBase64Encoded - A boolean flag to indicate if the applicable payload is Base64-encode (binary support)
-- @returns {string} object.statusCode - HTTP Status Code to be returned to the client
-- @returns {Object} object.headers - HTTP Headers to be returned
-- @returns {Object} object.body - JSON Payload to be returned


function handler(event, context)   
    response = {
        statusCode = 200,
        isBase64Encoded = false,
        body = { message = "hello world" },
        headers = { x_custom_header = "headerValue" },
    }    
    return response
end