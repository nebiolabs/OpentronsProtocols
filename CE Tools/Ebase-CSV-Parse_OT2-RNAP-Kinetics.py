import pandas
import statistics
import openpyxl

#Takes list of [input file directories], list of [time points], and 8 [column names]
#Returns dictionary of organized data tables 0 indexed
def Get1Enzyme(Files, tps, cols):
    PlateNum = 0
    DataDict = {}
    for file in Files:
        with open(file, 'r') as csv_file:
            RawData = pandas.read_csv(csv_file)
            Bin3 = RawData["Bin3 : B"]
            Bin3 = [float(Bin3[n].strip('%'))/ 100.0 for n in range(len(Bin3))]
            sortBin3 = {}
            for m in range(8):
                sortBin3[m] = [Bin3[n] for n in range(0+m, len(Bin3), 8)]
            Enzyme = pandas.DataFrame(sortBin3)
            Enzyme.columns = cols
            Enzyme.index = [str(n) for n in tps]
        csv_file.close()
        DataDict[PlateNum] = Enzyme
        PlateNum = PlateNum + 1
    return(DataDict)

#Takes list of [input file directories], list of [time points], and 4 [column names]
#Returns dictionary of dictionaries of organized data tables 0 indexed->'Rxn A/B'
def Get2Enzyme(Files, tps, cols):
    PlateNum = 0
    DataDict = {}
    for file in Files:
        with open(file, 'r') as csv_file:
            RawData = pandas.read_csv(csv_file)
            Bin3 = RawData["Bin3 : B"]
            Bin3 = [float(Bin3[n].strip('%'))/ 100.0 for n in range(len(Bin3))]
            sortBin3 = {}
            for m in range(8):
                sortBin3[m] = [Bin3[n] for n in range(0+m, len(Bin3), 8)]
            EnzymeA = pandas.DataFrame([sortBin3[n] for n in range(0,4)]).T
            EnzymeB = pandas.DataFrame([sortBin3[n] for n in range(4,8)]).T
            EnzymeA.columns = cols
            EnzymeA.index = [str(n) for n in tps]
            EnzymeB.columns = cols
            EnzymeB.index = [str(n) for n in tps]
        csv_file.close()
        Rxns = {}
        Rxns['Rxn A'] = EnzymeA
        Rxns['Rxn B'] = EnzymeB
        DataDict[PlateNum] = Rxns
        PlateNum = PlateNum + 1
    return(DataDict)

#Takes list of [input file directories], list of [time points], and 8 [column names]
#Returns list of 2 organized data tables: Average and Standard Deviation
def Analyze1Enzyme(Files, tps, cols):
    Data = Get1Enzyme(Files, tps, cols)
    AverageDict = {}
    for i in cols:
        AverageDict[i] = [statistics.mean([Data[k][i][j] for k in range(len(Data))]) for j in range(len(tps))]
    AverageTab = pandas.DataFrame(AverageDict)
    AverageTab.columns = ['Ave' + n for n in cols] 
    AverageTab.index = [str(n) for n in tps]
    SdevDict = {}
    for i in cols:
        SdevDict[i] = [statistics.stdev([Data[k][i][j] for k in range(len(Data))]) for j in range(len(tps))]
    SdevTab = pandas.DataFrame(SdevDict)
    SdevTab.columns = ['Sdev' + n for n in cols] 
    SdevTab.index = [str(n) for n in tps]
    return([AverageTab, SdevTab])

