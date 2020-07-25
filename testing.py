from bs4 import BeautifulSoup as sp
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import re
import pandas as pd
import collections

factory = StemmerFactory()
stemmer = factory.create_stemmer()

list_berita =[]
list_berita_cat =[]

unique = []
unique_dict = {}

weight = []
weight_cat_dict = {}

with open("stopword2016.txt","r") as stopword: sword = stopword.read().splitlines()

def openFile():
    file = open("corpus_berita.txt", encoding="utf8")
    soup = sp(file,'html.parser')
    doc_berita = soup.find_all("doc")
    return doc_berita

def preprocessing(berita):
    cleaning_words = re.sub("\W+"," ", berita)
    clean = cleaning_words.lower()

    tokenize = re.findall("\w+", clean)
    token = " ".join(tokenize)
    return stemmer.stem(token)

def termUnik(term,stopword):
    kata = " ".join(term)
    token = kata.split(' ')
    for item in token:
        if item not in stopword:
            if item not in unique:
                unique.append(item)
    unique.sort()
    unique_dict['Kata_Unik']=unique
    return unique_dict,unique

def webCraw(berita):
    for item in berita:
        berita = item.find("berita").text
        cat = item.find("cat").text
        cat = preprocessing(cat)
        berita = preprocessing(berita)
        list_berita.append(berita)
        list_berita_cat.append([berita]+[cat])

def categorized(berita_cat):
    categorized = {}
    for item in berita_cat:
        if item[1] in categorized:
            old = categorized[item[1]]
            categorized.update({item[1]:old +" "+item[0]})
        else:
            categorized[item[1]] = item[0]

    for key in categorized:
        tokenize = categorized[key].split(' ')
        categorized[key]= tokenize

    return categorized


def termWeight(categori):
    for key in categori:
        # print(key)
        waight_temp = []
        tes = {}
        for i in range(len(unique)):
            score = 0
            for item in categori[key]:
                if unique[i] == item:
                    score += 1
            tes[unique[i]] = score
            waight_temp.append(score)
        weight_cat_dict[key] = tes
        weight.append(waight_temp)

start = openFile()
webCraw(start)

# print(list_berita)
# print(f"{list_berita_cat} \n")

termUnik(list_berita,sword)
categori = categorized(list_berita_cat)
termWeight(categori)

# print(unique)
# print(len(unique))

frame = pd.DataFrame(weight_cat_dict)



sum_weight={}
for item in weight_cat_dict:
    term_count = 0
    for val in weight_cat_dict[item]:
        term_count+=weight_cat_dict[item][val]
    sum_weight[item]= term_count

possible = {}

for key in weight_cat_dict:
    poss_term=0
    temp = {}
    for value in weight_cat_dict[key]:
        poss_term = weight_cat_dict[key][value]
        p_kata = (poss_term+1)/(sum_weight[key]+ len(unique))
        temp[value]=p_kata
    possible[f"P(w|{key})"]=temp


frame_poss = pd.DataFrame(possible)
print(frame_poss)


# print(weight)

# print(unique_dict)
# print(weight_cat_dict)
# print(f"\n {unique}")

# print(f"\n {categori}")

# datafra = pd.DataFrame(categori)
# print(datafra)

