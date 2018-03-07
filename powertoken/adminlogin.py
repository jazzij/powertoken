from werkzeug.security import generate_password_hash, check_password_hash

class Admin:
	def __init__(self, email, password, username=None):
		self.email = email
		self.username = username if username else email
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)