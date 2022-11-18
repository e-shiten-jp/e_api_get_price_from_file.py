# -*- coding: utf-8 -*-
# Copyright (c) 2021 Tachibana Securities Co., Ltd. All rights reserved.

# 2021.07.09,   yo.
# 2022.11.18 reviced,   yo.
# Python 3.6.8 / centos7.4
# API v4r3 で動作確認
# 立花証券ｅ支店ＡＰＩ利用のサンプルコード
# ログインして、株価取得、ログアウトします。

import urllib3
import datetime
import json
import time


#--- 共通コード ------------------------------------------------------

# request項目を保存するクラス。配列として使う。
# 'p_no'、'p_sd_date'は格納せず、func_make_url_requestで生成する。
class class_req :
    def __init__(self) :
        self.str_key = ''
        self.str_value = ''
        
    def add_data(self, work_key, work_value) :
        self.str_key = work_key
        self.str_value = work_value


# 口座属性クラス
class class_def_cust_property:
    def __init__(self):
        self.sUrlRequest = ''       # request用仮想URL
        self.sUrlMaster = ''        # master用仮想URL
        self.sUrlPrice = ''         # price用仮想URL
        self.sUrlEvent = ''         # event用仮想URL
        self.sZyoutoekiKazeiC = ''  # 8.譲渡益課税区分    1：特定  3：一般  5：NISA     ログインの返信データで設定済み。 
        self.sSecondPassword = ''   # 22.第二パスワード  APIでは第２暗証番号を省略できない。 関連資料:「立花証券・e支店・API、インターフェース概要」の「3-2.ログイン、ログアウト」参照
        self.sJsonOfmt = ''         # 返り値の表示形式指定
        


# 機能: システム時刻を"p_sd_date"の書式の文字列で返す。
# 返値: "p_sd_date"の書式の文字列
# 引数1: システム時刻
# 備考:  "p_sd_date"の書式：YYYY.MM.DD-hh:mm:ss.sss
def func_p_sd_date(int_systime):
    str_psddate = ''
    str_psddate = str_psddate + str(int_systime.year) 
    str_psddate = str_psddate + '.' + ('00' + str(int_systime.month))[-2:]
    str_psddate = str_psddate + '.' + ('00' + str(int_systime.day))[-2:]
    str_psddate = str_psddate + '-' + ('00' + str(int_systime.hour))[-2:]
    str_psddate = str_psddate + ':' + ('00' + str(int_systime.minute))[-2:]
    str_psddate = str_psddate + ':' + ('00' + str(int_systime.second))[-2:]
    str_psddate = str_psddate + '.' + (('000000' + str(int_systime.microsecond))[-6:])[:3]
    return str_psddate


# JSONの値の前後にダブルクオーテーションが無い場合付ける。
def func_check_json_dquat(str_value) :
    if len(str_value) == 0 :
        str_value = '""'
        
    if not str_value[:1] == '"' :
        str_value = '"' + str_value
        
    if not str_value[-1:] == '"' :
        str_value = str_value + '"'
        
    return str_value
    
    
# 受けたテキストの１文字目と最終文字の「"」を削除
# 引数：string
# 返り値：string
def func_strip_dquot(text):
    if len(text) > 0:
        if text[0:1] == '"' :
            text = text[1:]
            
    if len(text) > 0:
        if text[-1] == '\n':
            text = text[0:-1]
        
    if len(text) > 0:
        if text[-1:] == '"':
            text = text[0:-1]
        
    return text
    


# 機能: URLエンコード文字の変換
# 引数1: 文字列
# 返値: URLエンコード文字に変換した文字列
# 
# URLに「#」「+」「/」「:」「=」などの記号を利用した場合エラーとなる場合がある。
# APIへの入力文字列（特にパスワードで記号を利用している場合）で注意が必要。
#   '#' →   '%23'
#   '+' →   '%2B'
#   '/' →   '%2F'
#   ':' →   '%3A'
#   '=' →   '%3D'
def func_replace_urlecnode( str_input ):
    str_encode = ''
    str_replace = ''
    
    for i in range(len(str_input)):
        str_char = str_input[i:i+1]

        if str_char == ' ' :
            str_replace = '%20'       #「 」 → 「%20」 半角空白
        elif str_char == '!' :
            str_replace = '%21'       #「!」 → 「%21」
        elif str_char == '"' :
            str_replace = '%22'       #「"」 → 「%22」
        elif str_char == '#' :
            str_replace = '%23'       #「#」 → 「%23」
        elif str_char == '$' :
            str_replace = '%24'       #「$」 → 「%24」
        elif str_char == '%' :
            str_replace = '%25'       #「%」 → 「%25」
        elif str_char == '&' :
            str_replace = '%26'       #「&」 → 「%26」
        elif str_char == "'" :
            str_replace = '%27'       #「'」 → 「%27」
        elif str_char == '(' :
            str_replace = '%28'       #「(」 → 「%28」
        elif str_char == ')' :
            str_replace = '%29'       #「)」 → 「%29」
        elif str_char == '*' :
            str_replace = '%2A'       #「*」 → 「%2A」
        elif str_char == '+' :
            str_replace = '%2B'       #「+」 → 「%2B」
        elif str_char == ',' :
            str_replace = '%2C'       #「,」 → 「%2C」
        elif str_char == '/' :
            str_replace = '%2F'       #「/」 → 「%2F」
        elif str_char == ':' :
            str_replace = '%3A'       #「:」 → 「%3A」
        elif str_char == ';' :
            str_replace = '%3B'       #「;」 → 「%3B」
        elif str_char == '<' :
            str_replace = '%3C'       #「<」 → 「%3C」
        elif str_char == '=' :
            str_replace = '%3D'       #「=」 → 「%3D」
        elif str_char == '>' :
            str_replace = '%3E'       #「>」 → 「%3E」
        elif str_char == '?' :
            str_replace = '%3F'       #「?」 → 「%3F」
        elif str_char == '@' :
            str_replace = '%40'       #「@」 → 「%40」
        elif str_char == '[' :
            str_replace = '%5B'       #「[」 → 「%5B」
        elif str_char == ']' :
            str_replace = '%5D'       #「]」 → 「%5D」
        elif str_char == '^' :
            str_replace = '%5E'       #「^」 → 「%5E」
        elif str_char == '`' :
            str_replace = '%60'       #「`」 → 「%60」
        elif str_char == '{' :
            str_replace = '%7B'       #「{」 → 「%7B」
        elif str_char == '|' :
            str_replace = '%7C'       #「|」 → 「%7C」
        elif str_char == '}' :
            str_replace = '%7D'       #「}」 → 「%7D」
        elif str_char == '~' :
            str_replace = '%7E'       #「~」 → 「%7E」
        else :
            str_replace = str_char

        str_encode = str_encode + str_replace
        
    return str_encode



