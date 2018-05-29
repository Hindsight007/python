import requests, sys, imp, datetime, json, pymysql,config
from bs4 import BeautifulSoup
imp.reload(sys)

db = pymysql.connect(host=config.db_host, user=config.db_user, password=config.db_password,
                     db=config.db_name, port=config.db_port, charset="utf8")
cursor = db.cursor()

# 因為編碼問題，這一行一定要用，將系統環境調整為 UTF-8
# sys.setdefaultencoding('utf-8')
url = "https://new.cpc.com.tw/Home/"

def requests_Get(url):
    res = requests.get(url, verify=False)
    res.encoding = "utf-8"
    soup = BeautifulSoup(res.text, "html.parser")
    return soup

soup = requests_Get(url)

oilData = soup.find(id="OilPrice2")
oilDetailAll = oilData.find_all("dd")

# 日期(年-月-日)
def todayDate():
    time = datetime.datetime.now().strftime("%Y-%m-%d")
    return time

time = todayDate()

oilNameDict={}

# 多筆Insert
sqlInsert = "INSERT INTO oil_info(oilDate, companyName, productName, price, unit) VALUES"

# for迴圈跑 5 次撈資料(98, 92, LGP, 超柴, 95)
for j in range(6):
    oilDetailOne = oilDetailAll[j]
    oilPrice = oilDetailOne.find_all("strong")[0].text  
    oilUnit = oilDetailOne.find_all("span")[0].text  
    oilName = oilDetailOne.text
    oilName = oilName.split(oilUnit)[0]
    oilName = oilName.split(oilPrice)[0]  

    # 統一名稱
    def modify_oilName(oilName):
        if(oilName[0] == "９" or oilName[0] == "9"):
            if(oilName[1] == "２" or oilName[1] == "2"):
                oilName = "92無鉛汽油"
                return oilName
            elif(oilName[1] == "５" or oilName[0] == "5"):
                oilName = "95無鉛汽油"
                return oilName
            elif(oilName[1] == "８" or oilName[0] == "8"):
                oilName = "98無鉛汽油"
                return oilName
        else:
            return oilName

    oilName = modify_oilName(oilName)       

    # 多筆Insert
    sqlInsert += "('{}', '{}', '{}', '{}', '{}'),".format(time, "cpc", oilName, oilPrice, oilUnit)

    # 放入Dict
    item = {"price": oilPrice,
            "unit": oilUnit
           }
    oilNameDict[oilName] = item

sqlInsert = sqlInsert[0:-1]
print(sqlInsert)
cursor.execute(sqlInsert)
db.commit()
db.close()

# cpc 為中油英文簡稱 
companyNameDict = {"cpc": oilNameDict}
oilDataDict = {time: companyNameDict}
