import os
from pyagentspec.agent import Agent
from pyagentspec.llms.openaicompatibleconfig import OpenAiCompatibleConfig
from pyagentspec.serialization import AgentSpecSerializer
from wayflowcore.agentspec import AgentSpecLoader
from gradio_client import Client, file
from dotenv import load_dotenv

load_dotenv()

# -------------------------------------------------------------------
# LLM CONFIG (Oracle AgentSpec -> Wayflow -> Gemini OpenAI-compatible)
# -------------------------------------------------------------------

GEMINI_MODEL_ID = "gemini-2.5-flash"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

llm_config = OpenAiCompatibleConfig(
    name="gemini-llm",
    model_id=GEMINI_MODEL_ID,
    url=GEMINI_URL,
    # If your version supports it, this helps avoid streaming issues:
    # stream=False,
)


# -------------------------------------------------------------------
# STEP 1 – Extract handwriting from whiteboard image (DeepSeek OCR)
# -------------------------------------------------------------------

def extract_handwriting(image_path: str) -> str:
    """
    Call the DeepSeek OCR Gradio Space to extract & correct handwriting
    from the provided image path. Returns MARKDOWN text.
    """
    print("Extracting handwriting from image:", image_path)

    clientOCR = Client("LauzHack/DeepSeek-OCR", token=os.getenv("HF_TOKEN"))

    # 1) Load image
    input_image = clientOCR.predict(
        file(image_path),  # local file path
        1,                 # page_num
        api_name="/load_image",
    )

    # 2) Run OCR + markdown postprocessing
    text, md_text, extra, out_img, gallery = clientOCR.predict(
        file(input_image),
        file(image_path),
        "Gundam",  # mode
        "📋 Markdown",  # task
        (
            "Extract the handwriting, correct typos and provide it in markdown "
            "format. Make sure the result makes sense."
        ),
        1,  # page_num
        api_name="/run",
    )

    return md_text


# -------------------------------------------------------------------
# STEP 2 – Enrich the idea using Kimi VL via Gradio
# -------------------------------------------------------------------

def enrich_idea(idea: str) -> str:
    """
    Call the Kimi VL Gradio Space to expand a short idea into a richer,
    more detailed entrepreneurial concept.
    """
    print("Enriching idea via Kimi VL")

    clientIdea = Client("LauzHack/Kimi-VL-A3B-Thinking", token=os.getenv("HF_TOKEN"))

    system_prompt = f"""
You are a world-class creative assistant that helps people to enrich their ideas.
You take a short idea and expand it into a detailed and compelling description.
The ideas are related to entrepreneurship, startups, and business innovation.
You should find use cases, useful features, and if necessary a technical approach to implement the idea.

Here is the idea to enrich:

{idea}
"""

    enriched_idea = clientIdea.predict(
        system_prompt=system_prompt,
        api_name="/predict",
    )

    # Your HF space returns a nested structure; keep your parsing logic:
    # enriched_idea[0][0][1] is the full text, then split on "Summary"
    raw_text = enriched_idea[0][0][1]
    if "Summary" in raw_text:
        return raw_text.split("Summary", 1)[1].strip()
    return raw_text.strip()


# -------------------------------------------------------------------
# STEP 3 – AgentSpec + Wayflow: Turn enriched idea into a clean spec
# -------------------------------------------------------------------

async def create_spec(image_path: str) -> str:
    """
    Full pipeline:
    1. OCR on whiteboard image -> markdown text
    2. Enrich with Kimi VL -> richer idea
    3. Use an Oracle AgentSpec agent (via Wayflow) with Gemini LLM
       to turn the enriched idea into a structured project specification.
    """

    # 1) Extract raw idea from handwriting (DeepSeek OCR)
    md_text = extract_handwriting(image_path)
    print("Extracted Markdown text from image:\n", md_text)

    # 2) Enrich the idea (Kimi VL)
    enriched = enrich_idea(md_text)
    print("Enriched idea:\n", enriched)

    # 3) Define an AgentSpec agent that turns the enriched idea into a spec
    agentEnricher = Agent(
        name="Project Spec Agent",
        llm_config=llm_config,
        tools=[],  # IMPORTANT: no tools here -> avoids streaming tool_call issues
        system_prompt=(
            "You are a senior product architect. "
            "You receive a rich, detailed startup idea and you must turn it into "
            "a clear, structured project specification.\n\n"
            "Your output MUST be in markdown with the following sections:\n"
            "1. Problem Statement\n"
            "2. Target Users\n"
            "3. Core Features\n"
            "4. Technical Architecture (high-level)\n"
            "5. Possible Extensions\n"
        ),
    )

    # Serialize AgentSpec → load into Wayflow
    serialized_agent = AgentSpecSerializer().to_json(agentEnricher)
    loader = AgentSpecLoader(tool_registry={})  # no tools registered
    wayflow_agent = loader.load_json(serialized_agent)

    # Start a conversation and run it ASYNC
    conversation = wayflow_agent.start_conversation()
    conversation.append_user_message(
        "Here is a detailed idea extracted from a whiteboard and enriched:\n\n"
        f"{enriched}\n\n"
        "Please produce the project specification in the markdown structure described "
        "in your system prompt."
    )

    # 🔴 IMPORTANT: use the async API inside FastAPI
    await conversation.execute_async()

    messages = conversation.get_messages()
    # Last assistant message content
    spec_text = messages[-1].contents[0].content
    return spec_text
