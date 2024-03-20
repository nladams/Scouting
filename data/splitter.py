import sys
import os 

def get_file_and_parents(text_file_of_files,file_index):

    #######################################################################
    #                                                                     #
    # Returns a string which is the file name and a tuple of parent files #
    #                                                                     #
    #######################################################################

    with open(text_file_of_files,"r") as data_files:
        files = data_files.readlines()
        file_name = files[file_index][:-1]

    parent_files = tuple(os.popen(f'dasgoclient -query="parent file={file_name}"').read().split('\n')[:-1])

    return(file_name,parent_files)

"""

params.register('condInputNum',
                0,
                VarParsing.multiplicity.singleton,
                VarParsing.varType.int,
                "the file to run on")

params.register('inputTextFile',
                '',
                VarParsing.multiplicity.singleton,
                VarParsing.varType.string,
                "path to text file with dataset file names")

to run the function, do the following:

file_name, parent_files = get_file_and_parents(params.inputTextFile,params.condInputNum)

cmsRun ak4.py inputTextFile="./test.txt" condInputNum=5 

"""


if __name__ == '__main__':
    
    file_index = int(sys.argv[1])

    file_name, parent_files = get_file_and_parents("./test.txt",file_index)

    print(file_name)
    print(*parent_files)
    

