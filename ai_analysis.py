
import pandas as pd
import numpy as np
import re
import pickle

# plotting
import seaborn as sns
import matplotlib.pyplot as plt

# Tune learning_rate
from numpy import loadtxt
from xgboost import XGBClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import StratifiedKFold

# First XGBoost model for MBTI dataset
from numpy import loadtxt
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

##### Compute list of subject with Type | list of comments 
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.corpus import stopwords 
from nltk import word_tokenize

import nltk
nltk.download('wordnet')

from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.manifold import TSNE


#타입을 숫자로 변환

def get_types(row):
    t=row['type']

    I = 0; N = 0
    T = 0; J = 0
    
    if t[0] == 'I': I = 1
    elif t[0] == 'E': I = 0
    else: print('I-E incorrect')
        
    if t[1] == 'N': N = 1
    elif t[1] == 'S': N = 0
    else: print('N-S incorrect')
        
    if t[2] == 'T': T = 1
    elif t[2] == 'F': T = 0
    else: print('T-F incorrect')
        
    if t[3] == 'J': J = 1
    elif t[3] == 'P': J = 0
    else: print('J-P incorrect')
    return pd.Series( {'IE':I, 'NS':N , 'TF': T, 'JP': J })


#딕셔너리파일 설정
b_Pers = {'I':0, 'E':1, 'N':0, 'S':1, 'F':0, 'T':1, 'J':0, 'P':1}

#리스트를 두개씩 묶어서 리스트로 만듬
b_Pers_list = [{0:'I', 1:'E'}, {0:'N', 1:'S'}, {0:'F', 1:'T'}, {0:'J', 1:'P'}]



def translate_personality(personality):
    # transform mbti to binary vector
    
    return [b_Pers[l] for l in personality]



def translate_back(personality):
    # transform binary vector to mbti personality
    
    s = ""
    for i, l in enumerate(personality):
        s += b_Pers_list[i][l]
    return s

# We want to remove these from the psosts
unique_type_list = ['INFJ', 'ENTP', 'INTP', 'INTJ', 'ENTJ', 'ENFJ', 'INFP', 'ENFP',
    'ISFP', 'ISTP', 'ISFJ', 'ISTJ', 'ESTP', 'ESFP', 'ESTJ', 'ESFJ']

unique_type_list = [x.lower() for x in unique_type_list]

# Lemmatize
stemmer = PorterStemmer()
lemmatiser = WordNetLemmatizer()

# Cache the stop words for speed 
cachedStopWords = stopwords.words("english")

def pre_process_data(data, remove_stop_words=True, remove_mbti_profiles=True):

    list_personality = []
    list_posts = []
    len_data = len(data)
    i=0
    
    for row in data.iterrows():
        i+=1
        if (i % 500 == 0 or i == 1 or i == len_data):
            print("%s of %s rows" % (i, len_data))

        ##### Remove and clean comments
        posts = row[1].posts
        temp = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', ' ', posts)
        temp = re.sub("[^a-zA-Z]", " ", temp)
        temp = re.sub(' +', ' ', temp).lower()
        if remove_stop_words:
            temp = " ".join([lemmatiser.lemmatize(w) for w in temp.split(' ') if w not in cachedStopWords])
        else:
            temp = " ".join([lemmatiser.lemmatize(w) for w in temp.split(' ')])
            
        if remove_mbti_profiles:
            for t in unique_type_list:
                temp = temp.replace(t,"")

        type_labelized = translate_personality(row[1].type)
        list_personality.append(type_labelized)
        list_posts.append(temp)

    list_posts = np.array(list_posts)
    list_personality = np.array(list_personality)
    return list_posts, list_personality


# read data
# data = pd.read_csv('/Users/jongphilkim/Desktop/Django_WEB/essayfitaiproject_2020_12_09/essayai/mbti_1.csv') 
data = pd.read_csv('./mbti/mbti_1.csv') 

# get_types 함수 적용
data = data.join(data.apply (lambda row: get_types (row),axis=1))

# load
with open('./mbti/list_posts.pickle', 'rb') as f:
    list_posts = pickle.load(f)

# load
with open('./mbti/list_personality.pickle', 'rb') as f:
    list_personality = pickle.load(f)


# # Posts to a matrix of token counts
cntizer = CountVectorizer(analyzer="word", 
                            max_features=1500, 
                            tokenizer=None,    
                            preprocessor=None, 
                            stop_words=None,  
                            max_df=0.7,
                            min_df=0.1) 

# Learn the vocabulary dictionary and return term-document matrix
print("CountVectorizer...")
X_cnt = cntizer.fit_transform(list_posts)


#################################################
#save!!! model X_cnt
import pickle
# save
# with open('./essayai/ai_character/mbti/data_X_cnt.pickle', 'wb') as f:
#     pickle.dump(X_cnt, f, pickle.HIGHEST_PROTOCOL)


# load
with open('./mbti/data_X_cnt.pickle', 'rb') as f:
    X_cnt = pickle.load(f)

#################################################

# Transform the count matrix to a normalized tf or tf-idf representation
tfizer = TfidfTransformer()

print("Tf-idf...")
# Learn the idf vector (fit) and transform a count matrix to a tf-idf representation
X_tfidf =  tfizer.fit_transform(X_cnt).toarray()

# load
with open('./mbti/data.pickle', 'rb') as f:
    X_tfidf = pickle.load(f)

