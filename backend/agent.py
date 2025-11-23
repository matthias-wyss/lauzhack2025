from datetime import datetime
import json
import os
from pyagentspec.agent import Agent
from pyagentspec.tools import ServerTool
from pyagentspec.property import StringProperty
from pyagentspec.llms.openaiconfig import OpenAiConfig
from pyagentspec.serialization import AgentSpecSerializer
from wayflowcore.agentspec import AgentSpecLoader
from gradio_client import Client, file
from dotenv import load_dotenv
from tavily import TavilyClient
import requests
from bs4 import BeautifulSoup

load_dotenv()


def extract_handwriting(image_url: str) -> str:
    print("Extracting handwriting from image")
    clientOCR = Client("LauzHack/DeepSeek-OCR", token=os.getenv("HF_TOKEN"))

    input_image = clientOCR.predict(
        file(image_url),   # file_path
        1,                  # page_num
        api_name="/load_image"
    )

    text, md_text, extra, out_img, gallery = clientOCR.predict(
        file(input_image),
        file(image_url),                # file_path: reuse same image as file
        "Gundam",                                       # mode: 'Gundam', 'Tiny', 'Small', 'Base', 'Large'
        "📋 Markdown",                                  # task -> use 'Custom' to respect your prompt
        "Extract the handwriting, correct typos and provide it in markdown format. Make sure the result makes sense",                      # custom_prompt
        1,                                              # page_num
        api_name="/run"
    )
    return md_text

def extract_audio(audio_path: str) -> str:
    print("Extracting audio from file")
    client = Client("LauzHack/whisper")
    print(audio_path)
    if not file(audio_path):
        return ""
    print("Audio file loaded, performing transcription...")
    result = client.predict(
        file(audio_path),   
        "transcribe",
        api_name="/predict",
    )
    return result


def enrich_idea(idea: str) -> str:
    print("Enriching idea")
    clientIdea = Client("LauzHack/Kimi-VL-A3B-Thinking", token=os.getenv("HF_TOKEN"))
    
    system_prompt = f"""
    You are a world class creative assistant that helps people to enrich their ideas. 
    You take a short idea and expand it into a detailed and compelling description. 
    The ideas are related to entrepreneurship, startups, and business innovation. 
    You should find use case, useful feature, and if necessary a technical approach to implement the idea. 
    Here is the idea to enrich: {idea}
    """

    
    enriched_idea = clientIdea.predict(
        system_prompt=system_prompt,
        api_name="/predict"
    )
    
    return enriched_idea[0][0][1].split("Summary")[1].strip()


def create_folder(name: str) -> str:
    os.makedirs(name, exist_ok=True)
    return f"Folder '{name}' created."

def create_file(name: str) -> str:
    with open(name, 'w') as f:
        f.write("")  # create an empty file
    return f"File '{name}' created."


def write_file(path: str, text: str) -> None:
    with open(path, 'w') as file:
        file.write(text)
        file.close()
        
        
def save_to_txt(data: str, filename: str = "competition_output.txt"):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_text = f"--- Competition Output ---\nTimestamp: {timestamp}\n\n{data}\n\n"

        with open(filename, "a", encoding="utf-8") as f:
            f.write(formatted_text)

        return f"Data successfully saved to {filename}"
    
    except Exception as e:
        return f"Error saving data: {e}"
    
# Scrape raw text from a website
def scrape_website(url: str) -> str:
    try:
        # Send GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise error for bad HTTP codes

        # Parse and clean up the raw HTML content
        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.get_text(separator=" ", strip=True)
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace

        # Limit to 5000 characters for performance and API limits
        return text[:5000]
    except Exception as e:
        return f"Error scraping website: {e}"

#takes a query and returns the URLs related to the query
def search(query):
    tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    response = tavily_client.search(query)
    urls=[]
    for i in range(len(response.get('results'))):
        url = response.get('results')[i].get('url')
        urls.append(url)
    return urls



