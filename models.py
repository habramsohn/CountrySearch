from google import genai

class WebSearcher(): 
    
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.webSources = []
    
    @staticmethod
    def contextPromptBuild(country, 
                           webSearchRelevanceTarget, 
                           avoidWords, 
                           requiredWords):
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
    
    def themePromptBuild(self, 
                         theme, 
                         country, 
                         themeURLs):
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
                      requiredWords,
                      limit):
        """
        Leverage WebSearcher context to generate a list of URLs and base domain names for all themes related to all countries in a list.
        
        Parameters should be set in parameters.json or passed in some other way.
        
        webSearchRelevanceTarget: General query of interest. For example - Government financing, infrastructure projects, political news, etc. Generally, these should be as distinct as possible.
        
        avoidWords: If the model is consistently returning certain irrelevant results, put the words here.
        
        requiredWords: If sources not containing certain words should be filtered out from the results, put the words here. 
        """
        for country in countries:
            
            # Build first prompt
            contextPrompt = self.contextPromptBuild(country, webSearchRelevanceTarget, avoidWords, requiredWords)
            contextResponse = self.client.models.generate_content(
                model='gemini-3-flash-preview',
                contents=contextPrompt
            ).text
            
            # Split into individual links and domain names and add to object list
            contextURLs = [temp.split('&') for temp in contextResponse.split(',')]
            self.webSources.extend(contextURLs)
            
            # Extend search for each theme
            for theme in themes:
                check = 0
                themeURLs = []
                # limit = Parameter for how exhaustive search should be; set in parameters.json
                while check < limit:
                    print(check, theme)
                    themePrompt = self.themePromptBuild(theme, country, themeURLs)
                    themeResponse = self.client.models.generate_content(
                        model='gemini-3-flash-preview',
                        contents=themePrompt
                    ).text
                    
                    # Allow model to end theme if no further information exists
                    if "Done." in themeResponse:
                        break
                    
                    URLs = [temp.split('&') for temp in themeResponse.split(',')]
                    
                    # Add URL to global context if not existing 
                    # Add URL to theme comtext to prevent repitition with minimal token spend
                    for URL in URLs:
                        if URL not in self.webSources:
                            self.webSources.append(URL)
                            themeURLs.append(URL)
                    check += 1
        self.client.close()
                
class SourceChecker():
    
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.output = []
        
    @staticmethod
    def sourcePromptBuild(source,
                          URLRelevanceTargets,
                          URLSearchTerms):
        sourcePrompt = f"""
            You are an expert open-source research assistant.

            For {source}:

            Run a comprehensive search across the URL's subdomains and sitemap, for evidence of the following topics:

            {URLRelevanceTargets}

            Your stopping rules:

            - You must individually open and inspect every URL that contains any of the specified keywords, across all archives and subpaths of the domain.
            - Treat this as a recall-maximization task: completeness is more important than speed or efficiency; shallow sampling is explicitly forbidden.
            - You are not allowed to infer absence of evidence from a subset of results; you must algorithmically enumerate all matching URLs and inspect each one before drawing conclusions.

            Always include the following terms in all languages present on the target URL:

            {URLSearchTerms}

            In addition to external search, always use the website’s internal search function with the above terms, including translations, to capture deep URLs.

            Be sure to run your searches in all official and otherwise relevant languages of the host nation.

            Your output should only contain the following structure: one number chosen from the list below, and a single sentence of your reasoning, with no additional formatting or tokens of any kind:
            
            num|reasoning
        
            Possible num:
            
            -1 = Unable to access source or execute search
            0 = No relevance
            1 = Possible or indirect relevance to topics or search terms
            2 = Relevance to multiple topics and search terms
            """
        return sourcePrompt
        
    def sourceCheck(self,
                    sources,
                    URLRelevanceTargets,
                    URLSearchTerms):
        for source in sources:
            print(source)
            sourcePrompt = self.sourcePromptBuild(source, URLRelevanceTargets, URLSearchTerms)
            sourceResponse = self.client.models.generate_content(
                        model='gemini-3-flash-preview',
                        contents=sourcePrompt
                    ).text
            print(sourceResponse)
            rating = tuple(sourceResponse.split('|'))
            print(rating)
            self.output.append((rating))
        self.client.close()

        
    