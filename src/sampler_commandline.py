from sys import argv
import sys, getopt, random

def sample():
    
    #variables the user can input
    inputfile = ''
    outputfile = ''
    pct=0
    chunks=0
    overlap=0
    con=-1 # 0 cannot be used as the unset value, as 0 is accepted input.
    max_percent=0

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'i:o:p:c:a:q:m:max')
    except getopt.GetoptError:
        print 'sampler.py -i <inputfile> -o <outputfile> Exited with error!'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'sampler.py takes the following input \n\n -i <inputfile> This is neccesary \n\n -o <outputfile> If not specified, this will be <inputfile>_out. \n\n -p <percentage> size of sample \n\n -c <number> Short for chunk. Outputs number of samples. This creates <number> of output files. If no percentage is specified, it will default to 100/<number>. Also used with -q. \n\n -q <number> Consequtively larger chunks starting at percentage <number>. Creates <number> files consisting of Consequtively larger chunks, randomly overlapping. Numerically named after <outputfile>. Do not use -p together with this, as you specify the starting percentage directly here. \n\n -max <number> This is the final percentage size of the last sample in a consequtive run (-q)'
            sys.exit()
        elif opt in ("-i"):
            inputfile = str(arg)
        elif opt in ("-o"):
            outputfile = str(arg)
        elif opt in ("-p", "-pct"):
            pct = float(arg)
        elif opt in ("-c", "-chunks"):
            chunks = int(arg)
        elif opt in ("-q", "-consequtive"):
            con = int(arg)
        elif opt in ("-max", "-m"):
            max_percent = int(arg)

    if inputfile=='':
        print 'no input file specified. Use -h to get help.'
        sys.exit() #exits the program. The code can not run with no input-file. Running further will ouput more errors, possibly confusing the user.
    print 'Input file is ', inputfile
    if outputfile=='':
        outputfile=inputfile+'_out'
    print 'Output file is ', outputfile


    # handling nonsensical input
    if (pct==0 and chunks==0 and con!=-1) or (con!=-1 and max_percent==0):
        print 'When doing a consequtive run, you must enter the amount of chunks (-c) and the percent of the dataset the final sample in the run should have (-max). If you want a specific difference in percent between each sample, use chunks = ((final_percentage) - (start_percentage) / (difference in percentage) + 1). \n\n Ex. a run from 2 to 10 percent with a difference of 2 (2, 4, 6, 8 and 10 percent sample sizes) is (( 10 - 2 ) / 2 ) + 1 = 5.' 
        sys.exit()
    if pct==0 and chunks==0 and con==-1: 
        print 'You must either define the sample size in percentage to the full set, or at least write the number of chunks. Use -h for specification.'
        sys.exit() #quit since it is not clear how to proceed.
    if pct*chunks > 100 :
        print 'The input is wrong. Each chunk will be the size of the percent (-p) input, so chunk*percent can not be more than 100%.'
        sys.exit()

    # Reading the file itself
    objectIn = open(inputfile, "r", 1) 
    # This list will be iterated over when creating the samples. Also create corresponding list for files to write to.
    percentage_sizes = [] 
    files = []

    # In case only a percentage is entered, only make one entry in the percentage_sizes list, by setting chunks=1.
    if con==-1 and chunks==0 and pct!=0:
        chunks=1
    # If a number of chunks larger than 1 are entered, but no percentage, the percentage is automatically set as 100/chunks. Not applicable if doing a consequtive run.
    elif pct ==0 and chunks != 0:
        pct=100/chunks


    # Make chunks and percentage lists.
    for i in range(chunks):
        if con==-1 :
            current_value = ((i+1)*pct)*0.01
            percentage_sizes.append(current_value)
            if chunks != 1:
                files.append(open(outputfile + "_chunk_" + str(int(current_value*100)), "a"))
            elif chunks == 1 and pct != 0:
                files.append(open(outputfile + "_pct_" + str(pct), "a"))
            else :
                files.append(open(outputfile + "_chunk_" + str(int(current_value*100)), "a"))
        else :
            unit = (max_percent - con) / chunks # finds the size of each chunk, based on input.
            current_value = ((((i+1)*unit)+con)*0.01)
            print cudef sample():rrent_value
            percentage_sizes.append(current_value*100)
            files.append(open(outputfile + "_conseq_chunk_" + str(int(current_value*100)), "a"))

    print 'creating and filling sample files.'

    # Traversing the input file
    for line in objectIn:
        r = random.uniform(0,1)
        for i in range(len(percentage_sizes)):
            if r <= percentage_sizes[i]:
                files[i].write(line)
                if con == -1 :
                    break  
            #else : break here to make faster?!              

    for x in percentage_sizes:
        print x

    objectIn.close()
    for outfile in files:
    	outfile.close()



sample()