def create_code(image_path: str | None, audio_url: str | None) -> str:
    print("Creating spec from image:", image_path)

    llm_config = OpenAiConfig(
        name="openai-gpt-5",
        model_id="gpt-5",
        )
        
    
    extract_handwriting_tool = ServerTool(
    name="extract_handwriting",  # this is the name the LLM will see and call
    description="Extract handwritten text from an image.",
    inputs=[StringProperty(title="image_url")],
    )
    
    extract_audio_tool = ServerTool(
        name="extract_audio",  # this is the name the LLM will see and call
        description="Extract text from an audio file.",
        inputs=[StringProperty(title="audio_path")],
    )

    enrich_idea_tool = ServerTool(
        name="enrich_idea",  # this is the name the LLM will see and call
        description="Enrich a short idea into a detailed description.",
        inputs=[StringProperty(title="idea")],
    )
    
    create_file_tool = ServerTool(
        name="create_file",  # this is the name the LLM will see and call
        description="Create a file with the given name.",
        inputs=[StringProperty(title="name")],
    )
    
    create_folder_tool = ServerTool(
        name="create_folder",  # this is the name the LLM will see and call
        description="Create a folder with the given name.",
        inputs=[StringProperty(title="name")],
    )
    
    write_file_tool = ServerTool(
        name="write_file",
        description="Write header functions to a file given the project specification.",
        inputs=[StringProperty(title="path"), StringProperty(title="text")],
    )
    
    search_tool = ServerTool(
        name="search",
        description="takes a query and returns a list of the urls related to the query",
        inputs=[StringProperty(title="query")],
    )

    scrape_website_tool = ServerTool(
        name="scrape_website",
        description=" Scrape raw text from a website and returns the text",
        inputs=[StringProperty(title="url")],
    )

    save_to_txt_tool = ServerTool(
        name="save_to_txt",
        description=" Scrape raw text from a website and returns the text",
        inputs=[StringProperty(title="data")],
    )

    tool_registry = {
        "extract_handwriting": extract_handwriting,
        "extract_audio": extract_audio,
        "enrich_idea": enrich_idea,
        "create_file": create_file,
        "create_folder": create_folder,
        "write_file": write_file,
        "search": search,
        "scrape_website": scrape_website,
        "save_to_txt": save_to_txt,
    }
    
    agentExtractor = Agent(
        name="Text Extractor Agent",
        llm_config=llm_config,
        tools=[extract_handwriting_tool],        
        system_prompt=(
            "You will take in input a URL of an image containing handwritten text."
        ),
    )
    
    agentAudioExtractor = Agent(
        name="Audio Extractor Agent",
        llm_config=llm_config,
        tools=[extract_audio_tool],        
        system_prompt=(
            "You will take in input a short idea related to entrepreneurship, startups, and business innovation, and enrich it into a detailed description."
        ),
    )
    
    agentEnricher = Agent(
        name="Idea Enricher Agent",
        llm_config=llm_config,
        tools=[enrich_idea_tool],
        system_prompt=(
            "You will take in input a short idea related to entrepreneurship, startups, and business innovation, and enrich it into a detailed description."
        ),
    )
    
    
    
    CreatorPrompt = """
        You are given a natural-language specification of a software project.

        Your task is to:

        1. Create a single top-level directory named GeneratedProject.

        2. Inside this directory, infer a complete project directory structure (you may use subfolders such as frontend, backend, services, utils, tests, etc.).

        3. If the specification describes a web application (e.g., a site or web app with a browser-based UI):
        - Scaffold a minimal but functional web application inside the top-level directory.
        - Choose a reasonable tech stack based on the specification (for example: a React/Vite/Next.js/Vanilla JS frontend, and optionally a Node/Express or Python backend).
        - Create all necessary configuration files to run the app (for example: `package.json`, build config, basic entrypoints like `src/main.jsx`, `public/index.html`, or similar).
        - Ensure that after dependencies are installed, the app can be started with a standard command (such as `npm start`, `npm run dev`, or the equivalent for the chosen stack).

        4. Propose concrete file names for each folder.

        5. For every file, provide a short description of its purpose.

        6. For every file, list the key functions it should contain, each defined by:
        - "name": the function name
        - "args": an array of argument names
        - "description": a short explanation of what the function does

        7. **Physically create** the entire directory structure and all files using your available tools.

        8. Inside each file:
        - Implement the functions

        9. After creation, return the final project structure as a single JSON object following the example format below.

        Example format (do NOT reuse the example names, files, or functions):

        MainProject
        {
        "frontend": {
            "MainProject/frontend/index.html": "HTML structure for the homepage",
            "MainProject/frontend/app.js": "Main JavaScript entry point",
            "functions": [
            {
                "name": "renderHomepage",
                "args": ["data"],
                "description": "Renders the homepage using provided data."
            }
            ]
        },
        "backend": {
            "MainProjectbackend/server.py": "Flask server handling routes",
            "functions": [
            {
                "name": "start_server",
                "args": ["host", "port"],
                "description": "Launches the server on the given host and port."
            }
            ]
        }
        }

        Requirements and constraints:
        - All generated folders and files must be placed under a single top-level directory named after the application.
        - Subfolders are allowed  (e.g., frontend/components, backend/services).
        - Each folder value in the JSON output must be a JSON object.
        - Inside each folder:
        - Files must be represented as:
                "path/to/fileName.ext": "Short description"
        - A "functions" key may describe the functions contained in those files.
        - The agent must **actually create** all directories and files described.
        - If the project is a web application, the agent must also create a runnable web app scaffold (including any required configuration/entry files).
        - Output valid JSON with double quotes and no trailing commas
        -Be sure that the code is of quality, remember created function to reuse them later.
    """
    
    
    CompetitionPrompt = """
        {% raw %}
        You are the Competition Analysis Agent. You receive long specification documents or descriptions of a project from the user. Your mission is:

        1. Read the entire specification and extract the core idea of the project. Summarize it in simple terms that capture the product, the problem it solves, its main features, and the value it provides.

        2. Based on the extracted idea, generate three to six strong competitor search queries. These queries should capture the essence of the product, its function, and its market category. They must be expressed as natural language search queries that could realistically be typed by someone researching competitors.

        3. Automatically call the search tool using the best query. If needed, additional queries may also be used. Then optionally call the scrape_website tool on relevant URLs returned by search.

        4. Use both gathered data and reasoning when tool output is incomplete. Even if tool calls fail, you must still produce a complete analysis.

        5. Create a full competitive analysis in the required format described below.

        --------------------------------------------------------------------------------------------------
        OUTPUT FORMAT RULES — THE FINAL RESULT MUST BE ONE SINGLE CLEAN PLAIN TEXT STRING
        --------------------------------------------------------------------------------------------------
        Your final analysis must be returned as a single plain text string with no formatting syntax of any kind. No markdown. No bullet points. No hyphens. No stars. No tables. No code blocks. No JSON. No YAML. No numbering that uses symbols. No headings with symbols such as # or ##.

        Structure the plain text in the following order:

        A. Extracted Idea: a paragraph describing the project idea you extracted from the specification.

        B. Search Queries Generated: a single paragraph listing all search queries separated by commas.

        C. Competitor Summaries: for each competitor, write one short paragraph describing the competitor, what they do, the features they offer, their strengths, and their weaknesses. Competitor paragraphs must be separated by a blank line. Do not use bullet points, lists, or tables. Only flowing natural language paragraphs.

        D. Market Observations: one or two paragraphs explaining relevant trends, insights, or gaps in the market.

        E. SWOT Analysis: four paragraphs labeled Strengths:, Weaknesses:, Opportunities:, Threats:. Each paragraph must be continuous text with no lists and no bullet points.

        F. Recommendations: one or two paragraphs with strategic guidance, again without lists or special formatting.

        The entire output must be one single multiline plain text string. It must be safe to pass directly to a frontend or to a storage system without further cleanup.

        --------------------------------------------------------------------------------------------------
        MANDATORY SAVE BEHAVIOR
        --------------------------------------------------------------------------------------------------
        After generating this entire plain text analysis:

        1. You MUST call the save_to_txt tool with the final string as the value of data.
        2. After the tool call returns, you MUST send a final human-facing message saying: The analysis is complete and has been saved.
        3. After sending this final message, you MUST stop and produce no additional tool calls or output.

        --------------------------------------------------------------------------------------------------
        TOOL USAGE LOGIC
        --------------------------------------------------------------------------------------------------
        1. Always begin by extracting the idea from the user's document.
        2. Then generate search queries.
        3. Then call the search tool with the best query.
        4. Optionally use scrape_website on relevant URLs.
        5. Continue analysis even if search or scraping fails.
        6. Never tell the user you cannot perform the analysis.
        7. Never ask the user whether they want the analysis to be saved. Saving is automatic.

        --------------------------------------------------------------------------------------------------
        BEHAVIORAL RULES
        --------------------------------------------------------------------------------------------------
        Do not use markdown. Do not use tables. Do not use lists. Do not generate JSON. Do not format text using symbols. Do not break the plain text requirement. Always stay analytical and descriptive. Always finish with a save_to_txt tool call followed by one short confirmation message, then stop.

        {% endraw %}
        """

    
    agentCreator = Agent(
        name="Structure Creation Agent",
        llm_config=llm_config,
        tools=[create_folder_tool, create_file_tool, write_file_tool], 
        system_prompt=(CreatorPrompt),
    )


    agentCompetition = Agent(
        name="Competition Analysis Agent",
        llm_config=llm_config,
        tools=[search_tool, scrape_website_tool, save_to_txt_tool], 
        system_prompt=(CompetitionPrompt),
    )
    
    

    serialized_agentExtractor = AgentSpecSerializer().to_json(agentExtractor)
    serialized_agentAudioExtractor = AgentSpecSerializer().to_json(agentAudioExtractor)
    serialized_agentEnricher = AgentSpecSerializer().to_json(agentEnricher)
    serialized_agentCreator = AgentSpecSerializer().to_json(agentCreator)
    serialized_agentCompetition = AgentSpecSerializer().to_json(agentCompetition)
            
    loader = AgentSpecLoader(tool_registry=tool_registry)
    wayflow_agentExtractor = loader.load_json(serialized_agentExtractor) 
    wayflow_agentAudioExtractor = loader.load_json(serialized_agentAudioExtractor)
    wayflow_agentEnricher = loader.load_json(serialized_agentEnricher)
    wayflow_agentCreator = loader.load_json(serialized_agentCreator)
    wayflow_agentCompetition = loader.load_json(serialized_agentCompetition)
    
    conversationExtractor = wayflow_agentExtractor.start_conversation()
    conversationExtractor.append_user_message(f"Extract handwritten text from the following image URL: {image_path}")
    conversationExtractor.execute()
    messages = conversationExtractor.get_messages()
        
    clean_messages = messages[-1].contents[0].content.split(":")[1].strip()
    print("Extracted Handwritten Text:\n", clean_messages)

    if audio_url:
        conversationAudioExtractor = wayflow_agentAudioExtractor.start_conversation()
        conversationAudioExtractor.append_user_message(f"Extract audio text from the following audio file: {audio_url}")
        conversationAudioExtractor.execute()
        messages = conversationAudioExtractor.get_messages()
        
        audio_text = messages[-1].contents[0].content.split(":")[1].strip()
        print("Extracted Audio Text:\n", audio_text)
    else:
        audio_text = ""

    conversationEnricher = wayflow_agentEnricher.start_conversation()
    conversationEnricher.append_user_message(f"Enrich the following idea into a detailed description: {clean_messages}, {audio_text}")
    conversationEnricher.execute()
    messages = conversationEnricher.get_messages()
        
    
    spec = messages[-1].contents[0].content
    print("Enriched Idea:\n", spec)
    
    conversationCompetition = wayflow_agentCompetition.start_conversation()
    conversationCompetition.append_user_message(spec)
    conversationCompetition.execute()
    messages = conversationCompetition.get_messages()
    
    competition_output = ""

    if os.path.exists("competition_output.txt"):
        with open("competition_output.txt", "r", encoding="utf-8") as f:
            competition_output = f.read()
    else:
        competition_output = "No competition analysis found."
    
    print("Competition Analysis Output:\n", competition_output)
    
    conversationCreator = wayflow_agentCreator.start_conversation()
    conversationCreator.append_user_message(spec)
    conversationCreator.execute()
    messages = conversationCreator.get_messages()
    
    print(messages)
    
    structure_json_str = messages[-1].contents[0].content
    for msg in messages:
        print(msg.contents)
    
    try:
        data = json.loads(structure_json_str)
        project_root = None

        for folder_content in data.values():
            if not isinstance(folder_content, dict):
                continue
            for path, desc in folder_content.items():
                if path == "functions" or not isinstance(desc, str):
                    continue
                # e.g. "MyApp/frontend/index.html" -> "MyApp"
                first_segment = path.split("/")[0]
                if first_segment:
                    project_root = first_segment
                    break
            if project_root:
                break

        if project_root is None:
            # Fallback if JSON didn’t contain paths as expected
            project_root = "GeneratedProject"
            os.makedirs(project_root, exist_ok=True)

    except Exception as e:
        print("Error parsing structure JSON to infer project root:", e)
        structure_json_str = ""
        project_root = "GeneratedProject"
        os.makedirs(project_root, exist_ok=True)

    # Return:
    # - spec (enriched idea / description)
    # - structure_json_str (JSON string with folders/files/functions)
    # - project_root (top-level directory where code was created)
    return spec, structure_json_str, project_root, competition_output