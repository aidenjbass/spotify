# query = input('What would you like to search for? : ')
# must be string, can be anything

def get_search_field():
    search_field = None
    try:
        search_field = str(input('What would you like to search for? : '))
        return search_field
    except ValueError:
        print('invalid')


get_search_field()
