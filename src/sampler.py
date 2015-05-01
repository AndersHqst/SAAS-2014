from sys import argv
import sys, getopt, random

def sample(inputfile='', outputfile='', pct=10):
    
    if inputfile!='' : # Reading the file itself
        objectIn = open(inputfile, "r", 1) 
    else :
        print 'error opening file.'
        sys.exit()
    if outputfile=='' :
        outputfile=inputfile+'out'
        print 'Sample outputfile is ' + str(outputfile)
    
    objectOut=open(outputfile, 'a')
    restFile=open(outputfile+'_rest', 'a')
    print 'File containing all other than sample: ' + str(restFile)


    print 'creating and filling sample file.'

    pctFormat = pct*0.01

    # Traversing the input file
    for line in objectIn:
        r = random.uniform(0,1)
        if r <= pctFormat:
            outputfile.write(line)
        else :
            restFile.write(line)
            

    objectIn.close()
    objectOut.close()
    restFile.close()


def sample_file(infile, outfile, sample_size=10):
    """
    sample_size is a percentage if positive number provided,
    negative is an explicit number of lines.
    """
    assert sample_size <= 100, 'invalid sample_size argument'
    assert sample_size != 0, 'Meaningless sample_size argument'

    # Compute total number of lines
    total_lines = 0
    for line in open(infile, 'rb'):
        total_lines += 1
    print 'total_lines: ', total_lines
    
    # Reduction is to be taken as a percentage of all lines
    target_lines = None
    if sample_size > 0:
        target_lines = int(total_lines * (sample_size / 100.))
    else:
        target_lines = abs(sample_size)

    # Create random sample
    sample = random.sample(range(total_lines), target_lines)
    sample_size = len(sample)
    print 'sample_size: ', sample_size

    # descending sort
    sample.sort(reverse=True)

    # Append/Write sampled lines to outfile
    with open(outfile, 'a') as sample_file:
        
        # init, pop smallest element
        sample_line = sample.pop() 

        for line_num, line in enumerate(open(infile, 'rb')):

            # If the line number is in the sample, 
            # write the line to the outfile
            if line_num == sample_line:
                sample_file.write(line)
                if len(sample) == 0:
                    break
                sample_line = sample.pop()                
    print 'Wrote sample of size {} to {}'.format(sample_size, outfile)
