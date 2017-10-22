import requests
import json

# import logging
# try:
#     import http.client as http_client
# except ImportError:
#     # Python 2
#     import httplib as http_client
# http_client.HTTPConnection.debuglevel = 1
#
# # You must initialize logging, otherwise you'll not see debug output.
# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True


def merge_dicts(*dict_args):
	"""
	From: https://stackoverflow.com/a/26853961/4492611
	Given any number of dicts, shallow copy and merge into a new dict,
	precedence goes to key value pairs in latter dicts.
	"""
	result = {}
	for dictionary in dict_args:
		result.update(dictionary)
	return result


class ModoException(ValueError):
	error_map = {
		1: "Success (how did you get this?)",
		-1000: "Exceeded allowed actions",
		-1001: "Unmet prerequisite",
		-1002: "Resource unavailable",
		-1003: "Not enough funds",
		-1004: "Invalid input",
		-1005: "Missing database object",
		-1006: "Duplicate request",
		-1007: "Action not supported",
		-1008: "Action not allowed",
		503: "Service unavailable",
		401: "Validation error"
	}

	def __init__(self, message, error_code):
		message = "{}\nError Code:{} - {}".format(message, error_code, self.code_to_message(error_code))
		super(ValueError, self).__init__(message)

	def code_to_message(self, code):
		if int(code) in self.error_map:
			return self.error_map[int(code)]
		else:
			return "Unknown Error!"


class Modo(object):
	api_url = "https://api.sbx.gomo.do/"
	request_header = {"Authorization": None}

	def __init__(self):
		with open("api-creds.json", "r") as f:
			self.sec_data = json.load(f)
		self.request_header["Authorization"] = "MODO0 key={}".format(self.sec_data["Key"])

	def post(self, url, headers=dict(), data=dict()):
		r = requests.post(self.api_url + url, headers=merge_dicts(self.request_header, headers), json=data).json()
		if int(r["status_code"]) is not 1:
			raise ModoException(r["developer_message"], r["status_code"])
		return r

	def get(self, url, headers=dict()):
		r = requests.post(self.api_url + url, headers=merge_dicts(self.request_header, headers)).json()
		if int(r["status_code"]) is not 1 or "developer_message" in r:
			raise ModoException(r["developer_message"], r["status_code"])
		return r

	@property
	def account_types(self):
		"""
		Get the account types for your Modo Account
		
		:return: List of accout types you can use
		:rtype: list
		"""
		# print self.request_header
		return self.post("api_v3/coin/account_types")["response_data"]


class ModoPerson(object):
	def __init__(self, api, user_id=None, phone=None, fname=None, lname=None, email=None):
		"""
		Object to represent a Modo Person
		
		:param api: Modo API instance
		:type api: Modo
		:param user_id: user_id (optional, if unprovided a person will be created)
		:type user_id: str
		:param fname: User First name (ignored if user_id is presented, required if not)
		:type fname: str
		:param lname: User Last name (ignored if user_id is presented, required if not)
		:type lname: str
		:param email: User email (ignored if user_id is presented, required if not)
		:type email: str
		"""

		self.api = api

		self._user_id = user_id
		self._phone = phone
		self._fname = fname
		self._lname = lname
		self._email = email

		if user_id is None:
			if phone is None:
				raise ValueError("Phone must not be none when creating a person!")
			if fname is None:
				raise ValueError("First Name (fname) must not be none when creating a person!")
			if lname is None:
				raise ValueError("Last Name (lname) must not be none when creating a person!")
			if email is None:
				raise ValueError("email must not be none when creating a person!")
			self._make_user()

	def _make_user(self):
		body = {
			"phone": int(self._phone),
			"fname": self._fname,
			"lname": self._lname,
			"email": self._email
		}
		self._user_id = self.api.post("api_v2/people/register", data=body)["response_data"]["user_id"]

	@property
	def phone(self):
		return self._phone

	@property
	def email(self):
		return self._email

	@property
	def fname(self):
		if self._fname is None:
			self._fname = api.post("people/profile", data={"user_id": self._user_id})["response_data"]["first_name"]
		return self._fname

	@property
	def lname(self):
		if self._lname is None:
			self._lname = api.post("people/profile", data={"user_id": self._user_id})["response_data"]["last_name"]
		return self._lname

	@property
	def user_id(self):
		return self._user_id

	def del_per(self):
		api.post("api_v2/people/delete", data={"user_id": self._user_id})

	def __repr__(self):
		return "User ID: {self.user_id}\nFirst Name: {self.fname}\nLast Name: {self.lname}\nPhone: {self.phone}\n" \
				"Email: {self.email}".format(
			self=self)


