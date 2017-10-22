import requests
import json

if __name__ == '__main__':
	r = requests.get("https://5nyjla88ub.execute-api.us-west-1.amazonaws.com/prod/AnyPay-Pay", headers={"user_id": "7399a968-a4df-4daf-acb6-70603433ca94", "payment_id": "8acb83b6-8c30-4f26-9a08-cc11980a9b7c"})
	print json.dumps(r.text)
	print r.status_code