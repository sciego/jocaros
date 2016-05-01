import jocarosdb
import game_categories
from flask import *
from functools import wraps
from werkzeug.utils import secure_filename

db = jocarosdb
app = Flask(__name__)
app.secret_key = '123'

ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png', 'gif'])
FILE_SIZE_LIMIT = 80000

# Wrappers
def login_required(test):
	@wraps(test)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return test(*args, **kwargs)
		else:
			return redirect(url_for('index'))
	return wrap

def developer_required(test):
	@wraps(test)
	def wrap(*args, **kwargs):
		if 'logged_in' not in session:
			feedback = [1, "You're not logged in."]
			return render_template('index.html', feedback=feedback)
		if session['logged_in'][4] == 0:
			feedback = [1, "You're not a Developer type user."]
			return render_template('home.html', feedback=feedback)
		else:
			return test(*args, **kwargs)
		
	return wrap

# Upload files
def allowed_images(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def upload_image(file):
    if file and allowed_images(file.filename):
    	filename = secure_filename(file.filename)
        image = file.read()
        if len(image) <= FILE_SIZE_LIMIT:
        	return image

    return None

# Login not required
@app.route('/')
def index():
	if 'logged_in' in session:
		return redirect(url_for('home'))
	return render_template('/index.html')

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
	feedback = None
	if request.method == 'POST':
		name = request.form['tbx-name']
		lastname = request.form['tbx-lastname']
		username = request.form['tbx-username']
		email = request.form['tbx-email']
		password = request.form['tbx-password']
		developer = request.form['developer']
		feedback = db.create_account(username, name, lastname, email, password, developer)
	return render_template('/create_account.html', feedback=feedback)

# Account
@app.route('/check_email_and_username')
def check_email_and_username():
	email = request.args.get('email', '', type=str)
	username = request.args.get('username', '', type=str)
	result = db.check_email_and_username(email, username)
	return jsonify(result=result)

@app.route('/login', methods=["GET", "POST"])
def login():
	error = None
	if request.method == "POST":
		session['logged_in'] = db.login(request.form['email'], request.form['password'])
		if session['logged_in'] == None:
			session.pop('logged_in', None)
			error = "Invalid username or password"
	
	if 'logged_in' in session:
		return redirect(url_for('home'))

	return render_template('/index.html', error=error)

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	return redirect(url_for('index'))

@app.route('/home')
@login_required
def home():
	# Search for best selling games (top 10)
	games = db.get_top_games()
	users = db.get_suggested_friends(session['logged_in'][0])
	return render_template('/home.html', games=games, users=users)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
	feedback = None
	if request.method == 'POST':
		name = request.form['tbx-name']
		lastname = request.form['tbx-lastname']
		email = request.form['tbx-email']
		avatar = upload_image(request.files['file'])
		if avatar == None:
			avatar = db.get_account_avatar(session['logged_in'][0])
		
		if email != session['logged_in'][5] and db.check_email_and_username(email, session['logged_in'][0])[0] > 0:
			feedback = [1, "The e-mail you choosed is already in use."]
		else:
			feedback = db.update_profile(session['logged_in'][0], name, lastname, email, avatar)
			if feedback[0] == 0:
				session['logged_in'][1] = name
				session['logged_in'][2] = lastname
				session['logged_in'][5] = email
		

	return render_template('profile.html', feedback=feedback)

@app.route('/change_password')
@login_required
def change_password():
	current = request.args.get('current', '', type=str)
	newpwd = request.args.get('newpwd', '', type=str)
	result = db.change_password(session['logged_in'][0], current, newpwd)
	return jsonify(result=result)

@app.route('/get_account_avatar/<id>')
@login_required
def get_account_avatar(id):
	data = db.get_account_avatar(id)
	if data == None:
		try:
			data = open('static/images/default_avatar.jpg', 'rb').read()
		except Exception, e:
			print str(e)
	return data

# Friends/Users
@app.route('/friends', methods=['GET', 'POST'])
@login_required
def friends():
	if request.method == "POST":
		username = request.form['tbx-username']
		return user_profile(username)

	friends = db.get_friends(session['logged_in'][0])
	return render_template('friends.html', users=friends)

@app.route("/user_profile/<id>")
@login_required
def user_profile(id): # Someone else's profile.
	feedback = None
	if id == session['logged_in'][0]:
		return profile()
	
	info = db.get_user_info(id)
	games = db.get_purchases(id)
	if info != None:
		developer = ""
		if info[3] == 0:
			developer = "Regular user"
		else:
			developer = "Developer"
		info = [info[0], info[1], info[2], developer, db.are_friends(session['logged_in'][0], info[0])]
		
	else:
		feedback = [1, "User not found."]
	
	return render_template('user_profile.html', info=info, games=games, feedback=feedback)

@app.route('/get_friend_requests')
@login_required
def get_friend_requests():
	friend_requests = db.get_friend_requests_for(session['logged_in'][0])
	return jsonify(result=friend_requests);

@app.route('/update_friend_request')
@login_required
def update_friend_request(): # Accept or reject friend request.
	id = request.args.get('id', '', type=str)
	status = request.args.get('status', 0, type=int)
	result = db.update_friend_status(session['logged_in'][0], id, str(status))
	return jsonify(result=result)

@app.route('/send_friend_request')
@login_required
def send_friend_request():
	id = request.args.get('id', 0, type=str)
	print id
	if db.friend_request_sent(session['logged_in'][0], id) == False:
		result = db.send_friend_request(session['logged_in'][0], id)
	else:
		result = "Unable to send friend request, it could be one of the following reasons:\n\n"
		result += "- You have already sent a friend request.\n"
		result += "- You have received a friend request from this user.\n"
		result += "- You have already accepted a friend request from this user."
	return jsonify(result=result)

# Messaging
@app.route('/send_message')
@login_required
def send_message():
	to = request.args.get('to', '', type=str)
	subject = request.args.get('subject', '', type=str)
	body = request.args.get('body', '', type=str)
	result = db.send_message(session['logged_in'][0], to, subject, body)

	return jsonify(result=result)

@app.route('/messages')
@login_required
def messages():
	messages = db.get_messages(session['logged_in'][0])
	if messages != None and len(messages) > 0:
		messages = reversed(messages)
	else:
		messages = None
	
	return render_template('messages.html', messages=messages)

@app.route('/get_unread_messages_count')
@login_required
def get_unread_messages_count():
	count = db.get_unread_messages_count(session['logged_in'][0])
	return jsonify(result=count)

@app.route('/get_message_by_id')
@login_required
def get_message_by_id():
	id = request.args.get('id', 0, type=int)
	message = db.get_message_by_id(id)
	return jsonify(result=message)

@app.route('/delete_message')
@login_required
def delete_message():
	id = request.args.get('id', 0, type=int)
	result = db.delete_message(id)
	return jsonify(result=result)

# Game
@app.route('/games_search', methods=['POST'])
@login_required
def games_search():
	search_by = request.form['searchbtn']
	search_for = request.form['tbx-search-game']
	by = 2 # If ENTER button is pressed or 'Title' link is clicked.
	if search_by == 'developer':
		by = 3
	games = db.search_games(by, search_for)
	
	return render_template('/games_search.html', games=games)

@app.route('/search_games_by_developer/<developer>')
@login_required
def search_games_by_developer(developer):
	games = db.search_games(3, developer)
	return render_template('/games_search.html', games=games)

@app.route('/get_game_cover/<int:id>')
@login_required
def get_game_cover(id):
	data = db.get_game_cover(id)
	if data == None:
		data = open('static/images/no_cover.jpg', 'rb').read()
	return data

@app.route('/game_overview/<int:id>,<int:purchased>')
@login_required
def game_overview(id, purchased):
	feedback = None
	game = db.search_games(1, str(id))
	if game == None:
			feedback = [1, "Game data does not exist."]

	return render_template('/game_overview.html', game=game, purchased=purchased, feedback=feedback)

# Purchases
@app.route('/purchase_game')
@login_required
def purchase_game():
	game_id = request.args.get('gameId', 0, type=int)
	result = db.purchase_game(session['logged_in'][0], game_id)
	if len(result) > 1:
		result = result[1]
	else:
		session['logged_in'] = db.login(session['logged_in'][5], session['logged_in'][7])
		result = result[0]

	return jsonify(result=result)

@app.route('/purchases')
@login_required
def purchases():
	purchases = db.get_purchases(session['logged_in'][0])
	if purchases != None and len(purchases) > 0:
		purchases = reversed(purchases)
	else:
		purchases = None

	return render_template('/purchases.html', purchases=purchases)

@app.route('/add_funds')
@login_required
def add_funds():
	amount = request.args.get('amount', 0, type=int)
	result = db.add_funds(session['logged_in'][0], amount)
	if result[0] == 0:
		session['logged_in'] = db.login(session['logged_in'][5], session['logged_in'][7])
	result = result[1]

	return jsonify(result=result)

@app.route('/reward_points', methods=['GET', 'POST'])
@login_required
def reward_points():
	feedback = None
	if request.method == "POST":
		if int(session['logged_in'][6]) > 0:
			new_balance = float(session['logged_in'][3]) + float(session['logged_in'][6])
			feedback = db.cash_reward_points(session['logged_in'][0], new_balance)
			if feedback[0] == 0:
				session['logged_in'][3] = new_balance
				session['logged_in'][6] = 0
		else:
			feedback = [1, "You don't have any reward points."]
	return render_template('reward_points.html', feedback=feedback)

# Developer
@app.route('/upload_game', methods=['GET', 'POST'])
@developer_required
def upload_game():
	feedback = None

	if request.method == 'POST':
		name = request.form['tbx-name']
		category = request.form['select-category']
		price = request.form['select-price']
		cover = upload_image(request.files['file'])
		if cover:
			feedback = db.upload_game(session['logged_in'][0], name, price, category, cover)
		else:
			feedback = [1, "You need to choose a valid game cover."]	

	categories = game_categories.get_categories_with_id()
	return render_template('upload_game.html', categories=categories, feedback=feedback)

if __name__ == '__main__':
	app.run(host="0.0.0.0")


