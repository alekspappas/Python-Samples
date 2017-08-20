import sys
import time

#Create function for dictionaries
def populate_dict(MovieLens_file, movie_dict, user_dict):
  line_count = 0
  user_count = 0
  movie_count = 0

  for line in MovieLens_file:
    line_count += 1
    field = line.split()
    user_id, movie_id, movie_rating = field[0], field[1], int(field[2])
  
    #Populate dictionary with user id keys and a dictionary for ratings as a value
    if user_id not in user_dict:
      user_count += 1
      ratings_dict, movie_rating_dict = {}, {}
      movie_rating_dict[movie_id] = movie_rating
    
      ratings_dict["ratings_total"] = movie_rating
      ratings_dict["ratings_count"] = 1
      ratings_dict["movie_ratings"] = movie_rating_dict
      user_dict[user_id] = ratings_dict
  
    else:
      user_dict[user_id]["ratings_total"] += movie_rating
      user_dict[user_id]["ratings_count"] += 1
      user_dict[user_id]["movie_ratings"][movie_id] = movie_rating 
    
    #Populate dictionary with movie id keys and sets of users who rated that movie for values
    if movie_id not in movie_dict:
      movie_count += 1
      user_set = set([user_id])
      movie_dict[movie_id] = user_set
    else:
      movie_dict[movie_id].add(user_id)

  user_dict = average_rating_per_user(user_dict)

  #Summarize file data to terminal
  print "\nRead %s lines with total of %s movies and %s users" % (line_count, movie_count, user_count)

#Create functions for similarities equation
#Create function to normalize values

def average_rating_per_user(user_dict):
  for key in user_dict:
    user_dict[key]["ratings_average"] = float(user_dict[key]["ratings_total"])/user_dict[key]["ratings_count"]
  return user_dict

#Create function to calculate numerator
def mean_difference(movieid_1, movieid_2, user_match):
  summation_mean_difference = 0
  
  for user in user_match:
    norm_rating_movie1 = user_dict[user]["movie_ratings"][movieid_1] - user_dict[user]["ratings_average"]
    norm_rating_movie2 = user_dict[user]["movie_ratings"][movieid_2] - user_dict[user]["ratings_average"]
    summation_mean_difference += float(norm_rating_movie1 * norm_rating_movie2)    
    
  return summation_mean_difference

#Create function to calculate denominator
def mean_squared_diff(movie_1, movie_2, user_match):
  sum_squared_diff_movie_1, sum_squared_diff_movie_2 = 0, 0 
  
  for user in user_match:
    sum_squared_diff_movie_1 +=  float((user_dict[user]["movie_ratings"][movie_1] - user_dict[user]["ratings_average"]) ** 2.0)
    sum_squared_diff_movie_2 += float((user_dict[user]["movie_ratings"][movie_2] - user_dict[user]["ratings_average"]) ** 2.0)
 
  return float((sum_squared_diff_movie_1 * sum_squared_diff_movie_2) ** (.5))   

#Create similarity function
def similarity(movie_1, movie_2, user_match):
  if mean_squared_diff(movie_1, movie_2, user_match) == 0:
    return float(mean_difference(movie_1, movie_2, user_match)) / float(1.e-6) 
  else:
    return float(mean_difference(movie_1, movie_2, user_match)) / mean_squared_diff(movie_1, movie_2, user_match)

#Analyze the command line arguments and setup the corresponding parameters
if len(sys.argv) < 3:
  print "Usage: \n python %s <MovieLens file> <similarities file> [user thresh (default = 5)]"
  exit()

MovieLens_file_name = sys.argv[1]
similarities_file_name = sys.argv[2]

if len(sys.argv) == 4:
  user_thresh = int(sys.argv[3])
else:
  user_thresh = 5

#Start summary text
print "Input MovieLens file: %s" % MovieLens_file_name
print "Output file for similarity data: %s" % similarities_file_name
print "Minimum number of common users: %s" % user_thresh

#Compute time start
t_0 = time.time()

#Open files for processing
MovieLens_file = open(MovieLens_file_name)
similarities_file = open(similarities_file_name, "w")

#Create dictionaries
movie_dict, user_dict = {}, {}

populate_dict(MovieLens_file, movie_dict, user_dict)

#Compute similarities

movies = []
for movie in movie_dict:
  movies.append(int(movie))

movies = sorted(movies)
movie_pairings = {}

for movie_1 in movies:
  highest_similarity = -2
  highest_similarity_id = ""
  user_match_count = 0

  for movie_2 in movies:
    if movie_1 != movie_2:
      user_match = movie_dict[str(movie_1)] & movie_dict[str(movie_2)]
      if len(user_match) < user_thresh: 
        continue
      
      pairing_key = 0
      if movie_1 > movie_2:
        pairing_key = "movie1:%s movie2:%s" % (movie_2, movie_1)
      else:
        pairing_key = "movie1:%s movie2:%s" % (movie_1, movie_2)
      
      #if we don't have this pairing key in movie_pairing calculate the similarity
      #otherwise get the similarity from movie_pairing
      if pairing_key in movie_pairings:
        new_similarity = movie_pairings[pairing_key]
      else:
        new_similarity = similarity(str(movie_1), str(movie_2), user_match)  
      if new_similarity > highest_similarity:
        highest_similarity = new_similarity
        highest_similarity_id = movie_2
        user_match_count = len(user_match)   
  
  if highest_similarity == -2:
      similarities_file.write(str(movie_1)+"\n")
  else:
    output_line = "%s (%s, %.2f, %s)\n" % (movie_1, highest_similarity_id, highest_similarity, user_match_count) 
    similarities_file.write(output_line)

#Compute time
t_1 = time.time()
print "Computed similarities in %.3f seconds" % (t_1-t_0)

#Close files
MovieLens_file.close()
similarities_file.close()
