import os
import time

import boto3

from modo import *


class AnyPayAPI(object):
	def __init__(self):
		self.MAPI = Modo()
		self.vault = ModoVualt(self.MAPI)
		self.ACCESS_KEY = os.environ.get('access_key_id')
		self.SECRET_KEY = os.environ.get('secret_access_key')
		self.dynamodb = boto3.resource(
			'dynamodb',
			region_name="us-west-1",
			aws_access_key_id=self.ACCESS_KEY,
			aws_secret_access_key=self.SECRET_KEY
		)
		self.person_table = self.dynamodb.Table("Users")
		self.payment_table = self.dynamodb.Table("open_payments")

	def make_user(self, first_name=None, last_name=None, phone=None, email=None):
		user = ModoPerson(self.MAPI, phone=phone, email=email, lname=last_name, fname=first_name)

		self.person_table.put_item(
			Item={
				'User_ID': user.user_id,
				'First_Name': first_name,
				'Last_Name': last_name,
				'Phone': phone,
				'Email': email,
				'Payment_Methods': []
			}
		)
		return user.user_id

	def get_user(self, user_id):
		person = self.person_table.get_item(
			Key={
				'User_ID': user_id
			}
		)
		return person['Item']

	def add_card(self, user_id, account=""):
		card = ModoEscrow(self.vault, account=account)
		self.person_table.update_item(
			Key={
				'User_ID': user_id
			},
			UpdateExpression="SET Payment_Methods = list_append(Payment_Methods, :i)",
			ExpressionAttributeValues={
				':i': [card.account]
			},
			ReturnValues="UPDATED_NEW"
		)
		return card.vault_id

	def add_new_card(self, data):
		self.payment_table.put_item(
			Item={
				'id': str(time.time()),
				'data': data
			}
		)


if __name__ == '__main__':
	a = AnyPayAPI()
	user_id = a.make_user(first_name="Mark", last_name="Omo", phone="7025576763", email="mark@markomo.me")
	acc = a.add_card(user_id)
	print json.dumps(a.get_user(user_id), indent=4)