# 機能： API問合せ文字列を作成し返す。
# 戻り値： url文字列
# 第１引数： ログインは、Trueをセット。それ以外はFalseをセット。
# 第２引数： ログインは、APIのurlをセット。それ以外はログインで返された仮想url（'sUrlRequest'等）の値をセット。
# 第３引数： 要求項目のデータセット。クラスの配列として受取る。
def func_make_url_request(auth_flg, \
                          url_target, \
                          work_class_req) :
    work_key = ''
    work_value = ''

    str_url = url_target
    if auth_flg == True :
        str_url = str_url + 'auth/'
    
    str_url = str_url + '?{\n\t'
    
    for i in range(len(work_class_req)) :
        work_key = func_strip_dquot(work_class_req[i].str_key)
        if len(work_key) > 0:
            if work_key[:1] == 'a' :
                work_value = work_class_req[i].str_value
            else :
                work_value = func_check_json_dquat(work_class_req[i].str_value)

            str_url = str_url + func_check_json_dquat(work_class_req[i].str_key) \
                                + ':' + work_value \
                                + ',\n\t'
               
        
    str_url = str_url[:-3] + '\n}'
    return str_url



# 機能: API問合せ。通常のrequest,price用。
# 返値: API応答（辞書型）
# 第１引数： URL文字列。
# 備考: APIに接続し、requestの文字列を送信し、応答データを辞書型で返す。
#       master取得は専用の func_api_req_muster を利用する。
def func_api_req(str_url): 
    print('送信文字列＝')
    print(str_url)  # 送信する文字列

    # APIに接続
    http = urllib3.PoolManager()
    req = http.request('GET', str_url)
    print("req.status= ", req.status )

    # 取得したデータを、json.loadsを利用できるようにstr型に変換する。日本語はshift-jis。
    bytes_reqdata = req.data
    str_shiftjis = bytes_reqdata.decode("shift-jis", errors="ignore")

    print('返信文字列＝')
    print(str_shiftjis)

    # JSON形式の文字列を辞書型で取り出す
    json_req = json.loads(str_shiftjis)

    return json_req



