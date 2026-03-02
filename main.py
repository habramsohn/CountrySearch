import os
from dotenv import load_dotenv
from models import WebSearcher
import json

# Load API keys for models
load_dotenv()

# Load parameters
with open('parameters.json', 'r') as file:
    parameters = json.load(file)
    
WebSearcherParameters = parameters["WebSearcher"]
SourceCheckerParameters = parameters["SourceChecker"]

WEBSEARCHER_KEY = os.getenv("WEBSEARCHER_KEY")
SOURCECHECKER_KEY = os.getenv("SOURCECHECKER_KEY")

if __name__ == "__main__":
    websearch = WebSearcher(WEBSEARCHER_KEY)
    websearch.countrySearch(**WebSearcherParameters)
    print(websearch.webSources)