import pandas as pd


def linkParser(list):
    elOne = [element[0] for element in list if len(element) >= 4]
    elTwo = [element[1] for element in list if len(element) >= 4]
    elThree = [element[2] for element in list if len(element) >= 4]
    elFour = [element[3] for element in list if len(element) >= 4]
    return elOne, elTwo, elThree, elFour


def linkCutter(links):
    adjs = []
    for link in links:
        if link.count("/") > 2:
            t = link.split("/")[:3]
            x = "/".join(t)
            adjs.append(x)
        else:
            adjs.append(link)
    return adjs


def frameBuilder(sources, domains, ratings, reasonings):
    zipped = list(zip(sources, domains, ratings, reasonings))
    cols = ["sources", "domains", "ratings", "reasonings"]
    df = pd.DataFrame(zipped, columns=cols)
    df.drop_duplicates(subset=["sources"],inplace=True)
    df.drop_duplicates(subset=["domains"],inplace=True)
    return df


def exportCsv(df, country):
    df.to_excel(f"Results/{country}_output.xlsx", index=False)