# ログイン関数
# 引数1: p_noカウンター
# 引数2: アクセスするurl（'auth/'以下は付けない）
# 引数3: ユーザーID
# 引数4: パスワード
# 引数5: 口座属性クラス
# 返値：辞書型データ（APIからのjson形式返信データをshift-jisのstring型に変換し、更に辞書型に変換）
def func_login(int_p_no, my_url, str_userid, str_passwd, class_cust_property):
    # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p2/46 No.1 引数名:CLMAuthLoginRequest を参照してください。
    
    req_item = [class_req()]
    str_p_sd_date = func_p_sd_date(datetime.datetime.now())     # システム時刻を所定の書式で取得

    str_key = '"p_no"'
    str_value = func_check_json_dquat(str(int_p_no))
    #req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"p_sd_date"'
    str_value = str_p_sd_date
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sCLMID"'
    str_value = 'CLMAuthLoginRequest'
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sUserId"'
    str_value = str_userid
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    str_key = '"sPassword"'
    str_value = str_passwd
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # 返り値の表示形式指定
    str_key = '"sJsonOfmt"'
    str_value = class_cust_property.sJsonOfmt    # "5"は "1"（1ビット目ＯＮ）と”4”（3ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    # ログインとログイン後の電文が違うため、第１引数で指示。
    # ログインはTrue。それ以外はFalse。
    # このプログラムでの仕様。APIの仕様ではない。
    # URL文字列の作成
    str_url = func_make_url_request(True, \
                                     my_url, \
                                     req_item)
    # API問合せ
    json_return = func_api_req(str_url)
    # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p2/46 No.2 引数名:CLMAuthLoginAck を参照してください。

    int_p_errno = int(json_return.get('p_errno'))    # p_erronは、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇ｒ〇）、REQUEST I/F、利用方法、データ仕様」を参照ください。
    int_sResultCode = int(json_return.get('sResultCode'))
    # sResultCodeは、マニュアル
    # 「立花証券・ｅ支店・ＡＰＩ（ｖ〇ｒ〇）、REQUEST I/F、注文入力機能引数項目仕様」
    # (api_request_if_order_vOrO.pdf)
    # の p13/42 「6.メッセージ一覧」を参照ください。

    if int_p_errno ==  0 and int_sResultCode == 0:    # ログインエラーでない場合
        # ---------------------------------------------
        # ログインでの注意点
        # 契約締結前書面が未読の場合、
        # 「int_p_errno = 0 And int_sResultCode = 0」で、
        # sUrlRequest=""、sUrlEvent="" が返されログインできない。
        # ---------------------------------------------
        if len(json_return.get('sUrlRequest')) > 0 :
            # 口座属性クラスに取得した値をセット
            class_cust_property.sZyoutoekiKazeiC = json_return.get('sZyoutoekiKazeiC')
            class_cust_property.sUrlRequest = json_return.get('sUrlRequest')        # request用仮想URL
            class_cust_property.sUrlMaster = json_return.get('sUrlMaster')          # master用仮想URL
            class_cust_property.sUrlPrice = json_return.get('sUrlPrice')            # price用仮想URL
            class_cust_property.sUrlEvent = json_return.get('sUrlEvent')            # event用仮想URL
            bool_login = True
        else :
            print('契約締結前書面が未読です。')
            print('ブラウザーで標準Webにログインして確認してください。')
    else :  # ログインに問題があった場合
        print('p_errno:', json_return.get('p_errno'))
        print('p_err:', json_return.get('p_err'))
        print('sResultCode:', json_return.get('sResultCode'))
        print('sResultText:', json_return.get('sResultText'))
        print()
        bool_login = False

    return bool_login


# ログアウト
# 引数1: p_noカウンター
# 引数2: class_cust_property（request通番）, 口座属性クラス
# 返値：辞書型データ（APIからのjson形式返信データをshift-jisのstring型に変換し、更に辞書型に変換）
def func_logout(int_p_no, class_cust_property):
    # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p3/46 No.3 引数名:CLMAuthLogoutRequest を参照してください。
    
    req_item = [class_req()]
    str_p_sd_date = func_p_sd_date(datetime.datetime.now())     # システム時刻を所定の書式で取得

    str_key = '"p_no"'
    str_value = func_check_json_dquat(str(int_p_no))
    #req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"p_sd_date"'
    str_value = str_p_sd_date
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sCLMID"'
    str_value = 'CLMAuthLogoutRequest'  # logoutを指示。
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # 返り値の表示形式指定
    str_key = '"sJsonOfmt"'
    str_value = class_cust_property.sJsonOfmt    # "5"は "1"（ビット目ＯＮ）と”4”（ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # ログインとログイン後の電文が違うため、第１引数で指示。
    # ログインはTrue。それ以外はFalse。
    # このプログラムでの仕様。APIの仕様ではない。
    # URL文字列の作成
    str_url = func_make_url_request(False, \
                                     class_cust_property.sUrlRequest, \
                                     req_item)
    # API問合せ
    json_return = func_api_req(str_url)
    # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p3/46 No.4 引数名:CLMAuthLogoutAck を参照してください。

    int_sResultCode = int(json_return.get('sResultCode'))    # p_erronは、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇ｒ〇）、REQUEST I/F、利用方法、データ仕様」を参照ください。
    if int_sResultCode ==  0 :    # ログアウトエラーでない場合
        bool_logout = True
    else :  # ログアウトに問題があった場合
        bool_logout = False

    return bool_logout

#--- 以上 共通コード -------------------------------------------------









