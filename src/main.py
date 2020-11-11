from urllib.request import urlopen
from zipfile import ZipFile
from io import BytesIO
from bs4 import BeautifulSoup

import lib.korea_dict as kd

stpwrd_path = './doc/stopword/stopword_dict.txt'
indwrd_path = './doc/indwrd/indwrd_dict.txt'
dict_list =[[]]
for i in range(len(kd.CHOSUNG_LIST) - 1):
    dict_list.append([])

'''************************************************
* @Function Name : get_co_rept
************************************************'''
def gt_co_rept():

    crtfc_key ="956243c104077738ebc3c93bd62c3e0c019eb877"

    #rcept_no = "20201111000101"     #파이오링크
    #rcept_no = "20201110000346"     #솔브레인홀딩스
    #rcept_no = "20200515001451"     #samsung
    #rcept_no = "20200515000890"    #seohan
    #rcept_no = '20200515001237'     #"shupigan"
    #rcept_no = '20200515001547'     #파루
    #rcept_no = '20200515002575'     #레고캠바이오
    rcept_no = '20200514000988'         #OCI

    home = "https://opendart.fss.or.kr/api/document.xml?crtfc_key="
    url = home + crtfc_key +  "&rcept_no=" + rcept_no
    resp = urlopen(url)

    with ZipFile(BytesIO(resp.read())) as zf:
        file_list = zf.namelist()

        while len(file_list) > 0:
            file_name = file_list.pop()
            co_rept = zf.open(file_name).read().decode('euc-kr')
            break

    soup = BeautifulSoup(co_rept, 'html.parser')
    str_xml = str(soup.prettify())
    str_list = str_xml.split('\n')

    with open('./co_oview.txt', 'w', encoding='utf-8') as f:
        for line in str_list:
            f.writelines(line + '\n')
    f.close()

    return str_list

'''************************************************
* @Function Name : extr_sect
************************************************'''
def extr_sect(xml_orgi):
    str_list = xml_orgi

    token_start = '<title aassocnote="D-0-2-0-0" atoc="Y">' # II. 사업의 내용
    token_end = '   <title aassocnote="D-0-3-0-0" atoc="Y">' # III. 재무에 관한 사항
    tkn_sect_strt = '<section-1 aclass="MANDATORY" apartsource="SOURCE">'

    stor_flag = False
    line_cnt = 0
    full_text = ''

    while(1):
        cur_line = str_list[line_cnt]
        nxt_line = str_list[line_cnt + 2]

        if '-="" <="" ' in cur_line:
            cur_line = cur_line.replace('-="" <="" ', '')

        #if '추<=""' in cur_line:
        if '<=' in cur_line:
            cur_line = cur_line.replace('<=', '=')
        else:
            pass

        if tkn_sect_strt in cur_line:
            if token_start in str_list[line_cnt + 1]:
                stor_flag = True

        elif stor_flag == True and (token_end in nxt_line):
            full_text = full_text + cur_line + '\n'
            break

        else:
            pass

        if stor_flag == True:
            full_text = full_text + cur_line + '\n'
        else:
            pass

        line_cnt = line_cnt + 1

    str_list.clear()
    return full_text


'''************************************************
* @Function Name : pars_xml
************************************************'''
def pars_xml(xml_orgi):
    import xml.etree.ElementTree as et

    parser = et.XMLParser(encoding='utf-8')
    root_el = et.fromstring(xml_orgi, parser=parser)

    aassocnote = "D-0-2-0-0" # II. 사업의 내용
    root = root_el.iter(tag='section-1')

    bdy_txt = []
    for root_ele in root:
        title = root_ele.find('title').items()
        item = title[0][1] # List[('A', 'B'), ('C', 'D')] 튜플이 요소인 리스트 형태

        if item == aassocnote:
            kids = root_ele.iter(tag='p')
            for kid in kids:
                if len(kid.text.strip()) != 0:
                    bdy_txt.append(kid.text.strip())

                childs = kid.iter(tag='span')
                for child in childs:
                    if len(child.text.strip()) != 0:
                        bdy_txt.append(child.text.strip())
    return bdy_txt


'''************************************************
* @Function Name : filt_str
************************************************'''
def filt_speci_str(bdy_txt):
    filt_txt =''
    for line in bdy_txt:

        if '.' in line:
            line = line.replace('&cr','').replace(',',' ').replace('.',' ').replace('(','').replace(')','').replace(';','').replace('/',' ')
            filt_txt += line + '\n'
        '''
        if line == '&cr':
            pass
        else:
            line = line.replace('&cr','').replace(',','').replace('(','').replace(')','').replace(';','')
            filt_txt += line
        '''
    return filt_txt


'''************************************************
* @Function Name : filt_str
************************************************'''
def ld_stpwrd(path):
    with open(path, 'r', encoding="utf-8") as f:
        doc = f.readlines()
        stpwrds = []

        for stpwrd in doc:
            stpwrds.append(stpwrd.replace('\n',''))
    f.close()

    return stpwrds


'''************************************************
* @Function Name : gt_tkn
************************************************'''
def gt_tkn(doc):
    from nltk.tokenize import word_tokenize
    tkned = word_tokenize(doc)

    return tkned