def mbti_classify(text):
    
    type_indicators = [ "IE: Introversion (I) / Extroversion (E)", "NS: Intuition (N) – Sensing (S)", 
                    "FT: Feeling (F) - Thinking (T)", "JP: Judging (J) – Perceiving (P)"  ]


    # Posts in tf-idf representation
    X = X_tfidf




    my_posts = str(text)

    # The type is just a dummy so that the data prep fucntion can be reused
    mydata = pd.DataFrame(data={'type': ['INFJ'], 'posts': [my_posts]})

    my_posts, dummy  = pre_process_data(mydata, remove_stop_words=True)

    my_X_cnt = cntizer.transform(my_posts)
    my_X_tfidf =  tfizer.transform(my_X_cnt).toarray()

    # setup parameters for xgboost
    param = {}
    param['n_estimators'] = 200
    param['max_depth'] = 2
    param['nthread'] = 8
    param['learning_rate'] = 0.2

    result = []
    # Let's train type indicator individually
    for l in range(len(type_indicators)):
        print("%s ..." % (type_indicators[l]))

        Y = list_personality[:,l]

        # split data into train and test sets
        seed = 7
        test_size = 0.33
        X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=test_size, random_state=seed)

        # fit model on training data
        model = XGBClassifier(**param)
        model.fit(X_train, y_train)

        # make predictions for my  data
        y_pred = model.predict(my_X_tfidf)
        result.append(y_pred[0])
        # print("* %s prediction: %s" % (type_indicators[l], y_pred))

        print("The result is: ", translate_back(result))

        #결과를 리스트에 담고
        Result_list = list(translate_back(result))



    #mbit 결과값에 따라 내용 print 하기
    # read data
    # data = pd.read_csv('/Users/jongphilkim/Desktop/Django_WEB/essayfitaiproject/essayai/mbti_exp.csv') 
    data = pd.read_csv('./mbti/mbti_exp.csv') 

    #새로운 데이터프레임을 만들어서 계산된 값을 추가할 예정
    df2 = pd.DataFrame(index=range(0,4),columns=['Type', 'Explain'])

    #리스트에서 한글자씩 불러와서 데이터프레임의 값을 출력하면 됨
    for i in range(0, len(Result_list)):
        type = Result_list[i]

        for j in range(0, len(data)):   
            if type == data.iloc[j,0]:
                break

        is_mbti = data.iloc[j,2]

        df2.iloc[i, [0,1]] = [type, is_mbti]    
        print(df2)


    return df2


# my_posts  = """Describe a place or environment where you are perfectly content. What do you do or experience there, and why is it meaningful to you? 644 words out of 650 Gettysburg, a small town in the middle of Pennsylvania, was the sight of the largest, bloodiest battle in the Civil War. Something about these hallowed grounds draws me back every year for a three day camping trip with my family over Labor Day weekend. Every year, once school starts, I count the days until I take that three and half hour drive from Pittsburgh to Gettysburg. Each year, we leave after school ends on Friday and arrive in Gettysburg with just enough daylight to pitch the tents and cook up a quick dinner on the campfire. As more of the extended family arrives, we circle around the campfire and find out what is new with everyone. The following morning, everyone is up by nine and helping to make breakfast which is our best meal of the day while camping. Breakfast will fuel us for the day as we hike the vast battlefields. My Uncle Mark, my twin brother, Andrew, and I like to take charge of the family tour since we have the most passion and knowledge about the battle. I have learned so much from the stories Mark tells us while walking on the tours. Through my own research during these last couple of trips, I did some of the explaining about the events that occurred during the battle 150 years ago. My fondest experience during one trip was when we decided to go off of the main path to find a carving in a rock from a soldier during the battle. Mark had read about the carving in one of his books about Gettysburg, and we were determined to locate it. After almost an hour of scanning rocks in the area, we finally found it with just enough daylight to read what it said. After a long day of exploring the battlefield, we went back to the campsite for some 'civil war' stew. There is nothing special about the stew, just meat, vegetables and gravy, but for whatever reason, it is some of the best stew I have ever eaten. For the rest of the night, we enjoy the company of our extended family. My cousins, my brother and I listen to the stories from Mark and his friends experiences' in the military. After the parents have gone to bed, we stay up talking with each other, inching closer and closer to the fire as it gets colder. Finally, we creep back into our tents, trying to be as quiet as possible to not wake our parents. The next morning we awake red-eyed from the lack of sleep and cook up another fantastic breakfast. Unfortunately, after breakfast we have to pack up and head back to Pittsburgh. It will be another year until I visit Gettysburg again. There is something about that time I spend in Gettysburg that keeps me coming back to visit. For one, it is just a fun, relaxing time I get to spend with my family. This trip also fulfills my love for the outdoors. From sitting by the campfire and falling asleep to the chirp of the crickets, that is my definition of a perfect weekend. Gettysburg is also an interesting place to go for Civil War buffs like me. While walking down the Union line or walking Pickett's Charge, I imagine how the battle would have been played out around me. Every year when I visit Gettysburg, I learn more facts and stories about the battle, soldiers and generally about the Civil War. While I am in Gettysburg, I am perfectly content, passionate about the history and just enjoying the great outdoors with my family. This drive to learn goes beyond just my passion for history but applies to all of the math, science and business classes I have taken and clubs I am involved in at school. Every day, I am genuinely excited to learn.
# """
# test = mbti_classify(my_posts)
# print ('check') 
# test
# print ('check2') 