# 「型＋情報コード」から「名前」を取得する
# 引数：型＋情報コード」（string）
# 戻り値：「名前」（string）
# 資料「立花証券・ｅ支店・ＡＰＩ、EVENT I/F 利用方法、データ仕様」（api_event_if.pdf）
# p6-9/26 【情報コード一覧】
def func_code_to_name(str_input):
    str_input = func_strip_dquot(str_input)
    str_return = ''
    if str_input == 'xLISS':        str_return = '"所属"'         # ShiftJIS文字列を１６進数文字列として設定。（含む半角カナ）
    elif str_input == 'pDPP':       str_return = '"現在値"'        # 
    elif str_input == 'tDPP:T':     str_return = '"現在値時刻"'    # 「HH:MM」
    elif str_input == 'pDPG':       str_return = '"現値前値比較"' # ,「0000」：事象なし「0056」：現値＝前値,「0057」：現値＞前値（↑）,「0058」：現値＜前値(↓),「0059」：中断板寄後の初値「0060」：ザラバ引け（・）,「0061」：板寄引け「0062」：中断引け,「0068」：売買停止引け※（）内は画面表示記号。
    elif str_input == 'pDYWP':      str_return = '"前日比"'        # 
    elif str_input == 'pDYRP':      str_return = '"騰落率"'        # 
    elif str_input == 'pDOP':       str_return = '"始値"'         # 
    elif str_input == 'tDOP:T':     str_return = '"始値時刻"'   # 「HH:MM」
    elif str_input == 'pDHP':       str_return = '"高値"'         # 
    elif str_input == 'tDHP:T':     str_return = '"高値時刻"'   # 「HH:MM」
    elif str_input == 'pDLP':       str_return = '"安値"'         # 
    elif str_input == 'tDLP:T':     str_return = '"安値時刻"'   # 「HH:MM」
    elif str_input == 'pDV':        str_return = '"出来高"'        # 
    elif str_input == 'pQAS':       str_return = '"売気配値種類"'    # 「0000」：事象なし,「0101」：一般気配,「0102」：特別気配（ウ）,「0107」：寄前気配（寄）,「0108」：停止前特別気配（停）,「0118」：連続約定気配,「0119」：停止前の連続約定気配（U）,「0120」：一般気配、買上がり・売下がり中,※（）内は画面表示記号。
    elif str_input == 'pQAP':       str_return = '"売気配値"'    # 
    elif str_input == 'pAV':        str_return = '"売気配数量"'    # 
    elif str_input == 'pQBS':       str_return = '"買気配値種類"'    # 「0000」：事象なし,「0101」：一般気配,「0102」：特別気配（カ）,「0107」：寄前気配（寄）,「0108」：停止前特別気配（停）,「0118」：連続約定気配,「0119」：停止前の連続約定気配（K）,「0120」：一般気配、買上がり・売下がり中,※（）内は画面表示記号。
    elif str_input == 'pQBP':       str_return = '"買気配値"'    # 
    elif str_input == 'pBV':        str_return = '"買気配数量"'    # 
    elif str_input == 'xDVES':      str_return = '"配当落銘柄区分"'    # 「配」：配当権利落、中間配当権利落、期中配当権利落,「」：上記外,※「」内文字を画面表示。
    elif str_input == 'xDCFS':      str_return = '"不連続要因銘柄区分"'    # 「分」：株式分割,「併」：株式併合、減資を伴う併合,「有」：有償,「無」：無償,「預」権利預り証落ち,「ム」：無償割当,「ラ」：ライツオファリング,「」：上記外,※「」内文字を画面表示。
    elif str_input == 'pDHF':       str_return = '"日通し高値フラグ"'    # 「0000」：事象なし,「0071」：ストップ高(S),
    elif str_input == 'pDLF':       str_return = '"日通し安値フラグ"'    # 「0000」：事象なし,「0072」：ストップ安(S), ※（）内は画面表示記号。
    elif str_input == 'pDJ':        str_return = '"売買代金"'    # 
    elif str_input == 'pAAV':       str_return = '"売数量（成行）"'    # 
    elif str_input == 'pABV':       str_return = '"買数量（成行）"'    # 
    elif str_input == 'pQOV':       str_return = '"売-OVER"'    # 
    elif str_input == 'pGAV10':     str_return = '"売-１０-数量"'    # 
    elif str_input == 'pGAP10':     str_return = '"売-１０-値段"'    # 
    elif str_input == 'pGAV9':      str_return = '"売-９-数量"'    # 
    elif str_input == 'pGAP9':      str_return = '"売-９-値段"'    # 
    elif str_input == 'pGAV8':      str_return = '"売-８-数量"'    # 
    elif str_input == 'pGAP8':      str_return = '"売-８-値段"'    # 
    elif str_input == 'pGAV7':      str_return = '"売-７-数量"'    # 
    elif str_input == 'pGAP7':      str_return = '"売-７-値段"'    # 
    elif str_input == 'pGAV6':      str_return = '"売-６-数量"'    # 
    elif str_input == 'pGAP6':      str_return = '"売-６-値段"'    # 
    elif str_input == 'pGAV5':      str_return = '"売-５-数量"'    # 
    elif str_input == 'pGAP5':      str_return = '"売-５-値段"'    # 
    elif str_input == 'pGAV4':      str_return = '"売-４-数量"'    # 
    elif str_input == 'pGAP4':      str_return = '"売-４-値段"'    # 
    elif str_input == 'pGAV3':      str_return = '"売-３-数量"'    # 
    elif str_input == 'pGAP3':      str_return = '"売-３-値段"'    # 
    elif str_input == 'pGAV2':      str_return = '"売-２-数量"'    # 
    elif str_input == 'pGAP2':      str_return = '"売-２-値段"'    # 
    elif str_input == 'pGAV1':      str_return = '"売-１-数量"'    # 
    elif str_input == 'pGAP1':      str_return = '"売-１-値段"'    # 
    elif str_input == 'pGBV1':      str_return = '"買-１-数量"'    # 
    elif str_input == 'pGBP1':      str_return = '"買-１-値段"'    # 
    elif str_input == 'pGBV2':      str_return = '"買-２-数量"'    # 
    elif str_input == 'pGBP2':      str_return = '"買-２-値段"'    # 
    elif str_input == 'pGBV3':      str_return = '"買-３-数量"'    # 
    elif str_input == 'pGBP3':      str_return = '"買-３-値段"'    # 
    elif str_input == 'pGBV4':      str_return = '"買-４-数量"'    # 
    elif str_input == 'pGBP4':      str_return = '"買-４-値段"'    # 
    elif str_input == 'pGBV5':      str_return = '"買-５-数量"'    # 
    elif str_input == 'pGBP5':      str_return = '"買-５-値段"'    # 
    elif str_input == 'pGBV6':      str_return = '"買-６-数量"'    # 
    elif str_input == 'pGBP6':      str_return = '"買-６-値段"'    # 
    elif str_input == 'pGBV7':      str_return = '"買-７-数量"'    # 
    elif str_input == 'pGBP7':      str_return = '"買-７-値段"'    # 
    elif str_input == 'pGBV8':      str_return = '"買-８-数量"'    # 
    elif str_input == 'pGBP8':      str_return = '"買-８-値段"'    # 
    elif str_input == 'pGBV9':      str_return = '"買-９-数量"'    # 
    elif str_input == 'pGBP9':      str_return = '"買-９-値段"'    # 
    elif str_input == 'pGBV10':     str_return = '"買-１０-数量"'    # 
    elif str_input == 'pGBP10':     str_return = '"買-１０-値段"'    # 
    elif str_input == 'pQUV':       str_return = '"買-UNDER"'        # 
    elif str_input == 'pVWAP':      str_return = '"VWAP"'    # 
    elif str_input == 'pPRP':       str_return = '"前日終値"'    # 
    else:                           str_return = 'none'

    return  str_return
        

