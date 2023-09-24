import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
import os
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import cmudict
nltk.download('punkt')
nltk.download('cmudict')

df=pd.read_csv("path to dataset csv file containing website links")
ls=['POSITIVE SCORE','NEGATIVE SCORE','POLARITY SCORE','SUBJECTIVITY SCORE','AVG SENTENCE LENGTH','PERCENTAGE OF COMPLEX WORDS','FOG INDEX','AVG NUMBER OF WORDS PER SENTENCE','COMPLEX WORD COUNT','WORD COUNT','SYLLABLE PER WORD','PERSONAL PRONOUNS','AVG WORD LENGTH']
for l in ls:
    df[l] = ''

stop_words = set()
with open("path to stopwords text file", 'r') as f:
    stop_words.update(set(f.read().splitlines()))
positive_words = set()
with open("path to positive words text file", 'r') as f:
    positive_words.update(set(f.read().splitlines()))
negative_words = set()
with open("path to negative words text file", 'r') as f:
    negative_words.update(set(f.read().splitlines()))

pronouncing_dict = cmudict.dict()

for i in range(114):  #number of data points
    url=df.iloc[i,1]
    try:
        response = requests.get(url)   # to retrieve data from a specified URL
    except:
        print("can't get response of {}".format(df.iloc[i,0]))
    try:
        soup = BeautifulSoup(response.content, 'html.parser')     #to to parse the HTML content of an HTTP response
    except:
        print("can't get page of {}".format(df.iloc[i,0]))
    try:
        title = soup.find('h1').get_text()                #to extract the heading of the article
    except:
        print("can't get title of {}".format(df.iloc[i,0]))
    article = ""
    try:
        for p in soup.find_all('p'):                     #to get the contents in the paragraph tag
            article += p.get_text()
    except:
        print("can't get text of {}".format(df.iloc[i,0]))

    # article=article[919:-394]     #this is optional if we want to remove some part of extracted text
                                
    file_path = "path to file where to save the extracted text"+str(df.iloc[0,0])+".txt"
    with open(file_path, 'a') as file:
        file.write(title)
        file.write(article)

    words = word_tokenize(article)
    filtered_article = [word for word in words if word not in stop_words]
    positive_score=0
    negative_score=0
    for word in filtered_article:
        if word in positive_words:
            positive_score=positive_score+1
    for word in filtered_article:
        if word in negative_words:
            negative_score=negative_score+1
    polarity_score=(positive_score - negative_score) / ((positive_score + negative_score) + 0.000001)
    subjectivity_score=(positive_score + negative_score) / ((len(filtered_article)) + 0.000001)

    def count_syllables(word):
        word = word.lower()
        if word in pronouncing_dict:
            return max([len(list(y for y in x if y[-1].isdigit())) for x in pronouncing_dict[word]])
        else:
            return 1
        
    avg_sen_len=len(words)/len(article.split('.'))

    complex_word_count=0
    for word in words:
        if (count_syllables(word)>2):
            complex_word_count=complex_word_count+1
    prcnt_cmplx_word=complex_word_count/len(words)

    fog_index=0.4*(avg_sen_len + prcnt_cmplx_word)

    AVG_NUMBER_OF_WORDS_PER_SENTENCE=avg_sen_len

    word_count=len(filtered_article)

    syllab_total=0
    for word in words:
        syllab_total=syllab_total+count_syllables(word)
    syllab_per_word=syllab_total/len(words)

    pattern = r'\b(I|we|my|ours|us)\b'
    matches = re.findall(pattern, article, flags=re.IGNORECASE)
    personal_pronouns=len(matches)

    total_word_len=0
    for word in words:
        total_word_len=total_word_len+len(word)
    avg_word_len=total_word_len/len(words)

    df.iloc[i,2]=positive_score
    df.iloc[i,3]=negative_score
    df.iloc[i,4]=polarity_score
    df.iloc[i,5]=subjectivity_score
    df.iloc[i,6]=avg_sen_len
    df.iloc[i,7]=prcnt_cmplx_word
    df.iloc[i,8]=fog_index
    df.iloc[i,9]=AVG_NUMBER_OF_WORDS_PER_SENTENCE
    df.iloc[i,10]=complex_word_count
    df.iloc[i,11]=word_count
    df.iloc[i,12]=syllab_per_word
    df.iloc[i,13]=personal_pronouns
    df.iloc[i,14]=avg_word_len

df