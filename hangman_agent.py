# import json
# import requests
# import random
# import string
# import secrets
# import time

import re

import collections


# try:
#     from urllib.parse import parse_qs, urlencode, urlparse
# except ImportError:
#     from urlparse import parse_qs, urlparse
#     from urllib import urlencode

# from requests.packages.urllib3.exceptions import InsecureRequestWarning

# requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

import numpy as np

class HangmanAPI(object):
    def __init__(self):
        # self.hangman_url = self.determine_hangman_url()
        # self.access_token = access_token
        # self.session = session or requests.Session()
        # self.timeout = timeout
        self.guessed_letters = []
        self.wrongly_guessed_letters = []
        
        full_dictionary_location = "words_250000_train.txt"
        self.full_dictionary = self.build_dictionary(full_dictionary_location)        
        self.full_dictionary_common_letter_sorted = collections.Counter("".join(self.full_dictionary)).most_common()
        self.count_table = np.load("Count_Table.npy")
        self.current_dictionary = []
        
    # @staticmethod
    # def determine_hangman_url():
    #     links = ['https://trexsim.com', 'https://sg.trexsim.com']

    #     data = {link: 0 for link in links}

    #     for link in links:

    #         requests.get(link)

    #         for i in range(10):
    #             s = time.time()
    #             requests.get(link)
    #             data[link] = time.time() - s

    #     link = sorted(data.items(), key=lambda x: x[1])[0][0]
    #     link += '/trexsim/hangman'
    #     return link
    
    def does_not_contain(self, dict_word):
        flag = True
        for ch in self.wrongly_guessed_letters:
            for ch_d in dict_word:
                if ch_d==ch:
                    flag = False
        return flag 
    
    def parse_solve(self,word):
        word = word[::2].replace("_","}")
        score = np.zeros((26))  
        
        n = len(word)

        for j in range(1,n):
            
            # Make string
            ch1 = 26
            ch2 = ord(word[j-1]) - ord('a')
            ch3 = ord(word[j]) - ord('a')
            ch4 = 27
            if j!=1:
                ch1 = ord(word[j-2]) - ord('a')
            if j!=n-1:
                ch4 = ord(word[j+1]) - ord('a')
                
            word1 = np.array([ch1,ch2,ch3,ch4])
               
            count_blank = 0
            for ix1 in range(4):
                if word1[ix1] == 28:
                    count_blank+=1
            
            if count_blank>0:
                distr = self.count_table[ch1][ch2][ch3][ch4]
                score+=distr
            
        ix_max = -1
        found = False
        visited = np.zeros((26))
        for ix in range(26):
            if visited[ix]==0 and (chr(ord('a')+ix) in self.guessed_letters)==False:
                if found==False:
                    ix_max = ix
                    found = True
                else:
                    if score[ix_max] < score[ix]:
                        ix_max = ix
        
        return chr(ord('a')+ix_max) 

    def guess(self, word): # word input example: "_ p p _ e "
        ###############################################
        # Replace with your own "guess" function here #
        ###############################################

        clean_word = word[::2].replace("_",".")
        len_word = len(clean_word)
        
        count = 0
        for ch in clean_word:
            if ch==".":
                count+=1
        
        guess_letter = '!'
        
        # Dict Solve
        current_dictionary = self.current_dictionary
        new_dictionary = []
        
        for dict_word in current_dictionary:
            # Removed length checker since template word could be a subset of some very big word
            
            match_list = re.findall(clean_word, dict_word)
            for match_word in match_list:
                if self.does_not_contain(match_word):
                    new_dictionary.append(match_word)
            

        self.current_dictionary = new_dictionary
        
        full_dict_string = "".join(new_dictionary)
        
        c = collections.Counter(full_dict_string)
        sorted_letter_count = c.most_common()                   
        
        
        for letter,instance_count in sorted_letter_count:
            if letter not in self.guessed_letters:
                guess_letter = letter
                break
            
        # if no word matches in training dictionary, use parse solving by frequency table
        if guess_letter == '!':
            guess_letter = self.parse_solve(word)
        
        return guess_letter 

    ##########################################################
    # You'll likely not need to modify any of the code below #
    ##########################################################
    
    def build_dictionary(self, dictionary_file_location):
        text_file = open(dictionary_file_location,"r")
        full_dictionary = text_file.read().splitlines()
        text_file.close()
        return full_dictionary

    def reset(self):
        self.guessed_letters = []
        self.wrongly_guessed_letters = []
        self.current_dictionary = self.full_dictionary

    def upd(self, prev_let, was_correct):
       self.guessed_letters.append(prev_let)
       if was_correct==False:
           self.wrongly_guessed_letters.append(prev_let)

    # def start_game(self, practice=True, verbose=True):
        
    #     self.guessed_letters = []
    #     self.wrongly_guessed_letters = []
    #     self.current_dictionary = self.full_dictionary
                         
    #     response = self.request("/new_game", {"practice":practice})
    #     if response.get('status')=="approved":
    #         game_id = response.get('game_id')
    #         word = response.get('word')
    #         tries_remains = response.get('tries_remains')
    #         if verbose:
    #             print("Successfully start a new game! Game ID: {0}. # of tries remaining: {1}. Word: {2}.".format(game_id, tries_remains, word))
    #         while tries_remains>0:
    #             guess_letter = self.guess(word)
    #             self.guessed_letters.append(guess_letter)
    #             if verbose:
    #                 print("Guessing letter: {0}".format(guess_letter))
                    
    #             try:    
    #                 res = self.request("/guess_letter", {"request":"guess_letter", "game_id":game_id, "letter":guess_letter})
    #             except HangmanAPIError:
    #                 print('HangmanAPIError exception caught on request.')
    #                 continue
    #             except Exception as e:
    #                 print('Other exception caught on request.')
    #                 raise e

    #             # Checking for wrongly guessed letters
    #             prev_tries = tries_remains   
    #             tries_remains = res.get('tries_remains')
    #             if tries_remains!=prev_tries:
    #                 self.wrongly_guessed_letters.append(guess_letter)
                
    #             if verbose:
    #                 print("Sever response: {0}".format(res))
    #             status = res.get('status')
                
    #             if status=="success":
    #                 if verbose:
    #                     print("Successfully finished game: {0}".format(game_id))
    #                 return True
    #             elif status=="failed":
    #                 reason = res.get('reason', '# of tries exceeded!')
    #                 if verbose:
    #                     print("Failed game: {0}. Because of: {1}".format(game_id, reason))
    #                 return False
    #             elif status=="ongoing":
    #                 word = res.get('word')
    #     else:
    #         if verbose:
    #             print("Failed to start a new game")
    #     return status=="success"
        
