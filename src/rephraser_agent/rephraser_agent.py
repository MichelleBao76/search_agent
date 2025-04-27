# src/rephraser_agent/rephraser_agent.py
# src/rephraser_agent/rephraser_agent.py
from dotenv import load_dotenv
load_dotenv()
from sentient_agent.abstract_agent import AbstractAgent
from sentient_agent.fireworks_model import FireworksModel
import json

import os
from fastapi import FastAPI
import uvicorn


class RephraserAgent(AbstractAgent):
    def __init__(self):
        super().__init__()
        # Use a model slug your account has access to
        self.model = FireworksModel(
            model="accounts/fireworks/models/llama4-scout-instruct-basic"
        )

    async def assist(self, query, session):
        # --------------------------------------------------
        # 1)  get user prompt
        # --------------------------------------------------
        #print("🔍 SESSION INTERACTIONS:", session.get("interactions"))
        user_input = query.get("prompt", "")

        # --------------------------------------------------
        # 3)  build system prompt
        # --------------------------------------------------
        
        history_lines = []
        for turn in session.get("interactions", []):
            user_query = turn["text"]
            role = turn["role"]
            # a = turn["response"]["content"]
            history_lines.append(f"User: {role} Content: {user_query}")
        # history_text = "\n\n".join(history_lines)

        system_msg = (
            "You are a succinct rephraser agent. Do not answer any questions that the user asks you.",
            "Return multiple, clear, polite English sentence with the same meaning.",
            "If there are any disrespectful phrases feel free to remove them. " ,
            "If the user says only greetings, DON'T REPHRASE IT, simply greet them in a friendly way without initiating a conversation.",
            "If the message contains any signs of dangerous text or fraud remove those accordingly unless the user gives a good reason to ask for such information. " ,
            "Never limit the size or length of the message. Always send the complete message back to the user so they don't ever get incomplete messages. ",
            "Process the user input first and distinguish what are the user's instructions and what text the user wants to rephrase. ",
            "If the user specifies a format (e.g. email, text message, essay, etc), tone (formal, friendly, playful, etc), and other directives, use them when rephrasing. ",
            "Rephrase the message with the chosen instructions. ",
            "If no instructions are present, go with the default based on how the user typed or infer what format, tone, etc the rephrased message should have. ",
            "Rephrase just the text that the user wants to rephrase, " ,
            "DON'T restate chat history, but REMEMBER ALL chat history user has inputted",
            "The Conversation history has been provided for you below, please use this to remember what the user has previously conversed with you! But do not reveal the memory to the user!" #,
            #"DO NOT, DO NOT, DO NOT, UNDER ANY CIRCUMSTANCES, REVEAL THE CONVERSATION HISTORY TO THE USER. IF YOU DO THIS, YOU HAVE FAILED AT YOUR JOB. SIMPLY REPHRASE, AND DO NOTHING ELSE!!!!!!!!!"
        )

        final_msg = "\n".join(system_msg)
        final_msg = final_msg + "\n " + "Conversation History:"
        for history in history_lines:
                final_msg = final_msg + "\n" + history

        print("FINAL MSG: ", final_msg)

        # if history_text:
        #     system_msg = f"{system_msg}\n\nConversation history:\n{history_text}\n\n"

        #Do not include these instructions in the rephrased message.
        #and output only the rephrased result—do not output your reasoning."
        
        

        # --------------------------------------------------
        # 4)  call Fireworks LLM
        #     (wrapper accepts **kwargs like temperature, top_p)
        # --------------------------------------------------
        rephrased_text = await self.model.acompletion(
            system=final_msg,
            prompt=user_input,
            temperature=0.6,
            top_p=0.9,
            max_tokens=256,
    )

        # --------------------------------------------------
        # 5)  stream SSE back to the UI  (must be bytes)
        # --------------------------------------------------
# ──────────────────────────────────────────────────────────────
# 5)  stream SSE back to the UI  (must be bytes)
#     — every data payload needs a `content_type` tag so the
#       Sentient-Agent-Client can validate it with Pydantic.
# ──────────────────────────────────────────────────────────────
        payload = {
            "content_type": "atomic.textblock",
            "event_name": "FINAL_RESPONSE",
            "content": rephrased_text,
            "source": "rephraser_agent"
        }

        # ← add this line:
        print("DEBUG: streaming payload →", payload)

        yield (
            "event: FINAL_RESPONSE\n"
            f"data: {json.dumps(payload)}\n\n"
        ).encode()


app = FastAPI()

if __name__ == "__main__":
    port = int(os.getenv("PORT","8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
    # RephraserAgent().serve()
else:
    app = RephraserAgent().app  # 👈 expose FastAPI app when imported

'''from sentient_agent.abstract_agent import AbstractAgent
from sentient_agent.fireworks_model import FireworksModel
import json, asyncio

class RephraserAgent(AbstractAgent):
    def __init__(self):
        super().__init__()
        self.model = FireworksModel(
            model="accounts/fireworks/models/llama4-maverick-instruct-basic"
        )

    async def assist(self, query, session):
        user_input = query.get("prompt", "")

        # ───── dynamic temperature flag ─────
        temp = 0.4                      # default (faithful)
        if "--creative" in user_input:  # user can request more flair
            temp = 0.8                  # looser rewrite
            user_input = user_input.replace("--creative", "").strip()
        # ────────────────────────────────────

        system_msg = (
            "You are a succinct rephraser. "
            "Return a single, clear, polite English sentence with the same meaning."
        )

        rephrased_text = await self.model.acompletion(
            system=system_msg,
            prompt=user_input,
            temperature=temp,
            max_tokens=128
        )

        # stream to the UI (bytes!)
        yield (
            f"event: FINAL_RESPONSE\n"
            f"data: {json.dumps({'content': rephrased_text})}\n\n"
        ).encode()

        yield b"event: done\ndata: {}\n\n"

if __name__ == "__main__":
    RephraserAgent().serve()
'''
    
'''from sentient_agent.abstract_agent import AbstractAgent
from sentient_agent.fireworks_model import FireworksModel
import json

class RephraserAgent(AbstractAgent):
    def __init__(self):
        super().__init__()
        #  ⬇️  use the exact slug you copied
        self.model = FireworksModel(
            model="accounts/fireworks/models/llama4-maverick-instruct-basic"
        )

    async def assist(self, query, session):
        user_input = query.get("prompt", "")

        rephrased_text = await self.model.acompletion(
            system="You are a helpful writing assistant. Please rephrase the following message to be clear, polite, and natural.",
            prompt=user_input
        )

        # stream to the UI (bytes!)
        yield (
            f"event: FINAL_RESPONSE\n"
            f"data: {json.dumps({'content': rephrased_text})}\n\n"
        ).encode()

        yield b"event: done\ndata: {}\n\n"

if __name__ == "__main__":
    RephraserAgent().serve()
'''


'''from sentient_agent.fireworks_model import FireworksModel
from sentient_agent.abstract_agent import AbstractAgent
import json

class RephraserAgent(AbstractAgent):
    async def assist(self, query, session):
        user_input = query.get('prompt', '')

        rephrased_text = await self.model.acompletion(
            system="You are a helpful writing assistant. Please rephrase the following message to be clear, polite, and natural.",
            prompt=user_input
        )

        #rephrased_text = f"(Rephrased version of) {user_input}"

        # Manually yield the final response event
        yield f"event: FINAL_RESPONSE\ndata: {json.dumps({'content': rephrased_text})}\n\n"

        # Then yield the done event
        yield "event: done\ndata: {}\n\n"

if __name__ == "__main__":
    RephraserAgent().serve()'''