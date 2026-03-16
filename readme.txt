# CountrySearch

A tool for gathering multiple web sources related to any topic in any specific country by leveraging AI API calls.

This tool is built for Gemini, but other AI APIs could be inserted by adjusting the prompt functions in models.py.

Note that because this tool produces AI output, manually reviewing the results is recommended. However, this tool should improve variety and efficiency of source searching.

## Setup

1. Create a virtual environment:
   ```
   python -m venv .venv
   ```

2. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Linux/Mac: `source .venv/bin/activate`

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your API keys:
   ```
   WEBSEARCHER_KEY=your_gemini_api_key_here
   SOURCECHECKER_KEY=your_gemini_api_key_here
   ```

## Parameters

The tool uses `parameters.json` to configure searches:

### WebSearcher Parameters
- `country`: Target country for research (e.g., "Bahrain")
- `themes`: List of themes to search for (e.g., government websites, universities, media)
- `webSearchRelevanceTarget`: Description of what information to look for
- `requiredWords`: Words that must appear in relevant sources
- `avoidWords`: Words to avoid in search results
- `limit`: How many search iterations per theme, generally returning 15 sources per limit per theme

Note: In my experience, a limit of 2 tends to give the most efficient results. A lower limit may miss essential results, and higher limits return more hallucinations or irrelevant sources, requiring more manual work. The optimal number may vary depending on the target. 

### SourceChecker Parameters
- `URLRelevanceTargets`: Topics to check for in found sources
- `URLSearchTerms`: Keywords to search for on source websites

## Usage

Run the main script:
```
python main.py
```

Results are exported to `Results/{country}_output.xlsx` with columns for sources, domains, ratings, and reasonings.

## Output Ratings
- -1: Unable to access or invalid source
- 0: No relevance
- 1: Indirect relevance
- 2: Direct relevance
- 3: Specific examples of relevance

## Modules and Functions

### main.py
The main entry point script that orchestrates the entire country search process.
- Loads environment variables and parameters from files
- Initializes WebSearcher and SourceChecker instances
- Executes the web search for sources
- Checks the relevance of found sources
- Processes and exports results to an Excel file

### models.py
Contains the core AI-powered classes for web searching and source validation.

#### WebSearcher Class
Handles the discovery of relevant web sources for a given country and themes.
- `__init__(api_key)`: Initializes the WebSearcher with a Gemini API key
- `contextPromptBuild(country, webSearchRelevanceTarget, avoidWords, requiredWords)`: Builds the initial prompt for finding reliable sources
- `themePromptBuild(theme, country, themeURLs)`: Builds prompts for theme-specific searches
- `themeSearch(theme, country, limit)`: Performs iterative searches for a specific theme up to set limit
- `countrySearch(country, themes, webSearchRelevanceTarget, avoidWords, requiredWords, limit)`: Main method to search for sources across all themes

#### SourceChecker Class
Validates and rates the relevance of discovered sources.
- `__init__(api_key)`: Initializes the SourceChecker with a Gemini API key
- `sourcePromptBuild(source, URLRelevanceTargets, URLSearchTerms)`: Builds prompt for checking source relevance
- `sourceAwait(source, URLRelevanceTargets, URLSearchTerms)`: Asynchronously loads a single source
- `sourceCheck(sources, URLRelevanceTargets, URLSearchTerms)`: Checks all loaded sources concurrently

### utils.py
Utility functions for data processing and export.
- `linkParser(list)`: Parses the output from SourceChecker into separate lists
- `frameBuilder(sources, domains, ratings, reasonings)`: Creates a pandas DataFrame from parsed data
- `exportCsv(df, countries)`: Exports the DataFrame to an Excel file in the Results directory