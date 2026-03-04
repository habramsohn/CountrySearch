import pandas as pd

def linkParser(list):
    elOne = [element[0] for element in list if len(element) > 1]
    elTwo = [element[1] for element in list if len(element) > 1]
    return elOne, elTwo

def frameBuilder(sources,
                 domains,
                 ratings,
                 reasonings):
    zipped = list(zip(sources, domains, ratings, reasonings))
    cols = ['sources','domains','ratings','reasonings']
    df = pd.DataFrame(zipped, columns = cols)
    return df

def exportCsv(df, countries):
    df.to_excel(f'Results/{countries}_output.xlsx',index = False)
    