#Takes list of [input file directories], list of [time points], and 8 [column names]
#Returns dictionary of lists of 2 organized data tables: Average and Standard Deviation indexed by 'Rxn A/B'
def Analyze2Enzyme(Files, tps, cols):
    Data = Get2Enzyme(Files, tps, cols)
    AverageDict1 = {}
    for i in cols:
        AverageDict1[i] = [statistics.mean([Data[k]['Rxn A'][i][j] for k in range(len(Data))]) for j in range(len(tps))]
    AverageDict2 = {}
    for i in cols:
        AverageDict2[i] = [statistics.mean([Data[k]['Rxn B'][i][j] for k in range(len(Data))]) for j in range(len(tps))]
    AverageTab1 = pandas.DataFrame(AverageDict1)
    AverageTab1.columns = ['Ave' + n for n in cols] 
    AverageTab1.index = [str(n) for n in tps]
    AverageTab2 = pandas.DataFrame(AverageDict2)
    AverageTab2.columns = ['Ave' + n for n in cols] 
    AverageTab2.index = [str(n) for n in tps]
    SdevDict1 = {}
    for i in cols:
        SdevDict1[i] = [statistics.stdev([Data[k]['Rxn A'][i][j] for k in range(len(Data))]) for j in range(len(tps))]
    SdevTab1 = pandas.DataFrame(SdevDict1)
    SdevTab1.columns = ['Sdev' + n for n in cols] 
    SdevTab1.index = [str(n) for n in tps]
    SdevDict2 = {}
    for i in cols:
        SdevDict2[i] = [statistics.stdev([Data[k]['Rxn B'][i][j] for k in range(len(Data))]) for j in range(len(tps))]
    SdevTab2 = pandas.DataFrame(SdevDict2)
    SdevTab2.columns = ['Sdev' + n for n in cols] 
    SdevTab2.index = [str(n) for n in tps]
    AveSdevDict = {}
    AveSdevDict['Rxn A'] = [AverageTab1, SdevTab1]
    AveSdevDict['Rxn B'] = [AverageTab2, SdevTab2]
    return(AveSdevDict)

#Takes list of csv files, list of 12 kinetics timepoints, list of labels for 8 experiments, desired excel file name, and desired raw/analyzed data sheet names
#Prints concatenated + analzed data to excel file
def Print1Enzyme(CSV, timepoints, labels, name, SheetName1, SheetName2):
    RawData = Get1Enzyme(CSV, timepoints, labels)
    RawData = pandas.concat(RawData, axis = 1)
    AnzData = Analyze1Enzyme(CSV, timepoints, labels)
    AnzData = pandas.concat(AnzData, axis = 1)
    with pandas.ExcelWriter(name) as writer:
        RawData.to_excel(writer, sheet_name = SheetName1)
        AnzData.to_excel(writer, sheet_name = SheetName2)

#Takes list of csv files, list of 12 kinetics timepoints, list of labels for 4 experiments, desired excel file name, and desired raw/analyzed data sheet names
#Prints concatenated + analzed data to excel file
def Print2Enzyme(CSV, timepoints, labels, name, SheetName1, SheetName2):
    RawData = Get2Enzyme(CSV, timepoints, labels)
    RawData = [pandas.concat(RawData[n], axis = 1) for n in RawData]
    RawData = pandas.concat(RawData, axis = 1)
    AnzData = Analyze2Enzyme(CSV, timepoints, labels)
    AnzData = [pandas.concat(AnzData[n], axis = 1) for n in AnzData]
    AnzData = pandas.concat(AnzData, axis = 1)
    with pandas.ExcelWriter(name) as writer:
        RawData.to_excel(writer, sheet_name = SheetName1)
        AnzData.to_excel(writer, sheet_name = SheetName2)

#To print to Excel file, Run appropriate "PrintXEnzyme" function as follows:

Timepoints = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
Labels = ["Label1", "Label2", "Label3", "Label4"] # or [..., "Label5", "Label6", "Label7", "Label8"] for 1 enzyme
CSVFiles = [r"Plate1.csv", r"Plate2.csv"]
Excel = "ExcelName.xlsx"
Sheet1 = "Raw Data sheet name"
Sheet2 = "Analyzed Data sheet name"

Print2Enzyme(CSVFiles, Timepoints, Labels, Excel, Sheet1, Sheet2)

