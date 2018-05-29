import requests, sys, imp, datetime, json, pymysql,config
from bs4 import BeautifulSoup
imp.reload(sys)

db = pymysql.connect(host=config.db_host, user=config.db_user, password=config.db_password,
                     db=config.db_name, port=config.db_port, charset="utf8")
cursor = db.cursor()

url = "https://www.npcgas.com.tw/html/oil/index.aspx"

def requests_Get(url):
    res = requests.get(url, verify=False)
    res.encoding = "utf-8"
    soup = BeautifulSoup(res.text, "html.parser")
    return soup

soup = requests_Get(url)

a = soup.find(id="price_92")
b = soup.find(id="price_95")
c = soup.find(id="price_98")
d = soup.find(id="price_oil")

oilPriceList = [a, b, c, d]
oilNameList = ["92無鉛汽油", "95無鉛汽油", "98無鉛汽油", "柴油"]

# 日期(年-月-日)
def todayDate():
    time = datetime.datetime.now().strftime("%Y-%m-%d")
    return time

time = todayDate()

oilNameDict={}

# 多筆Insert
sqlInsert = "INSERT INTO oil_info(oilDate, companyName, productName, price, unit) VALUES"

for i in range(4):
    
    oilName = oilNameList[i]
    oilPrice = oilPriceList[i].text

    # 多筆Insert
    sqlInsert += "('{}', '{}', '{}', '{}', '{}'),".format(time, "npcgas", oilName, oilPrice, "元/公升")

    item = {"price": oilPrice,
            "unit": "元/公升"}
    oilNameDict[oilName] = item

sqlInsert = sqlInsert[0:-1]
print(sqlInsert)
cursor.execute(sqlInsert)
db.commit()
db.close()

companyNameDict = {"npcgas": oilNameDict}
oilDataDict = {time: companyNameDict}