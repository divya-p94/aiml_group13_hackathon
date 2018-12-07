import os
import nltk
from nltk.stem.lancaster import LancasterStemmer
# word stemmer
stemmer = LancasterStemmer()

limit = 3

def ngrams(lines):
    global limit
    global ndict
    ngrams = []
    #Seema commented
    for i in range(1, limit+1):
        ndict = {}
        for line in lines:
            nline = ['<START>']*i + line + ['<END>']*i
            #print(nline)
            for x in range(len(nline)- i) :
                key = '_'.join(nline[x:x+i])
                #print('key')
                #print(key)
                if key in ndict.keys():
                    ndict[key] += 1
                else:
                    ndict[key] = 1
        ngrams += [ndict]
     #Seema commented till here
    return ngrams

def cleanLines(lines):
    for i in range(len(lines)):
        lines[i] = lines[i][:-1].split()
        for x in range(len(lines[i])):
            lines[i][x] = lines[i][x].lower()
    return lines

def score(uinput, tngramsdict):
    global limit
    scores = []
    uinput = [uinput.lower().split()]
    #print("uinput after split")
    #print(uinput)
    cur_ngramsdict = ngrams(uinput)
    #print("cur_ngramsdict after ngrams")
    #print(cur_ngramsdict)
    for key in tngramsdict:
        ngramsdict = tngramsdict[key]
        fscore = 0.0
        for i in range(len(cur_ngramsdict)):
            cur_dict = cur_ngramsdict[i]
            ansdict = ngramsdict[i]

            precision = 0
            for i in cur_dict.keys():
                if i in ansdict.keys():
                    precision+=1

            recall = 0
            for i in ansdict.keys():
                if i in cur_dict.keys():
                    recall+=1

            fscore += 1.0/float((len(ansdict.keys())/float(precision) + len(ansdict.keys())/float(recall)))
            
        scores+= [(key,fscore)]
        #print("key is")
        #print(key)
        #print(fscore)
    return scores

def stemmed_words(ngramsdict):
    # capture unique stemmed words in the training corpus
    global corpus_words
    global class_words
    corpus_words = {}
    class_words = {}
    # turn a list into a set (of unique items) and then a list again (this removes duplicates)
    classes = list(set([a['class'] for a in ngramsdict]))
    for c in classes:
        # prepare a list of words within each class
        class_words[c] = []

    # loop through each sentence in our training data
    for data in ngramsdict:
        # tokenize each sentence into words
        
        #print ("%s data" % data)
        #for word in nltk.word_tokenize(data['sentence']):
        for word in data['sentence']:
            # ignore a some things
            if word not in ["?", "'s","$"]:
                # stem and lowercase each word
                stemmed_word = stemmer.stem(word.lower())
                # have we not seen this word already?
                if stemmed_word not in corpus_words:
                    corpus_words[stemmed_word] = 1
                else:
                    corpus_words[stemmed_word] += 1

                # add the word to our words in class list
                class_words[data['class']].extend([stemmed_word])

    # we now have each stemmed word and the number of occurances of the word in our training corpus (the word's commonality)
    #print ("Corpus words and counts: %s \n" % corpus_words)
    # also we have all words in each class
    #print ("Class words: %s" % class_words)


# calculate a score for a given class
def calculate_class_score(sentence, class_name, show_details=True):
    score = 0
    uinput = [sentence.lower().split()]
    cur_ngramsdict = ngrams(uinput)
    #print("class name is")
    #print(class_name)
    
    # tokenize each word in our new sentence
    for word in nltk.word_tokenize(sentence):
        # check to see if the stem of the word is in any of our classes
        #if stemmer.stem(word.lower()) in cur_ngramsdict:
        #if stemmer.stem(word.lower()) in class_words[class_name]:
        if word.lower() in class_words[class_name]:
            # treat each word with same weight
            score += 1
            
            if show_details:
                print ("   match: %s" % stemmer.stem(word.lower() ))
    return score

# return the class with highest score for sentence
def classify(sentence):
    ngramsdict = init()
    high_class = None
    high_score = 0
    uinput = [sentence.lower().split()]
    cur_ngramsdict = ngrams(uinput)
    # loop through our classes
    #for c in ndict.keys():
    for c in class_words.keys():
        
        # calculate score of sentence for each class
        score = calculate_class_score(sentence, c)
        print("Score of class is ")
        print(c)
        print(score)
        # keep track of highest score
        if score > high_score:
            high_class = c
            high_score = score

    return high_score,c

def init():
    ngramsdict = {}
    path = './intents/'

    for fil in os.listdir(path):
        if fil.endswith('.dat'):
            with open(path + fil) as f:
                lines = f.readlines()
                lines = cleanLines(lines)
                ngramsdict[''.join(fil.split('.')[:-1])] = ngrams(lines)
    return ngramsdict

def init2():
    import re
    ngramsdict = []
    path = './intents/'

    for fil in os.listdir(path):
        if fil.endswith('.dat'):
            with open(path + fil) as f:
                lines = f.readlines()
                lines = cleanLines(lines)
                #ngramsdict[''.join(fil.split('.')[:-1])] = ngrams(lines)
                for j in lines:
                    ngramsdict.append({"class":re.sub('.dat', '', fil), "sentence":j})
    return ngramsdict

def ngrammatch(uinput):
    ngramsdict = init2()
    #print(ngramsdict)
    #scores = score(uinput, ngramsdict)
    #scores = calculate_class_score(uinput, ngramsdict)
    stemmed_words(ngramsdict)
    scores,h_class = classify(uinput)
    #print scores
    return scores,h_class



