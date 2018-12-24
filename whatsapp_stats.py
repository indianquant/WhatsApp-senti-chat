"""
Priyanshu Varshney
11 June 2018
Parser for WhatsApp chat history.
Displays stats related to messages including stats for individuals and the group.
"""

import re
import sys
#subsititue for nltk
from textblob import TextBlob
import string
#user defined class
from person import Person
import collections
from collections import defaultdict

# Global stats variables
people = []
stopwords = []
message_count = 0
longest_message_person = ""
shortest_message_length = 999 
shortest_message = ""
shortest_message_person = ""
most_messages = ""
least_messages = ""
chat_os = "" # flag for which OS the chat file was exported from
global_dict = {} 
ascii_check = 0 
most_positive_polarity = 0
most_positive_message = ""
most_positive_message_person = ""
most_negative_polarity = 0
most_negative_message = ""
most_negative_message_person = ""
longest_message_length = 0
longest_message = ""

def bot(filename, stopwords_filename):
	global stopwords
	global chat_os

	chat = readfile(filename)
	find_stop_words(stopwords_filename)
	
	first_line = chat[0]
	first_line = first_line.strip()
	first_line = first_line.lstrip("\xef\xbb\xbf") # Beginning of line chars
	chat_os = os1(first_line)
	print(chat_os)
	main(chat)

	print_results()

# Checks which operating system the chat history file is from.
def os1(line):
	osx_pattern = re.compile(r'\d\d\d\d/\d\d/\d\d,')
	android_pattern = re.compile(r'\d/\d/\d\d')
	android_pattern2= re.compile(r'\d\d/\d/\d\d')
	android_pattern3= re.compile(r'\d/\d\d/\d\d')
	android_pattern4= re.compile(r'\d\d/\d/\d\d')
	osx_match = osx_pattern.search(line)
	android_match  = android_pattern.search(line)
	if not android_match:
		android_match  = android_pattern2.search(line)

	if not android_match:
		android_match  = android_pattern3.search(line)
	
	if not android_match:
		android_match  = android_pattern4.search(line)

	if osx_match:
	    return "osx"
	elif android_match:
		return "android"
	else:
		return "no match"


def find_stop_words(stopwords_filename):
	global stopwords
	
	stopwords = readfile(stopwords_filename)

	for stopword in stopwords:
		stopwords[stopwords.index(stopword)] = stopword.strip()


def readfile(filename):
	with open(filename) as f:
		content = f.readlines()

	return content

def write_file(content):
	with open("stats_"+filename+".txt", "w") as output_file: #PVDW - Output file now defaults to stats_filename
		output_file.write(content)

def get_array(line):

	if not all(char.isspace() for char in line):
		os = os1(line)
			
		if os == "osx":
			return line.split(": ")
		elif os == "android":
			line_array = []
			temp_line_array = line.split(" - ")
			# print("2",temp_line_array[0])
			# print("2",temp_line_array[1])
			if len(temp_line_array) >= 2:
				line_array.append(temp_line_array[0])
				temp_line_array = temp_line_array[1].split(": ")
				# print("2",temp_line_array[0])
				# print(temp_line_array)

				if len(temp_line_array) >= 2:
					line_array.append(temp_line_array[0])
					line_array.append(temp_line_array[1])	
					# print(line_array)
					return line_array
		else:
			print("This line could not be parsed: " + line)

def main(chat):
	names = []

	for line in chat:
		line = line.strip()
		line = line.lstrip("\xef\xbb\xbf") # Beginning of line chars
		# print("1",chat)
		line_arr = get_array(line)
		# print(len(line_arr))
		if line_arr and len(line_arr) >= 3:
			name = line_arr[1]
			message = line_arr[2]

			
			if name not in names:
				add_person(name)
				names.append(name)

			person = get_person(name)
			person.os = chat_os

			media = False 
			if chat_os == "osx":
				if is_image(message):
					media = True
					person.image_count += 1
				elif is_video(message):
					media = True
					person.video_count += 1
			elif chat_os == "android":
				#TODO - Added Media for Android Support
				if is_media(message):
					media = True
					person.media_count += 1

			if not media:
				polarity = get_polarity(message)
				statistics(message, polarity, name)
				
				if polarity == 0:
					person.neutral_count += 1
				elif polarity > 0:
					person.positive_count += 1
				else:
					person.negative_count += 1

				person.message_count += 1

				person.character_count += len(message)

				word_count = get_word_count(message)
				person.word_count += word_count

				if word_count > person.max_message_length:
					person.max_message_length = word_count
				elif word_count < person.min_message_length:
					person.min_message_length = word_count

				update(person, message)


def update(person, message):
	global stopwords

	words = re.split(r'[^0-9A-Za-z]+', message)

	for word in words:
		if not word.isspace() and len(word) > 2:
			if word.lower() not in stopwords:
				if word.lower() in person.common_words:
					person.common_words[word.lower()] += 1
				else:
					person.common_words[word.lower()] = 1

	for word in words:
		if not word.isspace() and len(word) > 2:
			if word.lower() not in stopwords:
				if word.lower() in global_dict:
					global_dict[word.lower()] += 1
				else:
					global_dict[word.lower()] = 1

def is_media(message):
	if message.rstrip() == "<Media omitted>":
		return True
	else:
		return False
	