'''************************************************
* @Function Name : anly_tkn
************************************************'''
def anly_tkn(stpwrds, tkned):
    tkns = []

    for tkn in tkned:

        if len(tkn) == 1 : # 문장 수가 한글자인 경우, 불용어 리스트 탐색하여 결과 리스트에 미포함
            if tkn not in stpwrds:
                tkns.append(tkn)
        else:
            for stpwrd in stpwrds: # 불용어 리스트 요소 하나씩 탐색 하여 반환
                if stpwrd in tkn : # 만일 불용어가 문장에 포함되어 있을 경우
                    nw_tkn = tkn.replace(stpwrd, '')

                    if len(nw_tkn) > 1: # 원 단어에서 불용어 삭제 시 단어의 길이가 한글자보다 큰 경우
                        if len(stpwrd) == 1: # 불용어가 한글자 인경우 사전을 뒤져 불용어로 인한 정상단어 형태가 망가지는 것을 방지한다,

                            kr_dict = ret_match_dict(tkn)
                            if tkn in kr_dict: #우리말샘 전체 사전에서 탐색
                                pass  #사전에 있으면 불용어 유지

                            else: # 우리말샘 사전탐색 후 존재하지 않다면,
                                if tkn[len(tkn) - 1] == stpwrd: # 불용어가 토큰의 가장 마지막에 위치한다면,
                                    if nw_tkn in kr_dict: # 불용어 삭제된 토큰이 우리말 사전에 있는지 검색
                                        #print(nw_tkn)
                                        tkn = tkn.replace(stpwrd, '') # 사전에 존재한다면 토큰에서 불용어를 제거
                        else:
                            tkn = tkn.replace(stpwrd, '') # 문장에서 불용어를 제거
                    else:
                        tkn = ''


            tkns.append(tkn)
    tkns = list(filter(None, tkns)) #빈문자열제거

    return tkns

'''************************************************
* @Function Name : dedup_tkn
************************************************'''
def dedup_tkn(kwds):
    from difflib import SequenceMatcher
    #rate_2 = SequenceMatcher(None, str_1, str_2).ratio()

    kwd_filt = []
    i = 0
    for kwd in kwds:
        j = 0

        if len(kwd) > 1:
            kwd_filt.append(kwd)
            for cmp_kwd in kwds:
                if i != j:
                    if len(cmp_kwd) > 2 and kwd != cmp_kwd: # 비교키워드와 동일하지 않을 경우에만 유사도 rate 계산
                        if kwd in cmp_kwd:
                            kwd_filt.append(kwd)

                            kwd_spilt = cmp_kwd.split(kwd)
                            mrg = ''
                            for spilt_wds in kwd_spilt:
                                mrg += spilt_wds

                            if len(mrg) > 1:
                                kwds[j] = mrg
                            else:
                                kwds.pop(j)
                        else:
                            pass
                        #rate = SequenceMatcher(None, kwd, cmp_kwd).ratio()
                        '''
                        if rate >=0.7:
                            kwds[j] = kwd
                        else:
                            pass
                        '''
                    else:
                        pass
                else:
                    pass
                j += 1
        i += 1
    return kwd_filt

'''************************************************
* @Function Name : gt_kr_dict
************************************************'''
def gt_kr_dict():
    import os

    db_path = './doc/db_dict/'
    flist = os.listdir(db_path)

    for db in flist:
        db_nm = db.split('.')[0]
        with open(db_path + db, 'r', encoding='utf-8') as f:
            verbs = f.readlines()

            tmp = []
            for verb in verbs:
                tmp.append(verb.replace('\n',''))

            dict_list[int(db_nm)] = tmp

    return

'''************************************************
* @Function Name : ret_match_dict
************************************************'''
def ret_match_dict(word):
    mtch_dict = []

    chosung = kd.get_chosung(word)
    if chosung != '':
        mtch_dict = dict_list[kd.chosung_dict[chosung]]
    else:
        pass

    return mtch_dict


'''************************************************
* @Function Name : calc_tkn_kywds
************************************************'''
def calc_tkn_kywds(kywds):
    import pandas as pd

    kywds_lt = pd.Series(kywds)
    reslt = kywds_lt.value_counts().head(200)

    kwds = list(reslt.index)
    kwd_val = list(reslt.values)
    with open('./kewrod.txt', 'w', encoding= 'utf-8') as f:
        '''
        for kwd in kwds:
            print(kwd)
            f.writelines(str(kwd) + '\n')
        '''
        for i in range(len(kwds)):
            kwd = str(kwds[i])
            val = str(kwd_val[i])
            f.writelines(kwd + '             ' + val +'\n')
    f.close()


'''************************************************
* @Function Name : filt_industry_word
************************************************'''
def filt_industry_word(kywds, path):  # 산업과 관련된 불필요한 용어 제거 예를 들어, '기업', '산업', '연간' 등
    with open(path, 'r', encoding='utf-8') as f:
        doc = f.readlines()
        indwrds = []

        for indwrd in doc:
            indwrds.append(indwrd.replace('\n',''))
    f.close()

    filt_kywds = []
    for keywd in kywds:
        if keywd == '회사':
            print(1)

        if keywd not in indwrds:
            filt_kywds.append(keywd)

    return filt_kywds


'''************************************************
* @Function Name : main
************************************************'''
def main():
    #kd.gen_kr_dict()
    gt_kr_dict()

    res = gt_co_rept()
    res = extr_sect(res)
    res = pars_xml(res)
    doc = filt_speci_str(res)

    stpwrds = ld_stpwrd(stpwrd_path)
    tkned = gt_tkn(doc)

    res = anly_tkn(stpwrds, tkned)
    res = filt_industry_word(res, indwrd_path)

    res = dedup_tkn(res)
    calc_tkn_kywds(res)

    return

if __name__ == '__main__':
    main()
