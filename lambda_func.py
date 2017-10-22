import boto3
import json
import base64
from modo import *
from user_object import AnyPayAPI

def lambda_handler(event, context):
	if len(event) < 1:
		return {"error": "no request body!"}
	user_id = event["headers"]["user_id"]
	payment_id = event["headers"]["payment_id"]

	api = Modo()
	v = ModoVualt(api)
	print api.account_types
	mark = ModoPerson(api, user_id=user_id)
	src = ModoEscrow(v, vault_id=payment_id)
	dest = ModoGenCard(v, None)
	c = ModoCoin(api, user_id=mark.user_id, source=src, dest=dest)

	card = c.new_card.card_data
	a = AnyPayAPI()
	a.add_new_card(c.new_card.card_data)
	print card

	return {
		"isBase64Encoded": False,
		"statusCode": 200,
		"headers": {},
		"body": base64.b64encode("%{pan}^CARD/OPEN^{exp_month}{exp_year}000123456789?".format(**c.new_card.card_data["encrypted"]))
	}


if __name__ == '__main__':
	body = {
		"body": "{\"test\":\"body\"}",
		"resource": "/{proxy+}",
		"requestContext": {
			"resourceId": "123456",
			"apiId": "1234567890",
			"resourcePath": "/{proxy+}",
			"httpMethod": "POST",
			"requestId": "c6af9ac6-7b61-11e6-9a41-93e8deadbeef",
			"accountId": "123456789012",
			"identity": {
				"apiKey": None,
				"userArn": None,
				"cognitoAuthenticationType": None,
				"caller": None,
				"userAgent": "Custom User Agent String",
				"user": None,
				"cognitoIdentityPoolId": None,
				"cognitoIdentityId": None,
				"cognitoAuthenticationProvider": None,
				"sourceIp": "127.0.0.1",
				"accountId": None
			},
			"stage": "prod"
		},
		"queryStringParameters": {
			"foo": "bar"
		},
		"headers": {
			"Via": "1.1 08f323deadbeefa7af34d5feb414ce27.cloudfront.net (CloudFront)",
			"Accept-Language": "en-US,en;q=0.8",
			"CloudFront-Is-Desktop-Viewer": "true",
			"CloudFront-Is-SmartTV-Viewer": "false",
			"CloudFront-Is-Mobile-Viewer": "false",
			"X-Forwarded-For": "127.0.0.1, 127.0.0.2",
			"CloudFront-Viewer-Country": "US",
			"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
			"Upgrade-Insecure-Requests": "1",
			"X-Forwarded-Port": "443",
			"Host": "1234567890.execute-api.us-east-1.amazonaws.com",
			"X-Forwarded-Proto": "https",
			"X-Amz-Cf-Id": "cDehVQoZnx43VYQb9j2-nvCh-9z396Uhbp027Y2JvkCPNLmGJHqlaA==",
			"CloudFront-Is-Tablet-Viewer": "false",
			"Cache-Control": "max-age=0",
			"User-Agent": "Custom User Agent String",
			"CloudFront-Forwarded-Proto": "https",
			"Accept-Encoding": "gzip, deflate, sdch",
			"user_id": "7399a968-a4df-4daf-acb6-70603433ca94",
			"payment_id": "8acb83b6-8c30-4f26-9a08-cc11980a9b7c"
		},
		"pathParameters": {
			"proxy": "path/to/resource"
		},
		"httpMethod": "POST",
		"stageVariables": {
			"baz": "qux"
		},
		"path": "/path/to/resource"
	}
	print lambda_handler(body, "a")