class ModoVualt(object):
	def __init__(self, api):
		self.api = api

	@property
	def types(self):
		return self.api.post("api_v2/vault/get_type_list")["response_data"]["vault_types"]

	def add(self, data):
		if not isinstance(data, list):
			data = [data]
		return self.api.post("api_v2/vault/add", data={"items": data})

	def get_byid(self, id):
		if not isinstance(id, list):
			id = [id]
		data = {
			"item_ids": id
		}
		r = self.api.post("api_v2/vault/fetch", data=data)
		return r["response_data"]

class ModoOpenCard(object):
	account_type = "OPEN_CARD"
	def __init__(self, vualt, vault_id=None, description="", pan=None, exp_month=None, exp_year=None, name=None, address=None, zip_code=None, cvv=None, user_id=None):
		if vualt is None:
			raise ValueError("Vualt must be provided!")
		if vault_id is None:
			if pan is None:
				raise ValueError("pan must be provided!")
			if exp_month is None:
				raise ValueError("exp_month must be provided!")
			if exp_year is None:
				raise ValueError("exp_year must be provided!")
			if name is None:
				raise ValueError("name must be provided!")
			if address is None:
				raise ValueError("address must be provided!")
			if zip_code is None:
				raise ValueError("zip_code must be provided!")
			if cvv is None:
				raise ValueError("cvv must be provided!")
		self.vualt = vualt
		self.vault_id = vault_id
		self.description = description
		self.pan = pan
		self.exp_month = exp_month
		self.exp_year = exp_year
		self.name = name
		self.address = address
		self.zip_code = zip_code
		self.cvv = cvv
		self.user_id = user_id

	def _create_card(self):
		data = {
			"vault_type": "OPEN_CARD",
			"description": self.description,
			"json_to_be_encrypted": json.dumps({
				'pan': self.pan, # (required, immutable), Card account number. 12-19 digits. Must pass luhn check.
				'exp_month': int(self.exp_month), # (required) note this is an integer- not a string
				'exp_year': int(self.exp_year), # (required) note this is an integer- not a string
				'name': self.name, # Full name on card, 2-52 characters
				'address': self.address, # First line of card billing address. 2-52 characters.
				'zip': self.zip_code, # Zip code of card billing address. 3-10 characters.
				'cvv': int(self.cvv), # Card security code.
			})
		}
		if self.user_id is not None:
			data["user_id"] = self.user_id

		self.vault_id = self.vualt.add(data=data)["response_data"]["vault_id"]


class ModoEscrow(object):
	account_type = "Escrow"
	def __init__(self, vault, vault_id=None, account=None, user_id=None, description=""):
		self.vault = vault
		self.vault_id = vault_id
		self._account = account
		self.user_id = user_id
		self.description = description

		if vault_id is None and account is None:
			raise ValueError("Accout must be provided to create account")
		elif vault_id is None:
			self._make_account()

	def _make_account(self):
		data = {
			"vault_type": "FUNDED_ESCROW",
			"description": self.description,
			"unencrypted_json": "{}"
		}
		if self.user_id is not None:
			data["user_id"] = self.user_id

		r = self.vault.add(data=data)
		# print r
		self.vault_id = r["response_data"][0]["vault_id"]

	@property
	def account(self):
		if self._account is None or len(self._account) < 5:
			self._account = self.vault.get_byid(self.vault_id)
		return self._account

	def __repr__(self):
		return "Modo Escrow (from vault)\nAccount: {self.account}\nUser ID: {self.user_id}\n" \
				"Vault ID: {self.vault_id}".format(self=self)


