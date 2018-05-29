import requests, imp, sys, json, datetime, pymysql, config
from bs4 import BeautifulSoup
imp.reload(sys)

db = pymysql.connect(host=config.db_host, user=config.db_user, password=config.db_password,
                     db=config.db_name, port=config.db_port, charset="utf8")
cursor = db.cursor()

url = "http://www.fpcc.com.tw/tc/affiliate.php"

def requests_Get(url):
    res = requests.get(url, verify=False)
    res.encoding = "utf-8"
    soup = BeautifulSoup(res.text, "html.parser")
    return soup

soup = requests_Get(url)

# 日期(年-月-日)
def todayDate():
    time = datetime.datetime.now().strftime("%Y-%m-%d")
    return time

time = todayDate()

oilNameDict = {}

# 多筆Insert
sqlInsert = "INSERT INTO oil_info(oilDate, companyName, productName, price, unit) VALUES"

# for迴圈跑 4 次撈資料(98,95,92,超柴), 因為 class 命名的關係所以從 [1] 開始
for i in range(1, 5):
    oilData = soup.find("div", class_="GasPrice" + str(i))
    a = oilData.find("h3").text
    oilName = a.replace(" ", "")
    oilName = oilName.replace("\n", "")
    oilPrice = oilData.find("p", class_="pricing").text
    oilPrice = oilPrice.replace("$", "")
    oilUnit = oilData.find("p", class_="pricing_b").text

    # 統一名稱
    def modify_oilName(oilName):
        if(oilName[0] == "９" or oilName[0] == "9"):
            if(oilName[1] == "２" or oilName[1] == "2"):
                oilName = "92無鉛汽油"
                return oilName
            elif(oilName[1] == "５" or oilName[1] == "5"):
                oilName = "95無鉛汽油"
                return oilName
            elif(oilName[1] == "８" or oilName[1] == "8"):
                oilName = "98無鉛汽油"
                return oilName
        else:
            return oilName

    oilName = modify_oilName(oilName)

    # 調整單位格式
    def modify_oilUnit(oilUnit):
        oilUnit = oilUnit.replace(" ", "")
        return oilUnit

    oilUnit = modify_oilUnit(oilUnit)

    # 多筆Insert
    sqlInsert += "('{}', '{}', '{}', '{}', '{}'),".format(time, "fpcc", oilName, oilPrice, oilUnit)


    item ={
        "price": oilPrice,
        "unit": oilUnit
    }
    oilNameDict[oilName] = item   
"""
    print("-----start-----")
    
    print("名稱：{}\n油價：{}\n單位：{}".format(oilName, oilPrice, oilUnit))
    
    print("------end------")
"""

sqlInsert = sqlInsert[0:-1]
print(sqlInsert)
cursor.execute(sqlInsert)
db.commit()
db.close()

# fpcc 為台塑石化英文簡稱
companyNameDict = {"fpcc": oilNameDict}
oilDataDict = {time: companyNameDict}
