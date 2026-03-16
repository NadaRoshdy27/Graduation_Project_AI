"""
main.py
TalentTree AI - FastAPI service (no database).
Run: uvicorn main:app --reload
"""

import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# ==========================================
# LOGGING
# ==========================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ==========================================
# LLM CONFIGS PER AGENT
# ==========================================

LLM_CONFIGS = {
    "PRICING":   {"max_new_tokens": 80,  "temperature": 0.1},
    "MARKETING": {"max_new_tokens": 220, "temperature": 0.7},
    "CAPTION":   {"max_new_tokens": 180, "temperature": 0.7},
    "PLANNER":   {"max_new_tokens": 250, "temperature": 0.6},
    "GENERAL":   {"max_new_tokens": 200, "temperature": 0.7},
}

llms = {
    agent: HuggingFaceEndpoint(
        repo_id="meta-llama/Llama-3.1-8B-Instruct",
        max_new_tokens=config["max_new_tokens"],
        temperature=config["temperature"],
    )
    for agent, config in LLM_CONFIGS.items()
}

chat_models = {agent: ChatHuggingFace(llm=llm) for agent, llm in llms.items()}

# ==========================================
# IN-RAM SESSION MEMORY
# ==========================================

seller_memories: dict[str, list[dict]] = {}
MAX_MEMORY = 10


def add_to_memory(seller_id: str, role: str, message: str) -> None:
    if seller_id not in seller_memories:
        seller_memories[seller_id] = []
    seller_memories[seller_id].append({"role": role, "content": message})
    if len(seller_memories[seller_id]) > MAX_MEMORY:
        seller_memories[seller_id] = seller_memories[seller_id][-MAX_MEMORY:]


def get_memory(seller_id: str) -> str:
    history = seller_memories.get(seller_id, [])
    formatted = "Conversation History:\n"
    for msg in history[-6:]:
        formatted += f"{msg['role']}: {msg['content']}\n"
    return formatted


# ==========================================
# PROMPTS
# ==========================================

router_template = """
You are a strict classifier.
Classify the request into ONE label only:
PRICING / MARKETING / PLANNER / CAPTION / GENERAL
Return ONLY the label word. No explanation.
Request: {user_input}
"""

pricing_template = """
You are a pricing assistant.

Calculation rules:
- Total Cost = raw material cost + manufacturing cost
- Luxury audience: Price = Total Cost x 4 (minimum)
- Mass market audience: Price = Total Cost x 2

Reply using ONLY this exact format, no extra text:

Cost: [total cost]
Price: [total cost x multiplier]
Margin: [multiplier]x
Reason: [max 10 words]

Brand: {brand_name} | Audience: {target_audience} | Category: {category}
Request: {user_input}
"""
marketing_template = """
You are a Marketing Consultant for Talentree marketplace.
Brand: {brand_name} | Audience: {target_audience} | Category: {category}

Rules:
- Maximum 2 marketing ideas
- Each idea under 20 words
- No long explanations

User Request: {user_input}
"""

planner_template = """
You are a Senior Marketing Strategist. Create a 30-Day Marketing Plan.
Brand: {brand_name} | Audience: {target_audience} | Category: {category}

Rules:
- Only Week 1 to Week 4 headings
- Maximum 2 bullet points per week
- Each bullet under 15 words
- No extra explanations

Request: {user_input}
"""

caption_template = """
You are a Social Media Caption Expert.
Brand: {brand_name} | Tone: {tone} | Category: {category}

Rules:
- Exactly 3 captions
- Maximum 8 words per caption (not counting hashtags)
- No filler words like "Unleash", "Make a statement", "Get ready"
- Style: clean, minimal, confident
- End each caption with 1 relevant hashtag only

Product: {user_input}
"""

general_template = """
You are a Business Consultant for Talentree marketplace sellers.
Answer clearly and briefly in maximum 5 lines:
{user_input}
"""

TEMPLATES = {
    "PRICING":   pricing_template,
    "MARKETING": marketing_template,
    "PLANNER":   planner_template,
    "CAPTION":   caption_template,
}

HOLIDAY_KEYWORDS = [
    "EID", "RAMADAN", "CHRISTMAS", "NEW YEAR", "HOLIDAY",
    "BLACK FRIDAY", "PROMOTION", "SALE", "OFFER",
]

# ==========================================
# CORE CHAT LOGIC
# ==========================================


def talentree_chat(user_query: str, seller: dict) -> str:
    seller_id = seller["seller_id"]
    add_to_memory(seller_id, "User", user_query)

    router_chain = (
        ChatPromptTemplate.from_template(router_template)
        | chat_models["GENERAL"]
        | StrOutputParser()
    )
    raw = router_chain.invoke({"user_input": user_query}).strip().upper()

    if any(word in user_query.upper() for word in HOLIDAY_KEYWORDS):
        category = "MARKETING"
    elif "PRICE" in raw or "PRICING" in raw:
        category = "PRICING"
    elif "MARKET" in raw:
        category = "MARKETING"
    elif "PLAN" in raw:
        category = "PLANNER"
    elif "CAPTION" in raw:
        category = "CAPTION"
    else:
        category = "GENERAL"

    logger.info("seller_id=%s  routed_to=%s", seller_id, category)

    selected_template = TEMPLATES.get(category, general_template)
    memory_ctx = get_memory(seller_id)
    combined = selected_template + f"\n\n{memory_ctx}\nCurrent Request:\n{{user_input}}"

    final_chain = (
        ChatPromptTemplate.from_template(combined)
        | chat_models.get(category, chat_models["GENERAL"])
        | StrOutputParser()
    )

    response = final_chain.invoke({**seller, "user_input": user_query})
    add_to_memory(seller_id, "Assistant", response)
    return response


# ==========================================
# FASTAPI APP
# ==========================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("TalentTree AI service starting.")
    yield
    logger.info("TalentTree AI service shutting down.")
    seller_memories.clear()


app = FastAPI(
    title="TalentTree AI Chat API",
    description="Multi-agent AI assistant — Pricing · Marketing · Planner · Caption · General",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# SCHEMAS
# ==========================================


class ChatRequest(BaseModel):
    seller_id: str = Field(..., description="Unique seller session ID")
    brand_name: str = Field(..., description="Seller's brand name")
    category: str = Field(..., description="Product category")
    target_audience: str = Field(..., description="Target audience description")
    tone: str = Field(default="Professional", description="Caption tone")
    message: str = Field(..., description="The seller's message")


class ChatResponse(BaseModel):
    response: str


# ==========================================
# ENDPOINTS
# ==========================================

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "service": "TalentTree AI Chat API"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
def chat(request: ChatRequest):
    seller = {
        "seller_id": request.seller_id,
        "brand_name": request.brand_name,
        "category": request.category,
        "target_audience": request.target_audience,
        "tone": request.tone,
    }
    try:
        logger.info("Chat request: seller_id=%s", request.seller_id)
        ai_response = talentree_chat(request.message, seller)
        return ChatResponse(response=ai_response)
    except Exception as e:
        logger.exception("AI error for seller_id=%s", request.seller_id)
        raise HTTPException(status_code=500, detail=f"AI processing error: {str(e)}")


@app.delete("/memory/{seller_id}", tags=["Memory"])
def clear_memory(seller_id: str):
    if seller_id in seller_memories:
        del seller_memories[seller_id]
        return {"message": f"Memory cleared for: {seller_id}"}
    return {"message": f"No memory found for: {seller_id}"}