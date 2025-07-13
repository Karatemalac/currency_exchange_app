from configparser import ConfigParser
from os import path

config = ConfigParser()
configFilePath = path.join(path.dirname(__file__), "configs", "banks.ini")
# def createConfigFile():
#     config["Test"] = {"Test1": "1", "Test2": "2", "Test3": "3"}
#     config["Test"]["Test4"] = "4"
#     config ["Other"] = {}
#     config["Other"]["Other1"] ="O1"
#     with open(path.join(path.dirname(__file__), "configs", "test.ini"), "w") as configfile:
#         config.write(configfile)
# createConfigFile()
# config.read(path.join(path.dirname(__file__), "configs", "test.ini"))
# print(config.sections())
# print(config["Test"]["Test1"])
def returnConfigsList() -> list:
    config.read(configFilePath)
    return(config.sections())

def createConfigFile():
    if(not path.isfile(configFilePath)):
        # print("Working")
        with open(configFilePath, "w") as configfile:
            pass

def newBankConfig(bankName, separator, skipRows, header, encoding, startRow, dateColumn, amountColumn, receiptColumn, partnerColumn, currencyColumn):
    if(not config.has_section(bankName)):
        config[bankName] = {"Separator": separator, "Skips_Rows": skipRows, "Header": header, "Encoding": encoding, "Start_Row": startRow, "Date_Column": dateColumn, "Amount_Column": amountColumn, "Receipt_Column": receiptColumn, "Partner_Column": partnerColumn, "Currency_Column": currencyColumn}
    with open(configFilePath, "w") as configfile:
        config.write(configfile)

def editBankConfig(choosenBank: str, newValues: list):
    # print(newValues)
    newBankName = newValues[0]
    config[newBankName] = {}
    newValues = newValues[1:]
    newValueCounter = 0
    for key in config[choosenBank]:
        config[newBankName][key] = newValues[newValueCounter]
        newValueCounter +=1
    if(not choosenBank == newBankName):
        config.remove_section(choosenBank)
    with open(configFilePath, "w") as configfile:
        config.write(configfile)

def removeBankConfig(choosenBank: str):
    config.remove_section(choosenBank)
    with open(configFilePath, "w") as configfile:
        config.write(configfile)
    return

def validateKeys(df, configkeys: list, startRow: int) -> list:
    validLists = []
    for x in range(len(configkeys)):
        if(configkeys[x] == None):
            validLists.append(None)
        else:
            column = int(configkeys[x]) - 1
            validColumn = df.iloc[startRow:, column]
            validList = validColumn.values.tolist()
            validLists.append(validList)
    return(validLists)

def getSectionNames() -> list:
    sectionNames = []
    for section in config.defaults():
        sectionNames.append(section)
    return(sectionNames)

def getKeys(choosenBank: str) -> list:
    keys = []
    for key in config[choosenBank]:
        keys.append(config[choosenBank][key])
    return(keys)

createConfigFile()


# if(not getKeys(returnConfigsList()[1])[1]):
#     print("WORKING")
# else:
#     print("NOT WORKING")
# editConfig("Test", "separator", "New")
# newBankConfig("Test", ";", 4, 0, "latin1", 1, 2, 7)