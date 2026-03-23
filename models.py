from google import genai
import asyncio


class WebSearcher:

    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.webSources = []

    @staticmethod
    def contextPromptBuild(
        country, webSearchRelevanceTarget, avoidWords, requiredWords
    ):
        contextPrompt = f"""
            You are an expert at open-source research.
            
            For {country}:
            
            Give me the most important and reliable sources in {country} focusing on {webSearchRelevanceTarget}. Give me base URLs. Mistakes will get you fired.
            
            IMPORTANT: Do not give me URLs with content beyond the '.com', '.gov', or equivalent top-level domain.
            
            I am not looking for {avoidWords}. Only include sources containing at least one of the following categories:

            {requiredWords}
            
            Translate source name to English.
            
            Your output should be structured in the following way, with absolutely no extra formatting, spaces, or other tokens, for all found sources.
            
            Give me only the URL, no domain or other non-URL names:
            
            first_URL,second_URL, ...
            """
        return contextPrompt

    def themePromptBuild(self, theme, country, themeURLs):
        themePrompt = f"""
            Give me more sources related to {theme} specific to {country}. 
            
            Do not include any of these sources: 
            
            {themeURLs}
            
            IMPORTANT: If all found sources are in the above list, return this string with no extra formatting, spaces, or other tokens: "Done."
            
            Translate source name to English. Mistakes will get you fired.
            
            Your output should be structured in the following way, with absolutely no extra formatting, spaces, or other tokens, for all found sources.
            
            Give me only the URL, no domain or other non-URL names:
            
            first_URL,second_URL, ...
            """
        return themePrompt

    async def themeSearch(self, theme, country, limit):
        check = 0
        themeURLs = []
        # limit = Parameter for how exhaustive search should be; set in parameters.json
        while check < limit:
            print(check, theme)
            themePrompt = self.themePromptBuild(theme, country, themeURLs)
            themeResponse = (
                await self.client.aio.models.generate_content(
                    model="gemini-3.1-flash-lite-preview", contents=themePrompt
                )
            ).text

            # Allow model to end theme if no further information exists
            if "Done." in themeResponse:
                break

            URLs = themeResponse.split(",")

            # Add URL to global context if not existing
            # Add URL to theme context to prevent repetition with minimal token spend
            for URL in URLs:
                if URL not in self.webSources:
                    self.webSources.append(URL)
                    themeURLs.append(URL)
            check += 1

    def countrySearch(
        self,
        country,
        themes,
        webSearchRelevanceTarget,
        avoidWords,
        requiredWords,
        limit,
    ):
        """
        Leverage WebSearcher context to generate a list of URLs and base domain names for all themes related to specified country.

        Parameters should be set in parameters.json or passed in some other way.

        webSearchRelevanceTarget: General query of interest. For example - Government financing, infrastructure projects, political news, etc. Generally, these should be as distinct as possible.

        avoidWords: If the model is consistently returning certain irrelevant results, put the words here.

        requiredWords: If sources not containing certain words should be filtered out from the results, put the words here.
        """
        # Build first prompt
        contextPrompt = self.contextPromptBuild(
            country, webSearchRelevanceTarget, avoidWords, requiredWords
        )
        contextResponse = self.client.models.generate_content(
            model="gemini-3.1-flash-lite-preview", contents=contextPrompt
        ).text

        # Split into individual links and domain names and add to object list
        contextURLs = contextResponse.split(",")
        self.webSources.extend(contextURLs)

        # Extend search for each theme
        tasks = [self.themeSearch(theme, country, limit) for theme in themes]

        async def gather_tasks():
            return await asyncio.gather(*tasks)

        asyncio.run(gather_tasks())
        self.client.close()


class SourceChecker:

    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.output = []
        self.semaphore = asyncio.Semaphore(40)

    @staticmethod
    def sourcePromptBuild(source, country, URLRelevanceTargets, URLSearchTerms):
        sourcePrompt = f"""
            You are an expert open-source research assistant.

            For {source}:

            Run a comprehensive search across the URL's subdomains and sitemap, for evidence of the following topics:

            {URLRelevanceTargets}
            
            The source should be relevant to the above topics in {country}, specifically..

            Your stopping rules:

            - You must individually open and inspect every URL that contains any of the specified keywords, across all archives and subpaths of the domain.
            - Treat this as a recall-maximization task: completeness is more important than speed or efficiency; shallow sampling is explicitly forbidden.
            - You are not allowed to infer absence of evidence from a subset of results; you must algorithmically enumerate all matching URLs and inspect each one before drawing conclusions.

            Always include the following terms in all languages present on the target URL:

            {URLSearchTerms}

            In addition to external search, always use the website’s internal search function with the above terms, including translations, to capture deep URLs.

            Be sure to run your searches in all official and otherwise relevant languages of the host nation. Be highly discerning.

            Your output should only contain the following structure: one number chosen from the list below, and a single sentence of your reasoning, with no additional formatting or tokens of any kind.
            Website title is the normal name: e.g. 'New York Times' - translated to English and transliterated to English characters. 
            To assign a num to a source, you MUST have a specific, concrete example of relevance - mistakes will get you fired:
            
            website_url|website_title|num|specific_example
        
            Possible num:
            
            -1 = Unable to access source or execute search, or the domain is a specific article/post
            0 = No relevance
            1 = Specific example of relevance to topics and search terms
            2 = Extreme relevance to topics
            """
        return sourcePrompt

    async def sourceAwait(self, source, country, URLRelevanceTargets, URLSearchTerms):
        async with self.semaphore:
            try:
                print(source)
                sourcePrompt = self.sourcePromptBuild(
                    source, country, URLRelevanceTargets, URLSearchTerms
                )
                sourceResponse = (
                    await self.client.aio.models.generate_content(
                        model="gemini-3.1-flash-lite-preview", contents=sourcePrompt
                    )
                ).text
                print(sourceResponse)
                rating = tuple(sourceResponse.split("|"))
                self.output.append((rating))
            except Exception as e:
                print(f"Error checking {source}: {e}")

    def sourceCheck(self, sources, country, URLRelevanceTargets, URLSearchTerms):
        tasks = [
            self.sourceAwait(source, country, URLRelevanceTargets, URLSearchTerms)
            for source in sources
        ]

        async def gather_tasks():
            return await asyncio.gather(*tasks)

        asyncio.run(gather_tasks())
        self.client.close()
