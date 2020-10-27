# End points
PRODUCTION_API_ENDPOINT='https://api.furiosa.ai/api/v1'
SANDBOX_API_ENDPOINT='http://internal-furiosa-api-backend-dev-887583302.ap-northeast-2.elb.amazonaws.com:8080/api/v1'
LOCALHOST_API_ENDPOINT='http://localhost:8080/api/v1'
DEFAULT_API_ENDPOINT=PRODUCTION_API_ENDPOINT


# Shell environment variable list
FURIOSA_API_ENDPOINT_ENV='FURIOSA_API_ENDPOINT'
FURIOSA_ACCESS_KEY_ID_ENV='FURIOSA_ACCESS_KEY_ID'
SECRET_ACCESS_KEY_ENV='FURIOSA_SECRET_ACCESS_KEY'

# HTTP header keys
REQUEST_ID_HTTP_HEADER='X-Request-Id'
ACCESS_KEY_ID_HTTP_HEADER='X-FuriosaAI-Access-Key-ID'
SECRET_ACCESS_KEY_HTTP_HEADER='X-FuriosaAI-Secret-Access-KEY'

SUPPORT_TARGET_IRS = {'dfg', 'cdfg', 'ldfg', 'gir', 'lir', 'enf'}