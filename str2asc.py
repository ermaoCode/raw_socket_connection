def str2asc(s):
    asc = []
    for c in range(len(s)):
        # print s[c]
        asc.append(ord(s[c]))
    return asc


def printBinary(s):
    arr = str2asc(s)

    for i in range(len(arr)):
        print "%02x "%(arr[i]),

    print ''

