"""
    short mark, dot or dit (  . ): 1
    longer mark, dash or dah (  - ): 111
    intra-character gap (between the dits and dahs within a character): 0
    short gap (between letters): 000
    medium gap (between words): 0000000
    101010001110111011100011101 = son
"""
import pandas
from pandas import *
test = read_csv('test.csv')

# hit 7 (or 0->6)
binary = ["0000000",  "000" , "1110", "10"]
morse = ["  ", " ", "-", "."]

zipped_char_code = zip(binary, morse)

translator_dict = dict(zipped_char_code)

print("Binary & Morse Pair")
for key, value in translator_dict.items():
    print(key, value)


def last_length_decoder(array2, iterator, i, overshoot):
    
    print('test')
    if (overshoot > 3):
        print ('test')
        if (array2[i+iterator]==0): 
            if (array2[i+1]==0 and array2[i+2]==0):
                out += " "
                counter +=1
                iterator+=2
                print(out)

    # If current isn't 0 must be 1 
        else: 
            if (array2[i+1]==1 and array2[i+2]==1 and array2[i+3]==0):
                out += "-,"
                counter+=1
                iterator += 3
            # Doesnt need iteration b/c 0 is not counted for the dot
            if (array2[i+1]==0): 
                out += ".,"
                counter+=1
                print(out)    
    for x in range(6):
        if (i + iterator + x > len(array2)):
            a = i + iterator + x 
            length = len(array2)

            overshoot = a - length
            print("start", a, "overshoot", overshoot)
            array2 = array2[i+iterator:length]
            print("array2", array2, overshoot)
            
def decoder(to_decode): 
    out = ''
    iterator = 0 
    counter = 0 
    for i in range (len(to_decode)):
        print("i", i)
        # Current is 0
        for x in range(6):
            if (i + iterator + x > len(to_decode)):
                a = i + iterator + x 
                length = len(to_decode)

                overshoot = a - length
                print("start", a, "overshoot", overshoot)
                array2 = to_decode[i+iterator:length]
                print("array2", array2, overshoot)                
                last_length_decoder(array2, iterator, i, overshoot)
        if (to_decode[i+iterator]==0): 
            if (to_decode[i+1+iterator]==0 and to_decode[i+2+iterator]==0 and to_decode[i+3+iterator]==0 and to_decode[i+4+iterator]==0 and to_decode[i+5+iterator]==0 and to_decode[i+6+iterator]==0): 
                out += "   "
                counter+=1
                iterator += 6
                print(out)
            elif (to_decode[i+1+iterator]==0 and to_decode[i+2+iterator]==0):
                out += " "
                counter +=1
                iterator+=2
                print(out)

        # If current isn't 0 must be 1 
        else: 
            if (to_decode[i+1+iterator]==1 and to_decode[i+2+iterator]==1 and to_decode[i+3+iterator]==0):
                out += "-,"
                counter+=1
                iterator += 3
            # Doesnt need iteration b/c 0 is not counted for the dot
            if (to_decode[i+1+iterator]==0): 
                out += ".,"
                counter+=1
                print(out)


            
        
            
    
   
   
       
    
if __name__=="__main__":
    test_list = [0,0,0,0,0,0,0,1,0,0,0,1,0,1,0,0,0,0,1,0,1]     

    decoder(test_list)    
    

