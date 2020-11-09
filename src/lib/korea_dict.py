import os
import pandas as pd

path = "./doc/korea_dict/"
#targ_col_snme = '표제어' #우리말 기초사전
targ_col_snme = '어휘' #우리말샘 사전

# 초성 리스트. 00 ~ 18
CHOSUNG_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
# 중성 리스트. 00 ~ 20
JUNGSUNG_LIST = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']
# 종성 리스트. 00 ~ 27 + 1(1개 없음)
JONGSUNG_LIST = [' ', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

chosung_dict = {'ㄱ': 0, 'ㄲ': 1, 'ㄴ': 2, 'ㄷ': 3,  'ㄸ' : 4,'ㄹ': 5,'ㅁ': 6, 'ㅃ': 7, 'ㅂ': 8, 'ㅅ': 9, 'ㅆ': 10, 'ㅇ': 11,'ㅈ': 12, 'ㅉ': 13, 'ㅊ': 14,'ㅋ': 15, 'ㅌ': 16,'ㅍ': 17, 'ㅎ': 18}
dic_verb_list = [[]]

for i in range(len(CHOSUNG_LIST) - 1):
    dic_verb_list.append([])

'''************************************************
* @Function Name : pars_xml
************************************************'''
def get_chosung(verb):
    res_chosung = ''
    word = list(verb.strip())[0]
    if '가'<= word <='힣':
        ## 588개 마다 초성이 바뀜.
        ch1 = (ord(word) - ord('가')) // 588
        res_chosung = CHOSUNG_LIST[ch1]
    else:
        pass
    return res_chosung

'''************************************************
* @Function Name : pars_xml
************************************************'''
def gen_kr_dict():
    file_list = os.listdir(path)

    #판다스로 열 데이터 추출
    for dict_file in file_list:
        print("File - [%s] be processing" % dict_file)
        df = pd.read_excel(path + dict_file)
        dict_verb = df[targ_col_snme]

        for verb in dict_verb:
            verb = str(verb).replace('-','').replace('^','')

            if len(verb) != 1:
                chosung = get_chosung(verb)
                if chosung != '':
                    dic_verb_list[chosung_dict[chosung]].append(verb)
                else:
                    pass

    dir_path = './doc/db_dict/'
    if not os.path.isdir(dir_path):
        os.mkdir(dir_path)

    idx = 0
    for dict in dic_verb_list:
        f_nm = dir_path + str(idx) + '.txt'

        if os.path.isfile(f_nm):
            os.remove(f_nm)
            print("Existing DB have been deleted.")

        with open(f_nm, 'w', encoding="utf-8") as f:
            for word in dict:
                f.writelines(str(word) + '\n')
            dict.clear()
        f.close()
        idx += 1

        '''
        for verb in dict_verb:
            verb = str(verb).replace('-','').replace('^','')

            if len(verb) != 1:
                chosung = get_chosung(verb)
                if chosung != '':
                    dic_verb_list[chosung_dict[chosung]].append(verb)
                else:
                    pass
        '''
    return dic_verb_list


'''************************************************
* @Function Name : pars_xml
************************************************'''
def get_dict(word):
    mtch_dict = []
    chosung = get_chosung(word)
    if chosung != '':
        mtch_dict = dic_verb_list[chosung_dict[chosung]]
    else:
        pass

    return mtch_dict

def main():
    gen_kr_dict()

if __name__ == '__main__':
    main()