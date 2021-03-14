import re

# flag = False
# text = input("Enter some text: ")
#
# while not flag:
#     if re.search('[*+-]', text):
#         print("contains invalid characters")
#         flag = True
#     else:
#         print('valid')
#         break


artist_top_tracks_url = 'http://api.spotfy.com/v1/artists/'
artist_top_tracks_query = f'{artist_top_tracks_url}6eUKZXaKkcviH0Ku9w2n3V/top-tracks/'
print(artist_top_tracks_query)
