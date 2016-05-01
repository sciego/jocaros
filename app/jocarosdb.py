import MySQLdb
import game_categories

gc = game_categories
host = 'localhost'
user = 'root'
pwrd = '1234'
db = 'jocaros_db'

# Account
def check_email_and_username(email, username):
	result = None

	try:
		conn = MySQLdb.connect(host, user, pwrd, db)
		cursor = conn.cursor()
		cursor.execute("call check_email_and_username('" + email + "', '" + username + "');")
		result = cursor.fetchall()
	except:
		print "Error checking for email and username"
	
	cursor.close()
	conn.close()
	return result

def create_account(username, name, lastname, email, password, developer):
	result = None

	try:
		conn = MySQLdb.connect(host, user, pwrd, db)
		cursor = conn.cursor()
		cursor.execute("call create_account('"
			+ username + "', '"
			+ name + "', '"
			+ lastname + "', '"
			+ email + "', '"
			+ password + "', "
			+ developer + ");")
		conn.commit()
		result = [0, "Your account has been successfully created."]
	except:
		result = [1, "Unable to create new account. Please try again later."]
	
	cursor.close()
	conn.close()
	return result

def update_profile(id, name, lastname, email, avatar):
	result = None

	try:
		conn = MySQLdb.connect(host, user, pwrd, db)
		cursor = conn.cursor()
		query = "call update_profile(%s, %s, %s, %s, %s);"
		args = [id, name, lastname, email, avatar]
		cursor.execute(query, args)
		conn.commit()
		result = [0, "Changes have been made successfully"]

	except:
		result = [1, 'An error ocurred trying to update profile information. Please try again later.']

	cursor.close()
	conn.close()
	return result

def change_password(id, cpwd, npwd):
	result = None

	try:
		conn = MySQLdb.connect(host, user, pwrd, db)
		cursor = conn.cursor()
		cursor.execute("call change_password('" + id + "', '" + cpwd +"', '" + npwd + "');")
		result = cursor.fetchone()
		if result[0] == 1:
			result = "You password has been changed successfully."
		else:
			result = "The current password you entered is not correct."
	except Exception, e:
		result = "An error ocurred trying to change your password."

	cursor.close()
	conn.close()
	return result

def login(email, password):
	account = None
	
	try:
		conn = MySQLdb.connect(host, user, pwrd, db)
		cursor = conn.cursor()
		cursor.execute("call login ('"
			+ email + "', '"
			+ password + "');")
		account = cursor.fetchone()
		if account != None:
			account = [account[0], account[1], account[2], str(account[3]), account[4], str(account[5]), account[6], account[7]]
	except:
		print 'An error ocurred trying to authenticate. Please try again later.'

	cursor.close()
	conn.close()
	return account

def get_account_avatar(id):
	data = None

	try:
		conn = MySQLdb.connect(host, user, pwrd, db)
		cursor = conn.cursor()
		cursor.execute("SELECT Avatar FROM account WHERE Id='" + str(id) + "';");
		data = cursor.fetchone()[0]
	except:
		data = None

	cursor.close()
	conn.close()
	return data

# Friends/Users
def get_user_info(id):
	data = None

	try:
		conn = MySQLdb.connect(host, user, pwrd, db)
		cursor = conn.cursor()
		cursor.execute("select Id, Name, Lastname, Developer from account where Id='" + id + "';")
		data = cursor.fetchone()
	except:
		data = None

	cursor.close()
	conn.close()
	return data;

def get_friends(id):
	data = None

	try:
		conn = MySQLdb.connect(host, user, pwrd, db)
		cursor = conn.cursor()
		cursor.execute("call get_friends('" + id + "');")
		data = cursor.fetchall()
	except Exception, e:
		print str(e)

	cursor.close()
	conn.close()
	return data

def get_friend_requests(id): # Regardless who sent the request.
	data = None

	try:
		conn = MySQLdb.connect(host, user, pwrd, db)
		cursor = conn.cursor()
		cursor.execute("call get_friend_requests('" + id + "');")
		data = cursor.fetchall()
	except Exception, e:
		print str(e)

	cursor.close()
	conn.close()
	return data

def get_friend_requests_for(id): # Resquests sent TO 'id'.
	data = None

	try:
		conn = MySQLdb.connect(host, user, pwrd, db)
		cursor = conn.cursor()
		cursor.execute("call get_friend_requests_for('" + id + "');")
		data = cursor.fetchall()
	except:
		data = []

	cursor.close()
	conn.close()
	return data

def are_friends(user1, user2):
	friends = get_friends(user1)
	if friends != None:
		for f in friends:
			if f[0] == user2:
				return True

	return False

def friend_request_sent(user1, user2):
	requests = get_friend_requests(user1)
	if requests != None:
		for r in requests:
			if r[0] == user2:
				return True

	return False

def send_friend_request(from_user, to_user):
	result = None

	try:
		conn = MySQLdb.connect(host, user, pwrd, db)
		cursor = conn.cursor()
		cursor.execute("insert into friend values('" + from_user + "', '" + to_user + "', 2);")
		conn.commit()
		result = "Friend request sent successfully."
	except:
		result = "An error ocurred while trying to send the request."

	cursor.close()
	conn.close()
	return result

def update_friend_status(user1, user2, status): # To accept or reject friend request.
	result = None

	try:
		conn = MySQLdb.connect(host, user, pwrd, db)
		cursor = conn.cursor()
		query = "call update_friend_status(%s, %s, %s);"
		args = [user1, user2, status]
		cursor.execute(query, args)
		conn.commit()
		
		if status == '1':
			result = "Friend request accepted successfully."
		else:
			result = "Friend request rejected successfully."
	except:
		if status == '1':
			result = "An error ocurred trying to accept the friend request."
		else:
			result = "An error ocurred trying to reject the friend request."

	cursor.close()
	conn.close()
	return result

