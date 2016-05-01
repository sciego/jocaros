categories = ['Action/Adventure',
				'Strategy',
				'Fighting',
				'RPG',
				'Shooter',
				'Sports',
				'Platform',
				'Puzzle']

def get(numeric_value):
	return categories[numeric_value]

def get_categories_with_id():
	new_list = [{} for i in range(len(categories))]
	for index, c in enumerate(categories):
		new_list[index] = [index+1, c]

	return new_list