# 「名前」から「型＋情報コード」を取得する
# 引数：「名前」（string）
# 戻り値：型＋情報コード」（string）
# 資料「立花証券・ｅ支店・ＡＰＩ、EVENT I/F 利用方法、データ仕様」（api_event_if.pdf）
# p6-9/26 【情報コード一覧】
def func_name_to_code(str_input):
    str_input = func_strip_dquot(str_input)
    str_return = ''
    if str_input == '所属':        str_return = '" xLISS"'    # ShiftJIS文字列を１６進数文字列として設定。（含む半角カナ）
    elif str_input == '現在値':        str_return = '"pDPP"'    # 
    elif str_input == '現在値時刻':        str_return = '"tDPP:T"'    # 「HH:MM」
    elif str_input == '現値前値比較':        str_return = '"pDPG"'    # 「0000」：事象なし「0056」：現値＝前値,「0057」：現値＞前値（↑）,「0058」：現値＜前値(↓),「0059」：中断板寄後の初値「0060」：ザラバ引け（・）,「0061」：板寄引け「0062」：中断引け,「0068」：売買停止引け※（）内は画面表示記号。
    elif str_input == '前日比':        str_return = '"pDYWP"'    # 
    elif str_input == '騰落率':        str_return = '"pDYRP"'    # 
    elif str_input == '始値':        str_return = '"pDOP"'    # 
    elif str_input == '始値時刻':        str_return = '"tDOP:T"'    # 「HH:MM」
    elif str_input == '高値':        str_return = '"pDHP"'    # 
    elif str_input == '高値時刻':        str_return = '"tDHP:T"'    # 「HH:MM」
    elif str_input == '安値':        str_return = '"pDLP"'    # 
    elif str_input == '安値時刻':        str_return = '"tDLP:T"'    # 「HH:MM」
    elif str_input == '出来高':        str_return = '"pDV"'    # 
    elif str_input == '売気配値種類':        str_return = '"pQAS"'    # 「0000」：事象なし,「0101」：一般気配,「0102」：特別気配（ウ）,「0107」：寄前気配（寄）,「0108」：停止前特別気配（停）,「0118」：連続約定気配,「0119」：停止前の連続約定気配（U）,「0120」：一般気配、買上がり・売下がり中,※（）内は画面表示記号。
    elif str_input == '売気配値':        str_return = '"pQAP"'    # 
    elif str_input == '売気配数量':        str_return = '"pAV"'    # 
    elif str_input == '買気配値種類':        str_return = '"pQBS"'    # 「0000」：事象なし,「0101」：一般気配,「0102」：特別気配（カ）,「0107」：寄前気配（寄）,「0108」：停止前特別気配（停）,「0118」：連続約定気配,「0119」：停止前の連続約定気配（K）,「0120」：一般気配、買上がり・売下がり中,※（）内は画面表示記号。
    elif str_input == '買気配値':        str_return = '"pQBP"'    # 
    elif str_input == '買気配数量':        str_return = '"pBV"'    # 
    elif str_input == '配当落銘柄区分':        str_return = '"xDVES"'    # 「配」：配当権利落、中間配当権利落、期中配当権利落,「」：上記外,※「」内文字を画面表示。
    elif str_input == '不連続要因銘柄区分':        str_return = '"xDCFS"'    # 「分」：株式分割,「併」：株式併合、減資を伴う併合,「有」：有償,「無」：無償,「預」権利預り証落ち,「ム」：無償割当,「ラ」：ライツオファリング,「」：上記外,※「」内文字を画面表示。
    elif str_input == '日通し高値フラグ':        str_return = '"pDHF"'    # 「0000」：事象なし,「0071」：ストップ高(S),
    elif str_input == '日通し安値フラグ':        str_return = '"pDLF"'    # 「0000」：事象なし,「0072」：ストップ安(S), ※（）内は画面表示記号。
    elif str_input == '売買代金':        str_return = '"pDJ"'    # 
    elif str_input == '売数量（成行）':        str_return = '"pAAV"'    # 
    elif str_input == '買数量（成行）':        str_return = '"pABV"'    # 
    elif str_input == '売-OVER':        str_return = '"pQOV"'    # 
    elif str_input == '売-１０-数量':      str_return = '"pGAV10"'    # 
    elif str_input == '売-１０-値段':      str_return = '"pGAP10"'    # 
    elif str_input == '売-９-数量':        str_return = '"pGAV9"'    # 
    elif str_input == '売-９-値段':        str_return = '"pGAP9"'    # 
    elif str_input == '売-８-数量':        str_return = '"pGAV8"'    # 
    elif str_input == '売-８-値段':        str_return = '"pGAP8"'    # 
    elif str_input == '売-７-数量':        str_return = '"pGAV7"'    # 
    elif str_input == '売-７-値段':        str_return = '"pGAP7"'    # 
    elif str_input == '売-６-数量':        str_return = '"pGAV6"'    # 
    elif str_input == '売-６-値段':        str_return = '"pGAP6"'    # 
    elif str_input == '売-５-数量':        str_return = '"pGAV5"'    # 
    elif str_input == '売-５-値段':        str_return = '"pGAP5"'    # 
    elif str_input == '売-４-数量':        str_return = '"pGAV4"'    # 
    elif str_input == '売-４-値段':        str_return = '"pGAP4"'    # 
    elif str_input == '売-３-数量':        str_return = '"pGAV3"'    # 
    elif str_input == '売-３-値段':        str_return = '"pGAP3"'    # 
    elif str_input == '売-２-数量':        str_return = '"pGAV2"'    # 
    elif str_input == '売-２-値段':        str_return = '"pGAP2"'    # 
    elif str_input == '売-１-数量':        str_return = '"pGAV1"'    # 
    elif str_input == '売-１-値段':        str_return = '"pGAP1"'    # 
    elif str_input == '買-１-数量':        str_return = '"pGBV1"'    # 
    elif str_input == '買-１-値段':        str_return = '"pGBP1"'    # 
    elif str_input == '買-２-数量':        str_return = '"pGBV2"'    # 
    elif str_input == '買-２-値段':        str_return = '"pGBP2"'    # 
    elif str_input == '買-３-数量':        str_return = '"pGBV3"'    # 
    elif str_input == '買-３-値段':        str_return = '"pGBP3"'    # 
    elif str_input == '買-４-数量':        str_return = '"pGBV4"'    # 
    elif str_input == '買-４-値段':        str_return = '"pGBP4"'    # 
    elif str_input == '買-５-数量':        str_return = '"pGBV5"'    # 
    elif str_input == '買-５-値段':        str_return = '"pGBP5"'    # 
    elif str_input == '買-６-数量':        str_return = '"pGBV6"'    # 
    elif str_input == '買-６-値段':        str_return = '"pGBP6"'    # 
    elif str_input == '買-７-数量':        str_return = '"pGBV7"'    # 
    elif str_input == '買-７-値段':        str_return = '"pGBP7"'    # 
    elif str_input == '買-８-数量':        str_return = '"pGBV8"'    # 
    elif str_input == '買-８-値段':        str_return = '"pGBP8"'    # 
    elif str_input == '買-９-数量':        str_return = '"pGBV9"'    # 
    elif str_input == '買-９-値段':        str_return = '"pGBP9"'    # 
    elif str_input == '買-１０-数量':      str_return = '"pGBV10"'    # 
    elif str_input == '買-１０-値段':      str_return = '"pGBP10"'    # 
    elif str_input == '買-UNDER':          str_return = '"pQUV"'    # 
    elif str_input == 'VWAP':               str_return = '"pVWAP"'    # 
    elif str_input == '前日終値':          str_return = '"pPRP"'    # 
    else:       str_return = 'none'

    return str_return