def get_suggested_friends(id):
	data = None

	try:
		conn = MySQLdb.connect(host, user, pwrd, db)
		cursor = conn.cursor()
		cursor.execute("call suggest_friends('" + id + "');")
		data = cursor.fetchall()
	except Exception, e:
		print str(e)

	cursor.close()
	conn.close()
	return data

# Messaging
def get_messages(id):
	data = None

	try:
		conn = MySQLdb.connect(host, user, pwrd, db)
		cursor = conn.cursor()
		cursor.execute("call get_messages('" + id + "');")
		data = cursor.fetchall()
	except:
		data = None

	cursor.close()
	conn.close()
	return data

def send_message(sender, to, subject, body):
	result = None

	try:
		conn = MySQLdb.connect(host, user, pwrd, db)
		cursor = conn.cursor()
		query = "call send_message(%s, %s, %s, %s);"
		args = [sender, to, subject, body]
		cursor.execute(query, args)
		conn.commit()
		result = "Message sent successfully."
	except:
		result = "An error ocurred trying to send the message."

	cursor.close()
	conn.close()
	return result;

def get_unread_messages_count(id):
	data = 0

	try:
		conn = MySQLdb.connect(host, user, pwrd, db)
		cursor = conn.cursor()
		cursor.execute("SELECT COUNT(*) FROM message WHERE Id_To='" + id + "' AND Seen=0;")
		data = cursor.fetchone()
	except:
		data = 0

	cursor.close()
	conn.close()
	return data

def get_message_by_id(id):
	data = None

	try:
		conn = MySQLdb.connect(host, user, pwrd, db)
		cursor = conn.cursor()
		cursor.execute("call get_message_by_id(" + str(id) + ");")
		data = cursor.fetchone()

	except:
		data = None

	cursor.close()
	conn.close()
	return data

def delete_message(id):
	result = None

	try:
		conn = MySQLdb.connect(host, user, pwrd, db)
		cursor = conn.cursor()
		cursor.execute("DELETE FROM message WHERE Id=" + str(id) + ";")
		conn.commit()
	except:
		result = "An error ocurred trying to delete the message."

	cursor.close()
	conn.close()
	return result;

# Game
def upload_game(id_dev, name, price, category, cover):
	feedback = None

	try:
		conn = MySQLdb.connect(host, user, pwrd, db)
		cursor = conn.cursor()
		query = "call insert_game(%s, %s, %s, %s, %s);"
		args = [id_dev, name, price, category, cover]
		cursor.execute(query, args)
		conn.commit()
		feedback = [0, "Your game has been successfully uploaded."]
	except:
		feedback = [1, "An error occurred uploading your game."]
	
	cursor.close()
	conn.close()
	return feedback

def search_games(by, value):
	data = None

	try:
		conn = MySQLdb.connect(host, user, pwrd, db)
		cursor = conn.cursor()
		cursor.execute("call search_games("
			+ str(by) + ", '"
			+ value + "');")
		if by == 1:
			data = cursor.fetchone()
			game = [data[0], data[1], data[2], data[3], data[4], data[5], gc.get(data[6]-1)]
			data = game
		else:
			data = cursor.fetchall()
	except:
		data = None

	cursor.close()
	conn.close()
	return data

def get_game_cover(id):
	data = None

	try:
		conn = MySQLdb.connect(host, user, pwrd, db)
		cursor = conn.cursor()
		cursor.execute("SELECT Cover FROM game WHERE Id=" + str(id) + ";");
		data = cursor.fetchone()[0];
	except:
		data = None

	cursor.close()
	conn.close()
	return data

def get_top_games():
	data = None

	try:
		conn = MySQLdb.connect(host, user, pwrd, db)
		cursor = conn.cursor()
		cursor.execute("call top_games();")
		data = cursor.fetchall()
	except Exception, e:
		print str(e)

	cursor.close()
	conn.close()
	return data

# Purchasing
def purchase_game(account_id, game_id):
	result = None

	try:
		conn = MySQLdb.connect(host, user, pwrd, db)
		cursor = conn.cursor()
		cursor.execute("call purchase_game('" + account_id + "', " + str(game_id) + ");")
		result = cursor.fetchone()
	except:
		result = [1, "An error occurred trying to purchase the game."]
	
	cursor.close()
	conn.close()
	return result

def get_purchases(id):
	data = None

	try:
		conn = MySQLdb.connect(host, user, pwrd, db)
		cursor = conn.cursor()
		cursor.execute("call get_purchases('" + id + "');")
		data = cursor.fetchall()
	except:
		data = None

	cursor.close()
	conn.close()
	return data

def add_funds(id, amount):
	if amount > 100 or amount < 10:
		return [1, "The amount is invalid."]

	result = None

	try:
		conn = MySQLdb.connect(host, user, pwrd, db)
		cursor = conn.cursor()
		cursor.execute("call add_funds('" + id + "', " + str(amount) + ");")
		conn.commit()
		result = [0, "You have successfully added funds to your Wallet."]
	except:
		result = [1, "An error ocurred trying to add funds."]

	cursor.close()
	conn.close()
	return result

def cash_reward_points(id, new_balance):
	result = None

	try:
		conn = MySQLdb.connect(host, user, pwrd, db)
		cursor = conn.cursor()
		cursor.execute("UPDATE account SET Balance=" + str(new_balance) + ", Reward_Points=0 "
			+ "WHERE Id='" + id + "';")
		conn.commit()
		result = [0, "You have successfully cashed your reward points to get in store credit."]
	except:
		result = [1, "An error ocurred trying to cash your points."]

	cursor.close()
	conn.close()
	return result