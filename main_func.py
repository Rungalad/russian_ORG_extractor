# import file with ORG key words
key_words_path = r'<your adress>\ORG_key_words.pkl'
ff = open(key_words_path, 'rb')
key_words = pickle.load(ff)
ff.close()

# You olso can add a key word to your dictioanry
def AddWordToKeys(path_voc, words):
    words = [i for i in words if i]
    ff = open(path_voc, 'rb')
    key_words = pickle.load(ff)
    ff.close()
    key_words = key_words + list(set(words +  [''.join([list(i)[0].upper()] + list(i)[1:]) for i in words]))
    key_words = list(set(key_words))
    ff = open(path_voc, 'wb')
    pickle.dump(key_words, ff)
    ff.close()
    
AddWordToKeys(r'<your adress>\ORG_key_words.pkl', ['НПО', ])


def OE(sent0, key_words = key_words):
    sent = ' ' + sent0.replace('\n', ' ') + ' '
    no_list = ['настоящее', 'время', 'должность']
    # Добавь еще город типа <г. Курган и др>
    #Добавим название в кавычках
    in_brakets = "[«\'\"].{5,}[»\'\"]"
    reg_brakets = re.compile(in_brakets)
    WW = reg_brakets.findall(sent)
    v_in_brakets = [[sent.index(i), sent.index(i)+len(i), i] for i in reg_brakets.findall(sent)]
    if v_in_brakets: sent = sent[:v_in_brakets[0][0]] + '*'*len(v_in_brakets[0][2]) + sent[v_in_brakets[0][1]:]
    
    #print(sent) # Разберемся с встречаемостью шаблона <им. X.X. Иванова> и обозначим его положение в тексте
    in_name = "им[.]?[ ]?\w{1}[.][ ]?\w{1}[.][ ]?\w+"
    reg_in_name = re.compile(in_name)
    VV = reg_in_name.findall(sent)
    v_in_name = [[sent.index(i), sent.index(i)+len(i), i] for i in reg_in_name.findall(sent)]
    if v_in_name: sent = sent[:v_in_name[0][0]] + '*'*len(v_in_name[0][2]) + sent[v_in_name[0][1]:]
    #print(sent)
    
    # Подрузим основные слова обозначающие шаблоны организаций и создадим регулярное выражение ищем шаблоны в тексте
    key_w1 = [''.join([list(i)[0].upper()] + list(i)[1:]) for i in key_words]
    key_words = list(set(key_words + key_w1))
    #print(key_words)
    reg_1 = re.compile('[ :,.)»]|[ :,.(«]'.join(key_words))
    v_1 = [i for i in reg_1.findall(sent)]
    v_1_1 = [i.strip().replace(':', '').replace(',', '').replace('.', '') for i in v_1]
    v_1_2 = [[sent.index(i), sent.index(i) + len(i), i] for i in v_1_1]
    #print(v_1_2)
    
    # Выделим все слова из текста а также пунктуацию которая может пригодиться
    #pm1 = pm.MorphAnalyzer() # Пока не будем использовать частеречный анализ - это сильно замедляет
    reg0 = re.compile('\w+|[,.\'\"«»]')
    
    # Случай одного совпадения с шаблоном
    if len(v_1_2)==1:
        # Разбиваем оставшееся предложения на 2 части - до и после найденного ключевого слова
        s0 = [i for i in reg0.findall(sent[:v_1_2[0][0]])] #str(pm1.parse(i)[0].tag)[:4]
        # Считаем слова после последнего знака пунктуации в левом предложении относящимися к организации        
        cnt1 = 0; puncts = []
        for word in s0:
            #if (str(pm1.parse(word)[0].tag)[:4] != 'ADJF'): continue
            cnt1 = cnt1 + 1
            if word in ',.:': puncts = puncts + [cnt1]
        if puncts: s0 = s0[max(puncts):] # Нам по смыслу подходят слова следующие после точки до ключ слова
        #s0 = [wo for wo in s0 if (str(pm1.parse(wo)[0].tag)[:4]) == 'ADJF' or (str(pm1.parse(wo)[0].tag)[:4] == 'NOUN')]
        # все последующие слова должны быть с заглавной буквы  и не быть цифрами
        s0 = [j for j in s0[-4:] if (list(j)[0].upper() == list(j)[0]) and (not j.isnumeric())]
        
        # Для правого предложения все слова до первого знака препинания
        s1 = []
        for word in  reg0.findall(sent[v_1_2[0][1]:]):
            if (word in '.,:'): break
            s1 = s1 + [word]#str(pm1.parse(word)[0].tag)[:4]
        s1 = s1[:2] # Ограничим количество слов в предложении справа
        s1 = [j for j in s1 if list(j)[0].upper() == list(j)[0]] # все последующие слова должны быть с заглавной буквы
        r = [s0 + [v_1_2[0][2]] + s1][0] # Объединим все полученные данные
        return [' '.join(r)] + v_in_brakets + v_in_name 
    
    # Случай 2 и более совпадений с шаблонами (более редкий случай) 3 - это уже ошибка
    if (len(v_1_2)==2) and (v_1_2[0][2] != v_1_2[1][2]):
        # Для данного случая поступим проще, просто объединим все слова между найденными шаблонами
        # т.к. работаем со строками то сильного диссонанса это не вызовет
        r = ''
        for i in range(len(v_1_2)):
            if i==len(v_1_2)-1:
                r = r + sent0[v_1_2[i][0]: v_1_2[i][1]-1]; continue #-1 опционально - дрочь
            r = r + sent0[v_1_2[i][0]-1: v_1_2[i][1]] + sent0[v_1_2[i][1]: v_1_2[i+1][0]]
        return [r] + v_in_brakets + v_in_name
    
    # Случай когда более 2 шаблонов в строке или шаблоны совпадающие
    if (len(v_1_2)>2): return v_in_brakets + v_in_name
    
    # На случай если не нашлось установленных шаблонов в тексте поищем аббревиатуры, в CV они чаще обозначают организации
    if not v_1_2:
        return v_in_brakets + v_in_name
        #reg_in_name = re.compile("[ :,.(«][А-Я]{3,7}[ :,.)»]")
        #v_1_2 = [i.strip().replace('.', '').replace(',','').replace(':','')
        #         for i in reg_in_name.findall(sent0.replace('\n', ' '))]
        #return list(set(v_1_2)) + v_in_brakets + v_in_name
    if not v_1_2: pass # Тут можно прорабоать еще вариант с кавычками
    
    return v_in_brakets + v_in_name

# Final restruct for output
def FinObr(RES):
    res = ''
    for i in RES:
        #print(type(i))
        if (type(i)==type([])) and (i[2] not in res):
            res = res + ' ' + i[2]
        elif type(i)==type('a'): res = res + i
        else: pass
    return res
    
# test
# OE('ООО Учебно-Методический Центр «Маяк»: Практический курс работы в программе «1С: Зарплата и Управление персоналом 8»')
# result
# ['ООО Учебно-Методический Центр',
# [31,
#  116,
#  '«Маяк»: Практический курс работы в программе «1С: Зарплата и Управление персоналом 8»']]