def is_image(message):
	if message.rstrip() == "<image omitted>":
		return True
	else:
		return False

def is_video(message):
	if message.rstrip() == "<video omitted>":
		return True
	else:
		return False

def add_person(name):
	found = False

	for person in people:
		# print("@",person)
		if person.name == name:
			found = True
		

	if not found:
		new_person = Person(name)
		people.append(new_person)
		# print("#",people,name)

def get_person(name):
	for person in people:
		if person.name == name:
			return person

def get_polarity(message):
	printable = set(string.printable)
	message_printable_only = filter(lambda x: x in printable, message)
	a=''
	a=a.join(list(message_printable_only))
		
	blob_message = TextBlob(a)
	# print("#",a)	
	return blob_message.sentiment.polarity

def statistics(message, polarity, name):
	global message_count
	global most_negative_polarity
	global most_positive_polarity
	global most_negative_message
	global most_positive_message
	global most_positive_message_person
	global most_negative_message_person
	global longest_message_length
	global shortest_message_length
	global longest_message
	global shortest_message
	global longest_message_person
	global shortest_message_person

	message_count += 1

	if polarity > most_positive_polarity:
		most_positive_polarity = polarity
		most_positive_message = message
		most_positive_message_person = name
	elif polarity < most_negative_polarity:
		most_negative_polarity = polarity
		most_negative_message = message
		most_negative_message_person = name

	message_length = len(message)
	words = re.split(r'[^0-9A-Za-z]+', message) 
	if message_length < 5:
		try:
			print("1")
		except UnicodeDecodeError:
			ascii_check = 0
			#Message is not ascii
		else:
			ascii_check = 1
			#Message is ascii
	else:
		ascii_check = 1
		#Message might contain ascii

		if message_length > longest_message_length:
			longest_message_length = message_length
			longest_message = message
			longest_message_person = name
		elif message_length < shortest_message_length: 
			if ascii_check > 0: 
				if len(words) > 2: 
					shortest_message_length = message_length
					shortest_message = message
					shortest_message_person = name

def get_min_max():
	max_message_count = 0
	min_message_count = 100000
	max_message_count_person = ""
	min_message_count_person = ""
	string = ""
	
	for p in people:
		
		string += Person.convert(p) + "\n\n"

		if p.message_count > max_message_count:
			max_message_count = p.message_count
			max_message_count_person = p.name
		
		if p.message_count < min_message_count:
			min_message_count = p.message_count
			min_message_count_person = p.name

	string += "Total messages in chat: " + str(message_count)
	string += "\n\nMost messages: " + str(max_message_count)
	string += "\nPercent of total: " + str(round(max_message_count/float(message_count)*100,2)) + "%"
	string += "\nBy: " + max_message_count_person + "\n"
	string += "\nLeast messages: " + str(min_message_count)
	string += "\nPercent of total: " + str(round(min_message_count/float(message_count)*100,2)) + "%"
	string += "\nBy: " + min_message_count_person + "\n"

	return string

def get_word_count(message):
	words = re.split(r'[^0-9A-Za-z]+', message)

	return len(words)


def get_global_common_words():
	ordered_global_dict = collections.OrderedDict(sorted(global_dict.items(), key=lambda t: t[1], reverse=True))
	if len(ordered_global_dict)>= 1:
		string = "\nMost common word in Chat: " + str(list(ordered_global_dict.items())[0][0])
		string += "\n\tSaid " + str(list(ordered_global_dict.items())[0][1]) + " times"
	if len(ordered_global_dict)>= 2:
		string += "\nSecond most common word in Chat:  " + str(list(ordered_global_dict.items())[1][0])
		string += "\n\tSaid " + str(list(ordered_global_dict.items())[1][1]) + " times"
	if len(ordered_global_dict)>= 3:
		string += "\nThird most common word in Chat:  " + str(list(ordered_global_dict.items())[2][0])
		string += "\n\tSaid " + str(list(ordered_global_dict.items())[2][1]) + " times"
	else:
		string = "\nNo Global common words found"
	return string

def print_results():
	
	string = get_min_max()
	
	string += "\nMost Negative Message: " + str(most_negative_message).rstrip()
	string += "\nPolarity: " + str(most_negative_polarity)
	string += "\nBy: " + most_negative_message_person + "\n"
	string += "\nMost Positive Message: " + str(most_positive_message).rstrip()
	string += "\nPolarity: " + str(most_positive_polarity)
	string += "\nBy: " + most_positive_message_person + "\n"
	string += "\nLongest Message length (characters): " + str(longest_message_length)
	string += "\nLongest Message: " + str(longest_message).rstrip()
	string += "\nBy: " + longest_message_person + "\n"
	string += "\nShortest Message length (characters): " + str(shortest_message_length)
	string += "\nShortest Message: " + str(shortest_message).rstrip()
	string += "\nBy: " + shortest_message_person + "\n\n"

	string += get_global_common_words()

	print(string)
	write_file(string)

if len(sys.argv) == 2:
	filename = sys.argv[1]
	stopwords_filename = "stopwords.txt"
	bot(filename, stopwords_filename)

elif len(sys.argv) == 3:
	filename = sys.argv[1]
	stopwords_filename = sys.argv[2]
	bot(filename, stopwords_filename)
	
else:
	print("Usage: python whatsapp_stats.py <filename> [<stopwords_filename>]")