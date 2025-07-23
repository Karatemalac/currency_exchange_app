from mnb import Mnb
import os
import pandas as pd
import datetime
from configFiles import validateKeys

changeDate = ""
# print(configFilePath)

def convertValues(values):
    newValues = []
    for value in values:
        if(value == "None" or value== ""):
            newValues.append(None)
        else:
            try:
                newValues.append(int(value))
            except ValueError:
                newValues.append(str(value))

    return(newValues)

def readDataFrame(csvPath: os.path, configKeys: list) -> tuple[list[datetime.date], list[float], list[list]]:
    configKeys = convertValues(configKeys)
    try:
        df = pd.read_csv(csvPath, on_bad_lines='skip', na_filter=False, sep=configKeys[0], skiprows=configKeys[1], header=configKeys[2], encoding=configKeys[3])
    except Exception as e:
        print("One of the parameters is invalid or wrong!")

    # print(f"DataFrame:\n{df.shape}")

    startRow = int(configKeys[4]) - 1
    dateColumn = int(configKeys[5]) - 1
    amountColumn = int(configKeys[6]) - 1

    dfDate = df.iloc[startRow:, dateColumn]
    dfAmount = df.iloc[startRow:, amountColumn]
    dfDateList = dfDate.values.tolist()
    dfAmountList = [float(x.replace(".", "").replace(',', '.')) for x in dfAmount.values.tolist()]
    dfAmountList = [abs(x) for x in dfAmountList]

    return(dfDateList, dfAmountList, validateKeys(df, configKeys[7:], startRow))

def getRate(startDate: datetime.date, endDate: datetime.date) -> list:
    # API FORMAT
    # [Day(date=datetime.date(2025, 6, 20), rates=[Rate(currency='EUR', rate=402.74)])
    global changeDate
    formatDMY = f"%d.%m.%Y"
    formatYMD = f"%Y.%m.%d"
    while True:
        try:
            client = Mnb()
            try:
                startDate = datetime.datetime.strptime(startDate, formatDMY).date()
                endDate = datetime.datetime.strptime(endDate, formatDMY).date()
                changeDate = True
            except ValueError:
                startDate = datetime.datetime.strptime(startDate, formatYMD).date()
                endDate = datetime.datetime.strptime(endDate, formatYMD).date()
                changeDate = False
            # exchangeDate = datetime.date(2025, 6, 27)
            foreignRates = client.get_exchange_rates(startDate, endDate, ["EUR", "USD"]) or client.get_exchange_rates(endDate, startDate, ["EUR", "USD"])
            rate = foreignRates[0].date
            # print(rate)
            # print(foreignRates[1].rates[1].rate)
            # print(foreignRates)
            return(foreignRates)
        except IndexError:
            print("Rate not available, weekend or holiday")
            continue

def getNearestDate(dateList: list[datetime.date], date: datetime.date) -> datetime.date:
    nearestDate = min(dateList, key=lambda x: (x>date, abs(x - date)))
    # print(nearestDate)
    return(nearestDate)

def convertAndGetLists(dateList: list[datetime.date], amountList: list[float], otherLists: list[list]) -> tuple[list[datetime.date], list[None], list[float], list[float], list[list]]:
    currencyIndexes = {"EUR": 0, "USD": 1}
    foreignRates = getRate(dateList[0], dateList[len(dateList)-1])
    indexCounter = 0
    dataLength = len(dateList)
    emptyColumnList = [None] * dataLength
    foreignRateDateList = []
    dateListNew = []
    hufAmounts = []
    for x in range(len(foreignRates)):
        foreignRateDate = str(foreignRates[x].date).replace("-", ".")
        foreignRateDate = datetime.datetime.strptime(foreignRateDate, f"%Y.%m.%d").date()
        if(not foreignRateDate in foreignRateDateList):
            foreignRateDateList.append(foreignRateDate)
            # print(foreignRateDate)
    for date in dateList:
        currentCurrency = str(otherLists[2][indexCounter])
        if(changeDate):
            date = date.split(".")
            date[0], date[2] = date[2], date[0]
            date = ".".join(date)
            dateListNew.append(date)
        date = datetime.datetime.strptime(date, f"%Y.%m.%d").date()
        if(currentCurrency in currencyIndexes):
            if(date in foreignRateDateList):
                amountHuf = round(foreignRates[foreignRateDateList.index(date)].rates[currencyIndexes[currentCurrency]].rate * amountList[indexCounter], 0)
                hufAmounts.append(amountHuf)
                # elif(not date in foreignRateDateList):
                #     print(indexCounter)
                #     amountHuf = round(foreignRates[x-1].rates[0].rate * amountList[indexCounter], 0)
                #     hufAmounts.append(amountHuf)
                #     break
            else:
                amountHuf = round(foreignRates[foreignRateDateList.index(getNearestDate(foreignRateDateList, date))].rates[currencyIndexes[currentCurrency]].rate * amountList[indexCounter], 0)
                hufAmounts.append(amountHuf)
                # print(date)
                # print(getNearestDate(foreignRateDateList, date))
        # print(date)
        # print(datetime.datetime.strptime("1", f"%d").date())
        elif(currentCurrency == "HUF"):
            hufAmounts.append(amountList[indexCounter])
        else:
            hufAmounts.append("")
        indexCounter += 1
        continue
    print(len(dateList), len(emptyColumnList), len(hufAmounts), len(amountList))
    return(dateListNew, emptyColumnList, hufAmounts, amountList, otherLists)

def createExcel(csvPath: os.path, dateList: list[datetime.date], emptyColumnList: list[None], hufAmounts: list[float], amountList: list[float], otherLists: list[list]):
    dfHuf = pd.DataFrame({"Dátum": dateList, "Megnevezés": otherLists[1] or emptyColumnList, "Bizonylatjel": otherLists[0] or emptyColumnList, "Összeg": hufAmounts, "Tartozik": emptyColumnList, "Kovetel": emptyColumnList, "KTGHELY": emptyColumnList, "Tartozik megnevezés": emptyColumnList, "Követel megnevezés": emptyColumnList, "Deviza összeg": amountList, "Deviza kód": otherLists[2]})
    finishedExcelPath = os.path.join(os.path.dirname(__file__), "../", "Excels")
    if(not os.path.isdir(finishedExcelPath)):
        os.mkdir(finishedExcelPath)
    dfHuf.to_excel(os.path.join(finishedExcelPath, os.path.basename(csvPath)[:-3] + "xlsx"), index = False)

def addCsvToList(csvPath: os.path, csvFilesList: list):
    csvFilesList.append(csvPath)
    return(csvFilesList)
    