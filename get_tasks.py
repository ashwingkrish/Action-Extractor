import spacy
from spacy.symbols import dobj, xcomp, conj, VERB
# from nltk.tokenize import sent_tokenize
import time
import json

import os
from datetime import datetime
import random

def GetTasks(text):
	doc = nlp(text)
	# using the following logic:
	# start parsing tree from root. if item is a verb and has xcomp, go to the xcomp node
	# else if item is verb and has dobj, that is one action. If item is verb and has conjunction, go the the conjunction item
	# once you reach the noun, you have the action. If noun has conjunction, add another action with the verb but this noun
	final_json = []
	actions = []
	return get_actions(doc)

# function that gets actions in a sentence
def get_actions(sentence):
	i = 0
	actions = []
	acts = []
	while i < len(sentence):
		word = sentence[i]
		if word.pos == VERB:
			actions = evaluate_verb(word)
			if actions:
				flag = False
				for a in actions:
					s = ''
					if a[0]:
						s = a[0].text
						if a[0].i > i+1:
							flag = True
							i = a[0].i
					if a[1]:
						s += ' '+a[1].text
						if a[1].i > i+1:
							i = a[1].i
							flag = True
					if s:
						acts.append(s)
				if not flag:
					i+=1
			else:
				i+=1
		else:
			i+=1
	print("Actions found are: ", actions)
	return acts

def evaluate_verb(word):
	actions = []
	# get any xcomp verbs
	xcomp_items = [item for item in word.children if item.dep == xcomp]
	# sent index to that verb and break
	if len(xcomp_items) != 0:
		return actions

	# now this is a valid verb! find all the nouns associated with it
	verbs = get_verbs_with_verb(word)
	nouns = get_nouns_with_verb(word)

	if not nouns and not verbs:
		return [(word, '')]

	# if nouns are empty, all the nouns attached to the child verbs need to be attached
	if not nouns:
		nouns = get_nouns_with_verb(verbs[-1])
		if not nouns:
			for v in verbs:
				actions.append((v, ''))

		for n in nouns:
			for v in verbs:
				actions.append((v, n))

		return actions

	for n in nouns:
		actions.append((word, n))
	for v in verbs:
		actions.extend(evaluate_verb(v))
	return actions


# function that gets connected verbs, returns an array with a none type if found
def get_verbs_with_verb(verb):
	starting_verb = [possible_verb for possible_verb in verb.children if possible_verb.dep == conj and possible_verb.pos == VERB]
	print("Starting verbs are: ", starting_verb)
	if len(starting_verb) == 0:
		return starting_verb

	starting_verb.extend(get_verbs_with_verb(starting_verb[0]))
	return starting_verb

# function that gets nouns associated with a verb.
def get_nouns_with_verb(verb):
	starting_noun = [possible_noun for possible_noun in verb.children if possible_noun.dep == dobj]
	if len(starting_noun) == 0:
		return starting_noun

	starting_noun.extend(get_conj_nouns(starting_noun[0]))
	print("Starting nouns are: ", starting_noun)
	return starting_noun

# functions that return connected nouns
def get_conj_nouns(noun):
	next_noun = [possible_noun for possible_noun in noun.children if possible_noun.dep == conj]
	if len(next_noun) == 0:
		return next_noun
	next_noun.extend(get_conj_nouns(next_noun[0]))
	return next_noun



print("Enter the message: ")
s = input()

print("Tasks are: ")
print(s)