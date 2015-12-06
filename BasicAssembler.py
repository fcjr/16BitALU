import sys

correct = True
numRegs = 16
extraBits = "000"
numBits = 17
opcodes = {
    "add":"00000",
    "addi":"10000",
    "sub":"00011",
    "subi":"10011",
    "or":"00010",
    "ori":"10010",
    "and":"00001",
    "andi":"10001",
    "lw":"11000",
    "sw":"10100"
}
immediates = {"addi","andi","ori","subi"}
sudos = {"nop"}

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

def sudo(lineList, lineNumber):
    global correct
    global assembled
    if len(lineList) == 1 and lineList[0] == "nop":
        nopBin =  "0" * numBits
        assembled =  bs2hex(extraBits + nopBin) + " "
        return assembled
    else:
        correct = False
        print "invalid construction of sudo instruction on line: " + str(lineNumber)
        return ""

def standardOp(lineList, lineNumber):
    global correct
    opcode = opcodes[lineList[0]]
    destRaw = lineList[1].replace("$","")
    src1Raw = lineList[2].replace("$","")
    src2Raw = lineList[3].replace("$","")
    try:
        destInt = int(destRaw)
        src1Int = int(src1Raw)
        src2Int = int(src2Raw)
    except ValueError:
        correct = False
        print "invalid register name or immediate value on line: " + str(lineNumber)
        return ""
    if lineList[0] in immediates:
        if  0 <= destInt <= numRegs-1 and 0 <= src1Int <= numRegs-1 and -8 <= src2Int <= 7:
            #DO NOTHING
            pass
        else:
            correct = False
            print "immediate out of bounds on line" + str(lineNumber)
    elif 0 <= destInt <= numRegs-1 and 0 <= src1Int <= numRegs-1 and 0 <= src2Int <= numRegs-1:
        #DO NOTHING
        pass
    else:
        correct = False
        return ""
        print "reg out of range error"
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
    lineNumber = 1
    with open(filename) as readFile:
        for line in readFile:
            line = line.strip('\n')

            #REMOVES INLINE COMMENTS
            line = line.strip('\n')
            if not line.startswith("#"):
                line = line.split("#")
                line = line[0].lstrip().strip()

            lineList = line.split(" ")
            #print lineList
            if len(lineList) > 0 and lineList[0] in sudos:
                assembled += sudo(lineList, lineNumber)
            elif len(lineList) == 4 and opcodes.has_key(lineList[0]):
                assembled += standardOp(lineList, lineNumber)
            elif lineList[0].startswith("#") or len(lineList) == 1 and lineList[0] == "":
                pass #ignore oneliner comments and blank lines
            else:
                correct = False
                print "invalid line on line number: " + str(lineNumber)
            lineNumber += 1

        assembled = assembled.rstrip()
        if correct == True:
            save(filename,assembled)
        else:
            print "ERROR ASSEMBLING TRY AGAIN"

if __name__ == "__main__":
    main()
