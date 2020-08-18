from bs4 import BeautifulSoup as sp
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import re
import json
import pandas as pd

factory = StemmerFactory()
stemmer = factory.create_stemmer()

subs2 = '\s *\w\. |\(|\)|:|, |\.\n|”|“|…|\.  |&|\*|\?|"|- | -'
subs3 ='\. |, |\/\n'
substwith= '\n+|\s +'

with open("stopword2016.txt","r") as stopword: stopword = stopword.read().splitlines()

def openFile(corpus):
    file = open(corpus, encoding="utf8")
    soup = sp(file,'html.parser')
    doc_berita = soup.find_all("doc")
    return doc_berita

def priorProbability(berita):
    categori_only = {}
    prior_proba ={}
    jumlah = 0
    for item in berita:
        cat = item.find('cat').text
        cat = preprocessing(cat)
        if cat:
            if cat in categori_only:
                categori_only[cat]+=1
            else:
                categori_only[cat]=1
    for item in categori_only:
        jumlah+=categori_only[item]
    for items in categori_only:
        prior_proba[items]=(categori_only[items]/jumlah)
    return prior_proba

def preprocessing(berita):
    cleaning_words = re.sub(subs2, " ", berita)
    cleaning_words = re.sub(subs3, " ", cleaning_words)
    cleaning_words = re.sub(substwith, " ", cleaning_words)
    clean = cleaning_words.lower()
    tokenize = clean.split()
    token = " ".join(tokenize)
    return stemmer.stem(token)

def webCraw(berita):
    list_berita = []
    list_berita_cat = []
    list_tidak_ada_cat = []
    for item in berita:
        berita = item.find("berita").text
        cat = item.find("cat").text
        if cat:
            cat = preprocessing(cat)
            berita = preprocessing(berita)
            list_berita.append(berita)
            list_berita_cat.append([berita] + [cat])
        else:
            list_tidak_ada_cat.append(berita)
    with open("list_berita.json", "w") as write_file:
        json.dump(list_berita, write_file)

    with open("list_berita_cat.json", "w") as write_file:
        json.dump(list_berita_cat, write_file)

    with open("list_tidak_ada_cat.json", "w") as write_file:
        json.dump(list_tidak_ada_cat, write_file)

def termUnik(list_berita,stopword):
    unique = []
    kata = " ".join(list_berita)
    token = kata.split(' ')
    for item in token:
        if item:
            if item not in stopword:
                if item not in unique:
                    unique.append(item)
    unique.sort()
    return unique

def dikategorikan(berita_cat):
    categorized = {}
    for item in berita_cat:
        if item[0] or item[1]:
            if item[1] in categorized:
                old = categorized[item[1]]
                categorized.update({item[1]:old +" "+item[0]})
            else:
                categorized[item[1]] = item[0]

    for key in categorized:
        tokenize = categorized[key].split(' ')
        categorized[key]= tokenize

    return categorized

def termWeight(categori,kata_unik):
    weight_cat_dict ={}
    for key in categori:
        # print(key)
        waight_temp = []
        tes = {}
        for i in range(len(kata_unik)):
            score = 0
            for item in categori[key]:
                if kata_unik[i] == item:
                    score += 1
            tes[kata_unik[i]] = score
            waight_temp.append(score)
        weight_cat_dict[key] = tes
    return weight_cat_dict

def conProba(weight_cat_dict,term_unik):
    sum_weight = {}
    possible = {}
    for item in weight_cat_dict:
        term_count = 0
        for val in weight_cat_dict[item]:
            term_count+=weight_cat_dict[item][val]
        sum_weight[item]= term_count

    for key in weight_cat_dict:
        poss_term=0
        temp = {}
        for value in weight_cat_dict[key]:
            poss_term = weight_cat_dict[key][value]
            p_kata = (poss_term+1)/(sum_weight[key]+ len(term_unik))
            temp[value]=p_kata
        possible[key]=temp
    return possible


#Ambil corpus berita yang akan diolah
corpus = "corpus.txt"

#Buka Corpus  dengan hanya mengambil isi dari tag <doc>
doc_corpus = openFile(corpus)
# print(doc_corpus)

#Hitung probabilitas setiap fitur
prior_proba = priorProbability(doc_corpus)
# print(f"\nprobabilitas setiap kategori:\n{prior_proba}\n")

#Mengambil berita dan kategori berita tersebut disimpan di array
#Hanya perlu di run sekali apabila tidak ada perubahan corpus
# webCraw(doc_corpus)


with open('list_berita_cat.json') as a:
  list_berita_cat = json.load(a)

with open('list_berita.json') as f:
  list_berita = json.load(f)

# print(list_berita_cat)

# Mencari kata unik dengan menghilangkan stopword
term_unik = termUnik(list_berita,stopword)
# print(f"banyak: {len(term_unik)}\n"
#       f"Term_unik: {term_unik}\n")

#Mengkategorikan berdasarkan kategori
dikategori = dikategorikan(list_berita_cat)
# print(f"Berdasar Kategori:\n{dikategori}\n")

#Menghitung Raw TF berdasarkan kata unik
term_weight_dict = termWeight(dikategori,term_unik)
# print(f"Bobot masing-masing kata RAW:\n{term_weight_dict}\n")
print(pd.DataFrame(term_weight_dict))

#Menghitung P(w|xi) setiap kategori
condisional_probability = conProba(term_weight_dict,term_unik)
print(f"\nPosterior:\n{pd.DataFrame(condisional_probability)}\n")





#fase Testing

text =''

tes_prepro = preprocessing(text)
# print(tes_prepro)
split = tes_prepro.split()
print(split)

tes_cek_term = []
for item in split:
    if item in term_unik:
        tes_cek_term.append(item)

print(tes_cek_term)

hasil_kelas = {}
for key in condisional_probability:
    value = {}
    for val in condisional_probability[key]:
        if val in tes_cek_term:
            value[val]=condisional_probability[key][val]
    hasil_kelas[key] = value

print(f"\nHasil Setelah Dicari consnya:\n{pd.DataFrame(hasil_kelas)}\n")

hasil_tes = {}
for key in hasil_kelas:
    count = 1
    hasil = 0
    for val in hasil_kelas[key]:
        count *= hasil_kelas[key][val]
    hasil = prior_proba[key] * count
    hasil_tes[key] = hasil

print(f"\nHasil Posterior masing masing:\n{hasil_tes}\n")

print(f"\nHasil Kategori :\n{max(hasil_tes,key=hasil_tes.get)}"
      f"\nDengan Nilai :\n{max(hasil_tes.values())}")