# 株価取得リストの読み込み
# 引数：ファイル名、銘柄コード保存用配列、取得する情報コード用配列
# 指定ファイルを開き、1行目で取得する情報コードを読み込み、2行目以降で銘柄コードを読み込む。
# （通常1行目の）情報コードを読み込む行の第1項目は、'stock_code'とすることが必要。
def func_read_price_list(str_fname_input, my_code, my_column):
    try:
        # 入力データを読み込み処理開始
        with open(str_fname_input, 'r', encoding = 'shift_jis') as fin:
            print('file read ok -----', str_fname_input)
                            
            while True:
                line = fin.readline()
                
                if not len(line):
                    #EOFの場合
                    break

                # 行のデータをcsvの「,」で分割し必要なフィールドを読み込む。
                sprit_out = line.split(',')
                
                if len(sprit_out) > 0:
                    if len(sprit_out[0]) > 0 and func_strip_dquot(sprit_out[0]) == 'stock_code':
                        # １行目は表題行なので、情報コードを取得する。
                        # 取得できる価格情報は、資料「立花証券・ｅ支店・ＡＰＩ、EVENT I/F 利用方法、データ仕様」
                        # p6-8/26 【情報コード一覧】を利用する。
                        # 取得コードの書式：型+情報コード
                        
                        for i in range(1,len(sprit_out)):
                            my_column.append('')
                            my_column[i] = func_strip_dquot(sprit_out[i])

                        # 銘柄コードのリストの最初の項目に、便宜上'stock_code'を入れておく。
                        my_code[-1] = func_strip_dquot(sprit_out[0])
                            
                    elif  len(sprit_out[0]) > 0 :
                        my_code.append('')
                        my_code[-1] = func_strip_dquot(sprit_out[0])
                        
                    else:
                        pass
                                    
    except IOError as e:
        print('File Not Found!!!')
        print(type(e))
        #print(line)




