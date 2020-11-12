from selenium import webdriver

co_code_path = './doc/co_code/co_code.txt'
chrome_path = "C:\Program Files\Google\Chrome\Application\chromedriver"

'''************************************************
* @Function Name : set_chrome_opt
************************************************'''
def set_chrome_opt(opt1):
    opt = webdriver.ChromeOptions()

    # OPT1 : VISIBLE or INVISBLE
    if opt1 == 1:           #INVISIBLE
        opt.add_argument('headless')
        opt.add_argument('disable-gpu')
    else:
        pass

    return opt


'''************************************************
* @Function Name : gt_co_code
************************************************'''
def gt_co_code():
    co_code_li = [[]]

    print('>> Acquiring Company-code be started.')
    with open(co_code_path, 'r', encoding='utf-8') as f:
        co_codes = f.readlines()

        i = 0
        for co_code in co_codes:
            co_code = co_code.replace('\t','').replace('\n','')
            if i == 0:
                co_code_li[i] = co_code.split(':')
                i = 1
            else:
                co_code_li.append(co_code.split(':'))
    f.close()
    print('>> Acquiring Company-code be finished.')

    return co_code_li

'''************************************************
* @Function Name : gt_rcept_no
************************************************'''
def gt_rcept_no(co_codes):
    from bs4 import BeautifulSoup as bs

    driver = webdriver.Chrome(chrome_path, chrome_options=set_chrome_opt(0))

    url = 'http://dart.fss.or.kr/dsab001/main.do?autoSearch=true'
    driver.get(url)

    driver.find_element_by_xpath('//*[@id="ext-gen81"]').click()                                #초기팝업클로즈
    driver.find_element_by_xpath('//*[@id="publicTypeButton_01"]').click()                      #정기공시선택
    driver.find_element_by_xpath('//*[@id="publicType3"]').click()                              #분기보고서선택

    except_co = []
    include_co = []
    for co_code in co_codes:

        driver.find_element_by_xpath('//*[@id="textCrpNm"]').clear()                                #종목코드입력란 클리어
        driver.find_element_by_xpath('//*[@id="textCrpNm"]').send_keys(co_code[0])                  #종목코드입력
        driver.find_element_by_xpath('//*[@id="searchpng"]').click()                                #선택

        import time
        time.sleep(2)

        html = driver.page_source
        soup = bs(html, "html.parser")

        path = '#listContents > div.table_list > table > tbody > tr > td:nth-child(3)'
        soup_ym = soup.select_one(path)

        if soup_ym is not None:
            rcept_no = soup_ym.find('a').attrs['id']
            rcept_no = rcept_no.replace('r_','')

            co_rcept_no = co_code[1] + ':' + rcept_no
            include_co.append(co_rcept_no)

            print(co_code[1])
            print(rcept_no)
            print(">>>>>>>>>>")
        else:
            except_co.append(co_code[1])

    with open('./doc/co_rcept_no/co_rcept_no.txt', 'w', encoding='utf-8') as f:
        for co_rcept in co_rcept_no:
            f.writelines(co_rcept + '\n')

        f.writelines("===========================================================\n")

        for co_none in except_co:
            f.writelines(co_none + '\n')

        f.flush()
    f.close()

    import time
    time.sleep(500)

'''************************************************
* @Function Name : acc_dart
************************************************'''
def acc_dart():
    res = gt_co_code()
    gt_rcept_no(res)
