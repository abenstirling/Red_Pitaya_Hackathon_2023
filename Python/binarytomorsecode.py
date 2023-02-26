"""
    short mark, dot or dit (  . ): 1
    longer mark, dash or dah (  - ): 111
    intra-character gap (between the dits and dahs within a character): 0
    short gap (between letters): 000
    medium gap (between words): 0000000
    101010001110111011100011101 = son
"""

# hit 7 (or 0->6)
binary = ["0000000",  "000" , "111", "1"]
morse = ["___"     , "_"    , "-"    , "."]


test_list = [0,0,0,0,0,0,0, 1,1,1, 0,0,0 ,1, 0,0,0] # ___-_._
# test_list = [0,0,0] # ___-_._

index = -1
while index < len(test_list)-1:
    index+=1
    foundSequence = 0
    morseIndex = -1
    for sequence in binary: 
        if foundSequence:
            break
        morseIndex += 1
        sequenceLength = len(sequence) 
        curIndex = 0
        for digit in sequence:
            if (test_list[index + curIndex] == int(sequence[curIndex])):
                curIndex+=1 # the moment out of bounds, then say reached the end
            else:
                break
            if (curIndex == sequenceLength):
                # print("reached the end!")
                print(morse[morseIndex])
                index += len(sequence)-1
                foundSequence = 1
            if index + curIndex > len(test_list)-1:
                break
                
                
                





















































# ming has a big boooty
                
            
            
