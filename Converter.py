import pandas as pd

def convert(playerDict, write=False, file=""):
    print("CONVERTER")
    values = []
    for player in playerDict:
        print(player)
        category = playerDict[player]
        for table in category:
            print('   ', table)
            x = playerDict[player][table]
            x[0] = x[0][:len(x[1][0])]
            y =pd.DataFrame(x[1], columns=x[0])
            values.append(y)
            if write:
                writeToFile(y, file)

    return y


def writeToFile(value, file):
    with open(file, 'a') as f:
        f.write(value.to_csv())
    f.close()
