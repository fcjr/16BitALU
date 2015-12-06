import sys

correct = True
numRegs = 16
extraBits = ""
numBits = 20
numInstructions = 4096
opcodes = {
    "add":"00000000",
    "addi":"10000000",
    "sub":"00000011",
    "subi":"10000011",
    "or":"00000010",
    "ori":"10000010",
    "and":"00000001",
    "andi":"10000001",
    "lw":"10001000",
    "sw":"10000100",
    "blt":"00010000",
    "beq":"00110000",
    "bne":"00100000",
    "j":"01000000"
}
immediates = ["addi","andi","ori","subi"]
memory = ["sw","lw"]
branches = ["beq","blt","bne"]
sudos = ["nop","move","bgt"]

def int2bs(s, n):
    """ Converts an integer string to a 2s complement binary string.

        Args: s = Integer string to convert.to 2s complement binary.
              n = Length of outputted binary string.

        Example Input: stpd("4", 4)
        Example Output: "0100"

        Example Input: stpd("-3", 16)
        Example Output: "1111111111111101" """
    x = int(s)                              # Convert string to integer, store in x.
    if x >= 0:                              # If not negative, use python's binary converter and strip the "0b"
        ret = str(bin(x))[2:]
        return ("0"*(n-len(ret)) + ret)     # Pad with 0s to length.
    else:
        ret = 2**n - abs(x)                 # If negative, convert to 2s complement integer
        return bin(ret)[2:]                 # Convert to binary using python's binary converter and strip the "0b"

def bs2hex(v):
    """ Converts a binary string into hex.

        Args: v = Binary string to convert to hex

        Example Input: bs2hex("1010000010001111")
        Example Output: "a08f" """

    ret = ""                                                            # Initialize ret string.
    bschunks = ["0b" + v[i*4:(i+1)*4] for i in range(0, len(v) / 4)]    # Chunk the binary string into groups of 4.
    for chunk in bschunks:
        ret += hex(int(chunk, 2))[2:]                                   #Convert each chunk to hex and strip the "0x"
    return ret

def sudo(lineList, labels, instructionNumber, lineNumber, constants):
    global correct
    global assembled
    if len(lineList) == 1 and lineList[0] == "nop":
        nopBin =  "0" * numBits
        assembled =  bs2hex(extraBits + nopBin) + " "
        return assembled
    elif len(lineList) == 4 and lineList[0] == "bgt":
        one = lineList[2]
        two = lineList[1]
        three = lineList[3]
        flipped = ["blt",one, two, three]
        assembled = standardOp(flipped, labels, instructionNumber, lineNumber, constants)
        return assembled
    elif len(lineList) == 3 and lineList[0] == "move":
        newList =["addi",lineList[1],lineList[2],"0"]
        assembled = standardOp(newList, labels, instructionNumber, lineNumber, constants)
        return assembled
    else:
        correct = False
        print "Invalid construction of sudo instruction on line: " + str(lineNumber)
        return ""

def standardOp(lineList, labels, instructionNumber, lineNumber, constants):
    global correct
    opcode = opcodes[lineList[0]]
    destRaw = lineList[1].replace("$","")
    src1Raw = lineList[2].replace("$","")
    src2Raw = lineList[3].replace("$","")
    try:
        destInt = int(destRaw)
        src1Int = int(src1Raw)
    except ValueError:
        correct = False
        print "Invalid register on line: " + str(lineNumber)
        return ""
    try:
        src2Int = int(src2Raw)
    except ValueError:
        if lineList[0] in branches and src2Raw in labels:
            srcLine = labels[src2Raw]
            src2Int = srcLine - instructionNumber-1
        elif lineList[0] in immediates and src2Raw in constants or lineList[0] in memory and src2Raw in constants:
            src2Int = constants[src2Raw]
        else:
            correct = False
            print "Invalid register name, immediate value or label on line: " + str(lineNumber)
            return ""
    if lineList[0] in immediates or lineList[0] in branches:
        if 0 <= destInt <= numRegs-1 and 0 <= src1Int <= numRegs-1 and -8 <= src2Int <= 7:
            pass
        else:
            correct = False
            if lineList[0] in immediates:
                print "Immediate out of bounds on line: " + str(lineNumber)
            else:
                print "Branch out of bounds on line: " + str(lineNumber)
    elif 0 <= destInt <= numRegs-1 and 0 <= src1Int <= numRegs-1 and 0 <= src2Int <= numRegs-1:
        #DO NOTHING
        pass
    else:
        correct = False
        print "Reg out of range error on line: " + str(lineNumber)
        return ""
    assembled = ""
    if correct:
        dest = str(int2bs(destInt, 4))
        src1 = str(int2bs(src1Int, 4))
        src2 = str(int2bs(src2Int, 4))

        binary = extraBits + opcode + dest + src1 + src2
        #print binary
        binary = str(binary)
        hex = str(bs2hex(binary))
        #print hex
        assembled = hex
        assembled += " "
    return assembled