# １行目タイトルを株価情報のファイルに書き込む
# 引数：出力ファイル名、取得した株価情報（辞書型）、取得する情報コード用配列
# 指定ファイルを開き、1行目に取得する情報名を書き込み、2行目以降で取得した情報を書き込む。
def func_write_price_title(str_fname_output, my_column):
    try:
        with open(str_fname_output, 'w', encoding = 'shift_jis') as fout:
            print('file open at w, "fout": ', str_fname_output )
            # 出力ファイルの１行目の列名を作成
            str_text_out = 'stock_code'
            for i in range(len(my_column)):
                if len(my_column[i]) > 0 :
                    str_text_out = str_text_out + ',' + func_code_to_name(my_column[i])     # 情報コードを名前に変換。
            str_text_out = str_text_out + '\n'
            fout.write(str_text_out)     # １行目に列名を書き込む

    except IOError as e:
        print('Can not Write!!!')
        print(type(e))
        #print(line)




# 取得した株価情報を追記モードでファイルに書き込む
# 引数：出力ファイル名、取得した株価情報（辞書型）、取得する情報コード用配列
# 指定ファイルを開き、1行目に取得する情報名を書き込み、2行目以降で取得した情報を書き込む。
def func_write_price_list(str_fname_output, dic_return, my_column):
    try:
        with open(str_fname_output, 'a', encoding = 'shift_jis') as fout:
            print('file open at a, "fout": ', str_fname_output )
            # 取得した情報から行データを作成し書き込む
            str_text_out = ''
            for i in range(len(dic_return)):
                # 行データ作成
                str_sIssueCode = dic_return[i].get('sIssueCode') 
                if not str_sIssueCode == 'stock_code' :
                    str_text_out = str_sIssueCode
                    for n in range(len(my_column)):
                        if len(my_column[n]) > 0 :
                            str_text_out = str_text_out + ',' + dic_return[i].get(my_column[n])
                    str_text_out = str_text_out + '\n'
                    fout.write(str_text_out)     # 処理済みの株価データを書き込む
                  

    except IOError as e:
        print('Can not Write!!!')
        print(type(e))
        #print(line)




# 株価情報の取得
# 引数：銘柄コード（配列）, 取得する「情報コード」（配列）, 口座属性クラス
# マニュアル「ｅ支店・ＡＰＩ、ブラウザからの利用方法」の「時価」シートの時価関連情報取得サンプル
#
# ３．利用方法（２）時価関連情報の取得
# https://10.62.26.91/e_api_v4r2/request/MDExNDczNTEwMDQwNi05MS02NDU1NA==/?{"p_no":"20","p_sd_date":"2021.06.04-14:56:50.000",
# "sCLMID":"CLMMfdsGetMarketPrice","sTargetIssueCode":"6501,6501,101","sTargetColumn":"pDPP,tDPP:T,pPRP","sJsonOfmt":"5"}
#
# 
# 取得できる価格情報は、資料「立花証券・ｅ支店・ＡＰＩ、EVENT I/F 利用方法、データ仕様」
# p6-8/26 【情報コード一覧】を利用する。
# 取得コードの書式：型+情報コード
#
# 株価の取得は通信帯域に負荷が掛かります。利用する情報のみの取得をお願いいたします。
def func_get_price(int_p_no, str_code_list, my_column, class_cust_property):

    req_item = [class_req()]
    str_p_sd_date = func_p_sd_date(datetime.datetime.now())     # システム時刻を所定の書式で取得

    str_key = '"p_no"'
    str_value = func_check_json_dquat(str(int_p_no))
    #req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"p_sd_date"'
    str_value = str_p_sd_date
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    str_key = '"sCLMID"'
    str_value = '"CLMMfdsGetMarketPrice"'   # 株価取得を指定
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    # 株価を取得する銘柄コードをセット
    # 取得したい銘柄コードをカンマで区切りで羅列する。
    # 例：{"sTargetIssueCode":"6501,6502,101"}
    str_key = '"sTargetIssueCode"'
    str_value = str_code_list
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    

    # 取得する「情報コード」をセット
    # 取得したい情報コードをカンマで区切りで羅列する。	
    # 例：{"sTargetColumn":"pDPP,tDPP:T,pPRP"}
    str_list = ''
    for i in range(len(my_column)):
        if len(my_column[i]) > 0:
            str_list = str_list + my_column[i] + ','
        
    str_key = '"sTargetColumn"'
    str_value = str_list[:-1]
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    

    # 返り値の表示形式指定
    str_key = '"sJsonOfmt"'
    str_value = class_cust_property.sJsonOfmt
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # URL文字列の作成
    str_url = func_make_url_request(False, \
                                     class_cust_property.sUrlPrice, \
                                     req_item)
    # API問合せ
    json_return = func_api_req(str_url)

    return json_return




    
