from mnb import Mnb
import os
from tkinter import *
from tkinter import filedialog
import pandas as pd
import datetime
from configFiles import newBankConfig, getKeys, returnConfigsList, validateKeys, editBankConfig
# ADD DIFFFERENT CURRENCIES LATER  
changeDate = ""
csvPath = ""
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

def openCSV(buttonInput):
    global csvPath
    previousPath = csvPath
    csvPath = filedialog.askopenfilename(filetypes=(("CSV Files", "*.csv"),))
    if(not csvPath == ""):
        buttonInput.config(text=csvPath)
        return(csvPath)
    else:
        csvPath = previousPath
        return(previousPath)

def addNewBank():
    openAddBankWindows()

def editBank(bankToEdit):
    if(bankToEdit in returnConfigsList()):
        openEditBankWindow(bankToEdit)

def ok(choosenConfig, window):
    choosenBank = choosenConfig
    if((not choosenBank == "Bank") and (not csvPath == "")):
        try:
            createExcel(*convertAndGetLists(*readDataFrame(getKeys(choosenBank))))
        except Exception as e:
            print(e)
        # window.destroy()

def readDataFrame(configKeys: list):
    configKeys = convertValues(configKeys)
    try:
        df = pd.read_csv(csvPath, on_bad_lines='skip', na_filter=False, sep=configKeys[0], skiprows=configKeys[1], header=configKeys[2], encoding=configKeys[3])
    except Exception:
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

def getRate(startDate, endDate):
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
            eurRates = client.get_exchange_rates(startDate, endDate, ["EUR"]) or client.get_exchange_rates(endDate, startDate, ["EUR"])
            rate = eurRates[0].date
            # print(rate)
            # print(eurRates[1].rates[1].rate)
            return(eurRates)
        except IndexError:
            print("Rate not available, weekend or holiday")
            continue

def getNearestDate(dateList, date) -> datetime.date:
    nearestDate = min(dateList, key=lambda x: (x>date, abs(x - date)))
    # print(nearestDate)
    return(nearestDate)

def convertAndGetLists(dateList, amountList, otherLists: list):
    eurRates = getRate(dateList[0], dateList[len(dateList)-1])
    indexCounter = 0
    dataLength = len(dateList)
    emptyColumnList = [None] * dataLength
    eurRateDateList = []
    dateListNew = []
    hufAmounts = []
    for x in range(len(eurRates)):
        eurRateDate = str(eurRates[x].date).replace("-", ".")
        eurRateDate = datetime.datetime.strptime(eurRateDate, f"%Y.%m.%d").date()
        if(not eurRateDate in eurRateDateList):
            eurRateDateList.append(eurRateDate)
            # print(eurRateDate)
    for date in dateList:
        if(changeDate):
            date = date.split(".")
            date[0], date[2] = date[2], date[0]
            date = ".".join(date)
            dateListNew.append(date)
        date = datetime.datetime.strptime(date, f"%Y.%m.%d").date()
        if(date in eurRateDateList):
            amountHuf = round(eurRates[eurRateDateList.index(date)].rates[0].rate * amountList[indexCounter], 0)
            hufAmounts.append(amountHuf)
            # elif(not date in eurRateDateList):
            #     print(indexCounter)
            #     amountHuf = round(eurRates[x-1].rates[0].rate * amountList[indexCounter], 0)
            #     hufAmounts.append(amountHuf)
            #     break
        else:
            amountHuf = round(eurRates[eurRateDateList.index(getNearestDate(eurRateDateList, date))].rates[0].rate * amountList[indexCounter], 0)
            hufAmounts.append(amountHuf)
            # print(date)
            # print(getNearestDate(eurRateDateList, date))
        # print(date)
        # print(datetime.datetime.strptime("1", f"%d").date())
        indexCounter += 1
    print(len(dateList), len(emptyColumnList), len(hufAmounts), len(amountList))
    return(dateListNew, emptyColumnList, hufAmounts, amountList, otherLists)

def createExcel(dateList, emptyColumnList, hufAmounts, amountList, otherLists):
    dfHuf = pd.DataFrame({"Dátum": dateList, "Megnevezés": otherLists[1] or emptyColumnList, "Bizonylatjel": otherLists[0] or emptyColumnList, "Összeg": hufAmounts, "Tartozik": emptyColumnList, "Kovetel": emptyColumnList, "KTGHELY": emptyColumnList, "Tartozik megnevezés": emptyColumnList, "Követel megnevezés": emptyColumnList, "Deviza összeg": amountList, "Deviza kód": "EUR"})
    finishedExcelPath = os.path.join(os.path.dirname(__file__), "Excels", os.path.basename(csvPath)[:-3] + "xlsx")
    dfHuf.to_excel(finishedExcelPath, index = False)

def startProgram():
    bankConfigs = returnConfigsList()
    window = Tk()
    choosenConfig = StringVar(window)
    choosenConfig.set("Bank")
    window.geometry("400x120")
    window.title("Bank Konvertáló")
    buttonInput = Button(text="Input CSV", command=lambda: openCSV(buttonInput))
    buttonInput.pack()
    dropDownList = OptionMenu(window, choosenConfig, *bankConfigs or ["Bank"])
    dropDownList.pack()
    functionFrame = Frame(window)
    functionFrame.pack()
    buttonAddBank = Button(functionFrame, text="Add New Bank", command=addNewBank)
    buttonAddBank.pack(side=LEFT)
    editButton = Button(functionFrame, text="Edit Bank", command=lambda: editBank(choosenConfig.get()))
    editButton.pack(side=LEFT)
    buttonOK = Button(text="OK", command=lambda: ok(choosenConfig.get(), window))
    buttonOK.pack()
    window.mainloop()

def openAddBankWindows():
    addWindow = Tk()
    addWindow.title("New Bank")
    addWindow.geometry("300x300")
    Label(addWindow, text="Bank Name").grid(row=0)
    bankName = Entry(addWindow)
    bankName.grid(row=0, column=1)
    Label(addWindow, text="Separator").grid(row=1)
    separator = Entry(addWindow)
    separator.grid(row=1, column=1)
    Label(addWindow, text="Skips_Rows").grid(row=2)
    skipRows = Entry(addWindow)
    skipRows.grid(row=2, column=1)
    Label(addWindow, text="Header").grid(row=3)
    header = Entry(addWindow)
    header.grid(row=3, column=1)
    Label(addWindow, text="Encoding").grid(row=4)
    encoding = Entry(addWindow)
    encoding.grid(row=4, column=1)
    Label(addWindow, text="Start_Row").grid(row=5)
    startRow = Entry(addWindow)
    startRow.grid(row=5, column=1)
    Label(addWindow, text="Date_Column").grid(row=6)
    dateColumn = Entry(addWindow)
    dateColumn.grid(row=6, column=1)
    Label(addWindow, text="Amount_Column").grid(row=7)
    amountColumn = Entry(addWindow)
    amountColumn.grid(row=7, column=1)
    Label(addWindow, text="Receipt_Column").grid(row=8)
    receiptColumn = Entry(addWindow)
    receiptColumn.grid(row=8, column=1)
    addButton = Button(addWindow, text="Add", command=lambda: newBankConfig(bankName.get(), separator.get(), skipRows.get(), header.get(), encoding.get(), startRow.get(), dateColumn.get(), amountColumn.get(), receiptColumn.get()))
    addButton.grid(row=9, column=1)
    addWindow.mainloop()

def openEditBankWindow(bankToEdit):
    editWindow = Tk()
    editWindow.geometry("300x300")
    editWindow.title(f"Edit {bankToEdit}")

startProgram()