import nltk
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import pickle, os
import numpy as np
from tensorflow.keras.models import load_model
import  dbconfig, statistics
import json, random
from flask import Flask
from flaskext.mysql import MySQL
import matplotlib.pyplot as plt
import datetime, timeit



def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower() )for word in sentence_words]
    return sentence_words


def bow(sentence, words, show_details=True):
    sentence_words = clean_up_sentence(sentence)
    bag = [0]*len(words)  
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s: 
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)
    return(np.array(bag))



def predict_class(sentence, model, jsname):
    words = pickle.load(open('./words/'+jsname+'.pkl','rb'))
    p = bow(sentence, words, show_details=False)
    res = model.predict(np.array([p]))[0]
    if (jsname=='switch'):
        classes = pickle.load(open('./classes/'+jsname+'.pkl','rb'))
        retest = [[i,r] for i,r in enumerate(res)]
        retest.sort(key=lambda x: x[1], reverse=True)
        res_pvar = 0
        max_pvar = max(res)
        for r in res:
            res_pvar = res_pvar + (r-max_pvar)*(r-max_pvar)
        # x=[]
        # y=[]
        # for r in retest:
        #     y.append(classes[r[0]])
        #     x.append(r[1])
        # plt.plot(x,y,'go-')
        # plt.xlabel('Probability')
        # plt.ylabel('Subject')
        # plt.show()
        # print(res_pvar/len(res))
        return res_pvar/len(res), retest[0]
    else:
        classes = pickle.load(open('./classes/'+jsname+'.pkl','rb'))
        res_pvar = 0
        max_pvar = max(res)
        for r in res:
            res_pvar = res_pvar + (r-max_pvar)*(r-max_pvar)
        return res_pvar/len(res), res, classes
    
  
    
    

def takeelelist(lists, num):
    results = []
    count = 0
    for i in lists:
        results.append(i)
        count = count + 1
        if count == num:
            break
    return results


def getResponse(ints,jsnum,intents_json,res):
    app = Flask(__name__)
        

    if ints == None:
        return 'H??? th???ng kh??ng t??m th???y d??? li???u ph?? h???p ! B???n vui l??ng th??? l???i nh?? !'
    if jsnum == 0:
        for i in ints:
            if i['intent']=='10':
                return 'Chi ph?? s???a ch???a, thay th??? v???t t?? t??nh theo th???i gi??, vui l??ng truy c???p ktxbk.vn ????? bi???t th??m chi ti???t.'
            else:
                fee = ints[0]['intent']
                app = Flask(__name__)
                return dbconfig.findprice(fee,app)

    elif jsnum == 2:
        for i in ints:
            room = ints[0]['intent']
            app = Flask(__name__)
            return dbconfig.findroom(room,app)

    elif jsnum == 1:
        for i in ints:
            if (i['intent']=='greeting'):
                return '''Ch??o b???n ! M??nh l?? Chatbot h??? tr??? t?? v???n h???c t???p sinh vi??n ! M??nh c?? th??? gi??p g?? cho b???n ?'''
            elif (i['intent']=='goodbye'):
                return '''T???m bi???t b???n ! N???u c?? g?? th???c m???c, b???n c??? t??m ?????n Chatbot nh?? !'''
            elif (i['intent']=='thanks'):
                return '''Ch??ng t??i lu??n s???n s??ng gi???i ????p th???c m???c cho c???u !'''

    elif jsnum == 3:
        for i in ints:
            rule = ints[0]['intent']
            app = Flask(__name__)
            return dbconfig.findrule(rule,app)
        
                  
    elif jsnum ==4:
            for i in ints:
                staff = ints[0]['intent']
                app = Flask(__name__)
            return dbconfig.staffconfig(staff,app)
    else:
            return 'Hi???n t???i Bot ch??a hi???u y??u c???u c???a b???n! B???n vui l??ng th??? l???i nh??!'

#===================================================
def chatbot_response(msg):
    app = Flask(__name__)
    arr = os.listdir('./json file')
    arr_file_name = []
    for i in arr:
        arr_file_name.append(os.path.splitext(i)[0])
    model = load_model('./model h5/'+ 'switch' +'.h5')
    pvar, [js_num, js_prob] = predict_class(msg,model,'switch')
    print(pvar,"**********")
    if (pvar>0.5):
        jsname = arr_file_name[js_num]
        model = load_model('./model h5/'+ jsname +'.h5')
        pvar, res, classes =  predict_class(msg, model, jsname)
        print(jsname,pvar,js_prob)
        if (pvar>0.25):
            retest = [[i,r] for i,r in enumerate(res)]
            retest.sort(key=lambda x: x[1], reverse=True)
            for r in retest:
                print("intent: "+classes[r[0]]+" "+str(r[1]))
            ints = []
            for r in retest:
                ints.append({"intent": classes[r[0]], "probability": str(r[1])})
            answer = getResponse(ints,js_num,msg,res)
        else:
            answer = 'Hi???n t???i Bot ch??a hi???u y??u c???u c???a b???n! B???n c?? th??? xem th??m t???i web: ktx.vn !'
    else:
        answer = 'Hi???n t???i Bot ch??a hi???u y??u c???u c???a b???n! B???n vui l??ng th??? l???i nh??!'
    return answer, js_num