# ======================================================================================================
# ==== プログラム始点 =================================================================================
# ======================================================================================================

# --- 利用時に変数を設定してください -------------------------------------------------------

# 接続先 設定 --------------
# デモ環境（新バージョンになった場合、適宜変更）
my_url = 'https://demo-kabuka.e-shiten.jp/e_api_v4r3/'

# 本番環境（新バージョンになった場合、適宜変更）
# ＊＊！！実際に市場に注文が出るので注意！！＊＊
# my_url = 'https://kabuka.e-shiten.jp/e_api_v4r3/'


# ＩＤパスワード設定 ---------
my_userid = 'MY_USERID' # 自分のuseridに書き換える
my_passwd = 'MY_PASSWD' # 自分のpasswordに書き換える
my_2pwd = 'MY_2PASSWD'  # 自分の第２passwordに書き換える


# コマンド用パラメーター -------------------    
#
str_fname_input = 'price_list_in.csv'   # 取得する情報コードと銘柄を読み込むファイル名。カレントディレクトリに存在すること。
str_fname_output = 'price_list_out.csv'   # 書き込むファイル名。カレントディレクトリに上書きモードでファイルが作成される。


# --- 以上設定項目 -------------------------------------------------------------------------


class_cust_property = class_def_cust_property()     # 口座属性クラス

# ID、パスワード、第２パスワードのURLエンコードをチェックして変換
my_userid = func_replace_urlecnode(my_userid)
my_passwd = func_replace_urlecnode(my_passwd)
class_cust_property.sSecondPassword = func_replace_urlecnode(my_2pwd)

# 返り値の表示形式指定
class_cust_property.sJsonOfmt = '5'
# "5"は "1"（1ビット目ＯＮ）と”4”（3ビット目ＯＮ）の指定となり
# ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定

print('-- login -----------------------------------------------------')
# 送信項目、戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
# p2/46 No.1 引数名:CLMAuthLoginRequest を参照してください。
int_p_no = 1
# ログイン処理
bool_login = func_login(int_p_no, my_url, my_userid, my_passwd,  class_cust_property)


# ログインOKの場合
if bool_login :
    
    print()
    print('-- 株価の照会 ファイル読み込み、ファイル書き出し-------------------------------------------------------------')
    # マニュアル「ｅ支店・ＡＰＩ、ブラウザからの利用方法」の「時価」シートの時価関連情報取得サンプル
    # ３．利用方法（２）時価関連情報の取得
    # https://10.62.26.91/e_api_v4r2/request/MDExNDczNTEwMDQwNi05MS02NDU1NA==/?{"p_no":"20","p_sd_date":"2021.06.04-14:56:50.000",
    # "sCLMID":"CLMMfdsGetMarketPrice","sTargetIssueCode":"6501,6501,101","sTargetColumn":"pDPP,tDPP:T,pPRP","sJsonOfmt":"5"}
    # この例を参考に投げるurlを作成する。

    req_item = [class_req()]
    my_column = ['']
    my_code = ['']

    # ファイルから取得する情報コードと銘柄を読み込む。
    func_read_price_list(str_fname_input, my_code, my_column)

    # 株価情報の出力ファイルに１行目タイトルを書き込む。
    func_write_price_title(str_fname_output, my_column)

    start_time = datetime.datetime.now()    # 開始時刻計測

    str_code_list = ''
    i = 0
    j = 0
    int_set = 0
    # v4r3 より、株価取得は1度に120銘柄までに変更となった。
    while j < len(my_code):
        if len(my_code[j]) > 0 and not my_code[j] == 'stock_code' :
            str_code_list = str_code_list + my_code[j] + ','
        if i >= 119 :
            str_code_list = str_code_list[:-1]
            int_p_no = int_p_no + 1
            # 株価を取得。
            json_return = func_get_price(int_p_no, str_code_list, my_column, class_cust_property)
            # 株価情報部分を辞書型で抜き出す。
            dic_return = json_return.get('aCLMMfdsMarketPrice')

            # 取得した株価情報を追記モードでファイルに書き込む。
            func_write_price_list(str_fname_output, dic_return, my_column)

            # 120銘柄で初期化            
            i = 0
            int_set = int_set + 1
            str_code_list = ''
        else:
            i = i + 1
        j = int_set * 120 + i
        
    if len(str_code_list) > 0 :
        str_code_list = str_code_list[:-1]
        int_p_no = int_p_no + 1
        # 株価を取得。
        json_return = func_get_price(int_p_no, str_code_list, my_column, class_cust_property)

        finish_time = datetime.datetime.now()    # 終了時刻計測
        delta_time = finish_time - start_time
        print('delta_time= ', delta_time, ' ← 株価取得時間')

        # 株価情報部分を辞書型で抜き出す。
        dic_return = json_return.get('aCLMMfdsMarketPrice')

        # 取得した株価情報を追記モードでファイルに書き込む。
        func_write_price_list(str_fname_output, dic_return, my_column)



    print()
    print('-- logout -------------------------------------------------------------')
    # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p3/46 No.3 引数名:CLMAuthLogoutRequest を参照してください。
    int_p_no = int_p_no + 1
    bool_logout = func_logout(int_p_no, class_cust_property)
   
else :
    print('ログインに失敗しました')