def jumpOp(lineList, labels, lineNumber, constants):
    global correct
    opcode = opcodes[lineList[0]]
    destRaw = lineList[1].replace("$","")
    try:
        destInt = int(destRaw)
        if 0 <= destInt < numInstructions:
            pass
        else:
            correct = False
            print "Error attempt to jump to non-valid instruction address. Line: " + str(lineNumber)
    except ValueError:
        if destRaw in labels:
            destInt = labels[destRaw]
        elif destRaw in constants:
            destInt = labels[destRaw]
        else:
            correct = False
            print "Error: Attempting to jump to a non-existent label on line: " + str(lineNumber)
            return ""
    if not lineList[0] == "j":
        correct = False
        return ""
        print "Error constructing jump command on line: "  + str(lineNumber)
    dest = str(int2bs(destInt, 12))
    binary = extraBits + opcode + dest
    #print binary
    binary = str(binary)
    hex = str(bs2hex(binary))
    #print hex
    assembled = hex
    assembled += " "
    return assembled

def getLabels(filename):
    global correct
    labels = {}
    instructionNum = 0
    with open(filename) as readFile:
        for line in readFile:
            line = line.strip('\n')

            #REMOVES COMMENTS
            if not line.startswith("#"):
                line = line.split("#")
                line = line[0]

            lineList = line.split(":")
            if lineList[0].startswith("#") or lineList[0] is "" or "=" in lineList[0]:
                #line is a comment or blank or not a label, pass
                pass
            elif len(lineList) == 1:
                instructionNum += 1
            else:
                #print lineList
                if len(lineList) == 2:
                    label = lineList[0]
                    #print label
                    if label in labels:
                        print "Error: Code contains more than one instance of label: " + label
                        correct = False
                    else:
                        labels[label] = instructionNum
                        #print label
                else:
                    print "Label error, check your labels man."
                    correct = False
                instructionNum += 1
        #print labels
        return labels

def getConstants(filename):
    global correct
    constants = {}
    lineNumber = 0
    with open(filename) as readFile:
        for line in readFile:
            line = line.strip('\n')

            #REMOVES COMMENTS
            if not line.startswith("#"):
                line = line.split("#")
                line = line[0]


            lineList = line.split("=")
            if lineList[0].startswith("#") or lineList[0] is "":
                #line is a comment or blank or not a label, pass
                pass
            elif len(lineList) == 2:
                try:
                    rawVal = lineList[1].lstrip().strip()
                    val = int(rawVal)
                except ValueError:
                    correct = False
                    print "constant not an int on line: " + str(lineNumber)
                    return {}
                if -8 <= val <= 7:
                    constants[lineList[0].lstrip().strip()] = val
                else:
                    correct = False
                    print "constant out of bounds on line: " + str(lineNumber)
                    return {}
                lineNumber += 1
        return constants


def save(saveFile, assembledCode):
    saveList = saveFile.split(".")
    saveFile = ""
    saveFile += saveList[0]
    saveFile += ".hex"
    f = open(saveFile,"w")
    header = "v2.0 raw\n"
    f.write(header)
    f.write(assembledCode)
    f.close()
    print "Success! Assembled code saved to file: " + saveFile

def main():
    global correct
    correct = True
    assembled = ""
    filename = sys.argv[1]
    #print saveFile
    lineNumber = 1
    instructionNumber = 0
    labels = getLabels(filename)
    constants = getConstants(filename)
    with open(filename) as readFile:
        for line in readFile:

            #REMOVES COMMENTS AND LABELS
            line = line.strip('\n')
            if not line.startswith("#"):
                line = line.split("#")
                line = line[0]

            lineList = line.split(":")
            if len(lineList) == 2:
                lineList = lineList[1].lstrip().strip()
            elif len(lineList) == 1:
                lineList = lineList[0].lstrip().strip()
            else:
                print "Error, you may only have one label per line"
                correct = False

            lineList = lineList.split(" ")
            if lineList[0].startswith("#") or len(lineList) == 1 and lineList[0] is "" or "=" in lineList:
                #line is a comment or blank, or constant, pass
                pass
            elif len(lineList) > 0 and lineList[0] in sudos: #construct sudo instructions
                assembled += sudo(lineList, labels, instructionNumber, lineNumber, constants)
                instructionNumber += 1
            elif len(lineList) == 4 and opcodes.has_key(lineList[0]): #construct standard operations
                assembled += standardOp(lineList, labels, instructionNumber, lineNumber, constants)
                instructionNumber += 1
            elif len(lineList) == 2 and opcodes.has_key(lineList[0]):
                assembled += jumpOp(lineList, labels, lineNumber, constants)
                instructionNumber += 1
            else: # error in file prompt user.
                correct = False
                print "Parse error on line number: " + str(lineNumber)
            lineNumber += 1


        #Write to file if assembly went well, Prompt user about fail if not.
        assembled = assembled.rstrip()
        if correct == True:
            save(filename,assembled)
        else:
            print "ERROR ASSEMBLING DID NOT WRITE FILE. TRY AGAIN."

if __name__ == "__main__":
    main()
