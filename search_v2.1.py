def get_type_query():
    type_query = None
    option_limit = 4
    while type_query not in range(1, 3):
        try:
            type_query = int(input('1. Album\n'
                                   '2. Artist\n'
                                   '3. Track \n'
                                   'Choose an Option : '))
            if type_query >= option_limit:
                print('Not an option')
            else:
                return type_query
        except ValueError:
            print('Not an int')


get_type_query()