class ModoCoin(object):
	def __init__(self, api, coin_id=None, user_id=None, auto_operate=True, amount=1000, source=None, dest=None, description=""):
		if coin_id is None:
			if user_id is None:
				raise ValueError("User ID is required!")
			if source is None:
				raise ValueError("Source is required!")
			if dest is None:
				raise ValueError("Dest is required!")

		self.description = description
		self.api = api
		self.coin_id = coin_id
		self.user_id = user_id
		self.auto_operate = auto_operate
		self.amount = amount
		self.accounts = None
		if source is not None and not isinstance(source, list):
			source = [source]
		self.source = source
		if dest is not None and not isinstance(dest, list):
			dest = [dest]
		self.dest = dest
		self._state = None
		self.new_card = None

		if coin_id is None:
			self._mint_coin()

	def _mint_coin(self):
		inp = []
		for i in self.source:
			if isinstance(i, (ModoGenCard)):
				inp.append({
					"instrument_id": i.vault_id,
					"account_type": i.send_type
				})
			else:
				inp.append({
					"instrument_id": i.vault_id,
					"account_type": i.account_type
				})
		out = []
		for i in self.dest:
			if isinstance(i, (ModoGiftCard, ModoPOS)):
				out.append({
					"account_type": i.account_type,
					"qualifier": json.dumps({'merchant_id': i.qualifier})
				})
			else:
				out.append({
					"instrument_id": i.vault_id,
					"account_type": i.account_type
				})
		data = {
			"user_id": self.user_id,
			"description": self.description,
			"auto_operate": self.auto_operate,
			"amount": self.amount,
			"inputs": inp,
			"outputs": out
		}
		res = self.api.post("api_v3/coin/mint", data=data)
		# print res
		self.coin_id = res["response_data"]["coin_id"]
		self._state = res["response_data"]["state"]
		self.accounts = res["response_data"]["accounts"]
		for i in self.accounts:
			if "new_vault_item" in self.accounts[i] and self.accounts[i]["new_vault_item"]["type"] == "GENERATED_OPEN_CARD":
				new = ModoGenCard(self.api, self.accounts[i]["new_vault_item"]["vault_id"])
				new.card_data = self.accounts[i]["new_vault_item"]
				self.new_card = new
		return self._state

	def update(self):
		r = self.api.post("api_v3/coin/status", data={"coin_id": self.coin_id})
		self._state = r["response_data"]["state"]
		self.accounts = r["response_data"]["accounts"]
		for i in self.accounts:
			if "new_vault_item" in i and i["new_vault_item"]["type"] == "GENERATED_OPEN_CARD":
				new = ModoGenCard(self.api, i["new_vault_item"]["vault_id"])
				new.card_data = i["new_vault_item"]
				self.new_card = new

	def pump(self, reason=""):
		return self.api.post("api_v3/coin/status", data={"coin_id": self.coin_id, "reason": reason})["response_data"]["state"]


class ModoGiftCard(object):
	account_type = "GiftCard"
	def __init__(self, api, vault_id, qualifier=None):
		self.api = api
		self.vault_id = vault_id
		self.qualifier = qualifier

class ModoPOS(object):
	account_type = "MerchantPos"
	def __init__(self, api, vault_id, qualifier):
		self.api = api
		self.vault_id = vault_id
		self.qualifier = qualifier


class ModoGenCard(object):
	account_type = "CardIssuer"
	send_type = "Card"

	def __init__(self, vault, vault_id):
		self.vault = vault
		self.vault_id = vault_id
		self.card_data = None

	def attributes(self):
		self.card_data = self.vault.get_byid(self.vault_id)["response_data"][0]
		return self.card_data

	def __repr__(self):
		return json.dumps(self.card_data, indent=4)

if __name__ == '__main__':
	api = Modo()
	v = ModoVualt(api)
	print api.account_types
	mark = ModoPerson(api, phone="8025576763", fname="Mark", lname="Test", email="mark+test@markomo.me")
	src = ModoEscrow(v, account="Mark Test 2")
	gift = ModoGenCard(v, None)
	c = ModoCoin(api, user_id=mark.user_id, source=src, dest=gift)
	print json.dumps(c.accounts, indent=4)
	print c.new_card
