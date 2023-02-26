# " " = separation between characters
# "   " = separation between words 

testMorse = "- .... . --.- ..- .. -.-. -.- -... .-. --- .-- -. ..-. --- -..- .--- ..- -- .--. . -.. --- ...- . .-. - .... . .-.. .- --.. -.-- -.. --- --."
key = {
    ".-" : 'a',
    "-..." : 'b',
    "-.-." : 'c', 
    "-.." : 'd', 
    "." : 'e',
    "..-." : 'f',
    "--." : 'g',
    "...." : 'h', 
    ".." : 'i',
    ".---" : 'j',
    "-.-" : 'k',
    ".-.." : 'l',
    "--" : 'm',
    "-." : 'n',
    "---" : 'o',
    ".--." : 'p',
    "--.-" : 'q',
    ".-." : 'r',
    "..." : 's',
    "-" : 't',
    "..-" : 'u',
    "...-" : 'v',
    ".--" : 'w',
    "-..-" : 'x', 
    "-.--" : 'y',
    "--.." : 'z'
}
msg = ""
nextSpace = testMorse.find(" ")
lastSpace = 0
while nextSpace != -1:
    msg += (key.get(testMorse[lastSpace:nextSpace]))
    if (testMorse[nextSpace+1] == " "):
        print(" ")
        lastSpace = nextSpace + 3
    else:
        lastSpace = nextSpace+1
    nextSpace = testMorse.find(" ", lastSpace)

msg += (key.get(testMorse[lastSpace:])) # Dont forget the last fricking character!!
print(msg)