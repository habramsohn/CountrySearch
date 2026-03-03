import pandas as pd

def linkParser(list):
    URLs = [element[0] for element in list]
    domains = [element[1] for element in list]
    return URLs, domains