#     def my_status(self):
#         return self.request("/my_status", {})
    
#     def request(
#             self, path, args=None, post_args=None, method=None):
#         if args is None:
#             args = dict()
#         if post_args is not None:
#             method = "POST"

#         if self.access_token:
#             if post_args and "access_token" not in post_args:
#                 post_args["access_token"] = self.access_token
#             elif "access_token" not in args:
#                 args["access_token"] = self.access_token

#         time.sleep(0.2)

#         num_retry, time_sleep = 50, 2
#         for it in range(num_retry):
#             try:
#                 response = self.session.request(
#                     method or "GET",
#                     self.hangman_url + path,
#                     timeout=self.timeout,
#                     params=args,
#                     data=post_args,
#                     verify=False
#                 )
#                 break
#             except requests.HTTPError as e:
#                 response = json.loads(e.read())
#                 raise HangmanAPIError(response)
#             except requests.exceptions.SSLError as e:
#                 if it + 1 == num_retry:
#                     raise
#                 time.sleep(time_sleep)

#         headers = response.headers
#         if 'json' in headers['content-type']:
#             result = response.json()
#         elif "access_token" in parse_qs(response.text):
#             query_str = parse_qs(response.text)
#             if "access_token" in query_str:
#                 result = {"access_token": query_str["access_token"][0]}
#                 if "expires" in query_str:
#                     result["expires"] = query_str["expires"][0]
#             else:
#                 raise HangmanAPIError(response.json())
#         else:
#             raise HangmanAPIError('Maintype was not text, or querystring')

#         if result and isinstance(result, dict) and result.get("error"):
#             raise HangmanAPIError(result)
#         return result
    
# # class HangmanAPIError(Exception):
# #     def __init__(self, result):
# #         self.result = result
# #         self.code = None
# #         try:
# #             self.type = result["error_code"]
# #         except (KeyError, TypeError):
# #             self.type = ""

# #         try:
# #             self.message = result["error_description"]
# #         except (KeyError, TypeError):
# #             try:
# #                 self.message = result["error"]["message"]
# #                 self.code = result["error"].get("code")
# #                 if not self.type:
# #                     self.type = result["error"].get("type", "")
# #             except (KeyError, TypeError):
# #                 try:
# #                     self.message = result["error_msg"]
# #                 except (KeyError, TypeError):
# #                     self.message = result

# #         Exception.__init__(self, self.message)