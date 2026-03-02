from google import genai

class WebSearcher(): 
    
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.webSources = []
    
    @staticmethod
    def contextPromptBuild(country, webSearchRelevanceTarget, avoidWords, requiredWords):
        contextPrompt = f"""
            You are an expert at open-source research.
            
            For {country}:
            
            Give me the most important and reliable sources in {country} focusing on {webSearchRelevanceTarget}.
            
            I am not looking for {avoidWords}. I am only interested in identifying specific transactions. Only include sources containing at least one of the following categories:

            {requiredWords}
            
            Your output should be structured in the following way, with absolutely no extra formatting, spaces, or other tokens, for all found sources:
            
            URL1&source_name1,URL2&source_name2, ...
            """
        return contextPrompt
    
    def themePromptBuild(self, theme, country, themeURLs):
        themePrompt = f"""
            Give me more sources related to {theme} in {country}. 
            
            Do not include any of these sources: 
            
            {themeURLs}
            
            IMPORTANT: If all found sources are in the above list, return this string with no extra formatting, spaces, or other tokens: "Done."
            
            Your output should be structured in the following way, with absolutely no extra formatting, spaces, or other tokens, for all found sources:
            
            URL1&source_name,URL2&source_name2, ...
            """
        return themePrompt
        
    def countrySearch(self, 
                      countries, 
                      themes, 
                      webSearchRelevanceTarget, 
                      avoidWords, 
                      requiredWords):
        """
        Leverage WebSearcher context to generate a list of URLs and base domain names for all themes related to all countries in a list.
        
        Parameters should be set in parameters.json or passed in some other way.
        
        webSearchRelevanceTarget: General query of interest. For example - Government financing, infrastructure projects, political news, etc. Generally, these should be as distinct as possible.
        
        avoidWords: If the model is consistently returning certain irrelevant results, put the words here.
        
        requiredWords: If sources not containing certain words should be filtered out from the results, put the words here. 
        """
        for country in countries:
            contextPrompt = self.contextPromptBuild(country, webSearchRelevanceTarget, avoidWords, requiredWords)
            contextResponse = self.client.models.generate_content(
                model='gemini-3-flash-preview',
                contents=contextPrompt
            ).text
            contextURLs = [temp.split('&') for temp in contextResponse.split(',')]
            self.webSources.extend(contextURLs)
            for theme in themes:
                rep = True
                tempCheck = 0
                themeURLs = []
                while rep and tempCheck < 5:
                    themePrompt = self.themePromptBuild(theme, country, themeURLs)
                    themeResponse = self.client.models.generate_content(
                        model='gemini-3-flash-preview',
                        contents=themePrompt
                ).text
                    if "Done." in themeResponse:
                        break
                    URLs = [temp.split('&') for temp in themeResponse.split(',')]
                    URLnum = len(URLs)
                    repCount = 0
                    for URL in URLs:
                        if URL not in self.webSources:
                            self.webSources.append(URL)
                            themeURLs.append(URL)
                        else:
                            repCount += 1
                    tempCheck += 1
                    if repCount == URLnum:
                        rep = False
        self.client.close()
                
class SourceChecker():
    
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)