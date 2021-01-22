import _sqlite3
import json
from datetime import datetime
import os
import shutil
import pandas as pd
import re
from application_logging.logger import App_Logger

class Raw_Data_Validation:
    def __init__(self,path):
        self.Batch_Directory = path
        self.schema_path = 'schema_training.json'
        self.logger = App_Logger()

    def values_from_schema(self):
        try:
            with open(self.schema_path,'r') as f:
                dic = json.load(f)
                f.close()
            pattern = dic['SampleFileName']
            LengthOfDateStampInFile = dic['LengthOfDateStampInFile']
            LengthOfTimeStampInFile = dic['LengthOfTimeStampInFile']
            columns_name = dic['ColName']
            NumberofColumns = dic['NumberofColumns']

            file = open('Training_Logs/valuesfromschemaValidationLog.txt','a+')
            #message ='LengthOfDateStampFile::%s' %LengthOfDateStampInFile% + '\t' + 'LengthOfTimeStampFile::%s' %LengthOfTimeStampInFile% + '\t' + 'NumberofColumns::%s' %Numberofcolumns% + '\n'
            message = "LengthOfDateStampInFile:: %s" % LengthOfDateStampInFile + "\t" + "LengthOfTimeStampInFile:: %s" % LengthOfTimeStampInFile + "\t " + "NumberofColumns:: %s" % NumberofColumns + "\n"
            self.logger.log(file,message)
            file.close()

        except ValueError:
            file = open('Training_Logs/valuesfromschemaValidationLog.txt','a+')
            self.logger.log(file,'Value Error:Value not Found inside schema_training.json')
            file.close()
            raise ValueError

        except KeyError:
            file = open('Training_Logs/valuesfromschemaValidationLog.txt', 'a+')
            self.logger.log(file, 'Key Error:Key Value Error Incorrect key passed')

        except Exception as e:
            file = open('Training_Logs/valuesfromschemaValidationLog.txt', 'a+')
            self.logger.log(file, str(e))
            file.close()
            raise e
        return LengthOfDateStampInFile,LengthOfTimeStampInFile,columns_name,NumberofColumns


    def manualRegexCreation(self):
        regex = "['wafer']+['\_'']+[\d_]+[\d]+\.csv"
        return  regex


    def createDirectoryForGoodBadRawData(self):
        try:
            path = os.path.join("Training_Raw_files_validated/", "Good_Raw/")
            if not os.path.isdir(path):
                os.makedirs(path)

            path = os.path.join("Training_Raw_files_validated/", "Bad_Raw/")
            if not os.path.isdir(path):
                os.makedirs(path)

        except OSError as ex:
            file = open("Training_Logs/GeneralLog.txt", 'a+')
            self.logger.log(file,'Error while creating directory %s' % ex)
            file.close()
            raise OSError

    def deleteExistingGoodDataTrainingFolder(self):
        try:
            path = 'Training_Raw_file_validated/'
            if os.path.isdir(path + 'Good_Raw/'):
                shutil.rmtree(path + 'Good_Raw/')
                file = open('Training_Logs/General_Log.txt','a+')
                self.logger.log(file,'Good Raw directory delete successfully!!!')
                file.close()
        except OSError as ex:
            file = open('Training_Logs/General_Log.txt','a+')
            self.logger.log(file,'Error while deleting Directory: %s' % s)
            file.close()
            raise OSError

    def deleteExistingBadDataTrainingFolder(self):
        try:
            path = 'Training_Raw_file_validated/'
            if os.path.isdir(path + 'Bad_Raw/'):
                shutil.rmtree(path + 'Bad_Raw/')
                file = open('Training_Logs/General_Log.txt','a+')
                self.logger.log(file,'Bad Raw directory delete successfully!!!')
                file.close()
        except OSError as ex:
            file = open('Training_Logs/General_Log.txt','a+')
            self.logger.log(file,'Error while deleting Directory: %s' % s)
            file.close()
            raise OSError


    def moveBadFilesToArchiveBad(self):
        now = datetime.now()
        date = now.date()
        time = now.strftime("%H%M%S")
        try:
            source = 'Training_Raw_files_validation/BadRaw/'
            if os.path.isdir(source):
                path = "TrainingArchiveBadData"
                if not os.path.isdir(path):
                    os.makedirs(path)
                dest = 'TrainingArchiveBadData/BadData_' + str(date)+"_"+str(time)

                if not os.path.isdir(dest):
                    os.makedirs(dest)
                files = os.listdir(source)
                for f in files:
                    if f not in os.listdir(dest):
                        shutil.move(source + f, dest)
                file = open("Training_Logs/GeneralLog.txt", 'a+')
                self.logger.log(file,'Bad files moved to archive')
                path = 'Training_Raw_files_validated/'
                if os.path.isdir(path + 'Bad_Raw/'):
                    shutil.rmtree(path + 'Bad_Raw/')
                self.logger.log(file,'Bad Raw file Data Folder Deleted Successfully!!')
                file.close()
        except Exception as e:
            file = open("Training_Logs/GeneralLog.txt", 'a+')
            self.logger.log(file, "Error while moving bad files to archive:: %s" % e)
            file.close()
            raise e


    def validationFileNameRaw(self,regex,LengthOfDateStampInFile,LengthOfTimeStampInFile):

        #pattern = "['Wafer']+['\_'']+[\d_]+[\d]+\.csv"
        # delete the directories for good and bad data in case last run was unsuccessful and folders were not deleted.
        self.deleteExistingBadDataTrainingFolder()
        self.deleteExistingGoodDataTrainingFolder()
        self.createDirectoryForGoodBadRawData()
        onlyfiles = [f for f in os.listdir(self.Batch_Directory)]
        try:
            f = open("Training_Logs/nameValidationLog.txt", 'a+')
            for filename in onlyfiles:
                if (re.match(regex, filename)):
                    splitAtDot = re.split('.csv', filename)
                    splitAtDot = (re.split('_', splitAtDot[0]))
                    if len(splitAtDot[1]) == LengthOfDateStampInFile:
                        if len(splitAtDot[2]) == LengthOfTimeStampInFile:
                            shutil.copy("Training_Batch_Files/" + filename, "Training_Raw_files_validated/Good_Raw")
                            self.logger.log(f,"Valid File name!! File moved to GoodRaw Folder :: %s" % filename)

                        else:
                            shutil.copy("Training_Batch_Files/" + filename, "Training_Raw_files_validated/Bad_Raw")
                            self.logger.log(f,"Invalid File Name!! File moved to Bad Raw Folder :: %s" % filename)
                    else:
                        shutil.copy("Training_Batch_Files/" + filename, "Training_Raw_files_validated/Bad_Raw")
                        self.logger.log(f,"Invalid File Name!! File moved to Bad Raw Folder :: %s" % filename)
                else:
                    shutil.copy("Training_Batch_Files/" + filename, "Training_Raw_files_validated/Bad_Raw")
                    self.logger.log(f, "Invalid File Name!! File moved to Bad Raw Folder :: %s" % filename)

            f.close()

        except Exception as e:
            f = open("Training_Logs/nameValidationLog.txt", 'a+')
            self.logger.log(f, "Error occured "
                               "while validating FileName %s" % e)
            f.close()
            raise e



    def validateColumnLength(self,NumberofColumns):
        try:
            f = open("Training_Logs/columnValidationLog.txt", 'a+')
            self.logger.log(f,"Column Length Validation Started!!")
            for file in os.listdir('Training_Raw_files_validated/Good_Raw/'):
                csv = pd.read_csv("Training_Raw_files_validated/Good_Raw/" + file)
                if csv.shape[1] == NumberofColumns:
                    pass
                else:
                    #shutil.move("Training_Raw_files_validated/Good_Raw/" + file, "Training_Raw_files_validated/Bad_Raw")
                    shutil.move("Training_Raw_files_validated/Good_Raw/" + file, "Training_Raw_files_validated/Bad_Raw")
                    self.logger.log(f, "Invalid Column Length for the file!! File moved to Bad Raw Folder :: %s" % file)
            self.logger.log(f, "Column Length Validation Completed!!")
        except OSError:
            f = open("Training_Logs/columnValidationLog.txt", 'a+')
            self.logger.log(f, "Error Occured while moving the file :: %s" % OSError)
            f.close()
            raise OSError
        except Exception as e:
            f = open("Training_Logs/columnValidationLog.txt", 'a+')
            self.logger.log(f, "Error Occured:: %s" % e)
            f.close()
            raise e
        f.close()

    def validateMissingValuesInWholeColumn(self):
        try:
            f = open("Training_Logs/missingValuesInColumn.txt", 'a+')
            self.logger.log(f,"Missing Values Validation Started!!")

            for file in os.listdir('Training_Raw_files_validated/Good_Raw/'):
                csv = pd.read_csv("Training_Raw_files_validated/Good_Raw/" + file)
                count = 0
                for columns in csv:
                    if (len(csv[columns]) - csv[columns].count()) == len(csv[columns]):
                        count+=1
                        shutil.move("Training_Raw_files_validated/Good_Raw/" + file,
                                    "Training_Raw_files_validated/Bad_Raw")
                        self.logger.log(f,"Invalid Column Length for the file!! File moved to Bad Raw Folder :: %s" % file)
                        break
                if count==0:
                    csv.rename(columns={"Unnamed: 0": "Wafer"}, inplace=True)
                    csv.to_csv("Training_Raw_files_validated/Good_Raw/" + file, index=None, header=True)
        except OSError:
            f = open("Training_Logs/missingValuesInColumn.txt", 'a+')
            self.logger.log(f, "Error Occured while moving the file :: %s" % OSError)
            f.close()
            raise OSError
        except Exception as e:
            f = open("Training_Logs/missingValuesInColumn.txt", 'a+')
            self.logger.log(f, "Error Occured:: %s" % e)
            f.close()
            raise e
        f.close()














