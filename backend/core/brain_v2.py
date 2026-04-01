import os
import json
import datetime
from groq import Groq
from typing import List, Dict

from core.memory import MemoryCore
from skills.system_skill import AVAILABLE_SKILLS
from ai_core import FRIDAY_SYSTEM_PROMPT

AI_PROVIDER = os.getenv("FRIDAY_AI_PROVIDER", "groq")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

class FRIDAYBrainV2:
    def __init__(self):
        self.provider = AI_PROVIDER
        self.memory = MemoryCore()
        self.tools = [skill.to_tool_schema() for skill in AVAILABLE_SKILLS]
        self.skills_map = {skill.name: skill for skill in AVAILABLE_SKILLS}
        
        self.session_id = "default_session"
        print(f"[FRIDAY V2] Neural Core initializing with provider: {self.provider.upper()}")
        self._init_client()

    def _init_client(self):
        if self.provider == "groq":
            if not GROQ_API_KEY:
                raise ValueError("GROQ_API_KEY required for tool calling in V2")
            self._client = Groq(api_key=GROQ_API_KEY)
            self._model = "llama-3.3-70b-versatile" # Latest model supports tools great
            print(f"[FRIDAY V2] Client ready. Model: {self._model}")
        else:
            print("[FRIDAY V2] WARNING: V2 currently optimized for Groq tool calling. Falling back to simple mode.")
            self._client = None

    def _get_system_prompt(self) -> str:
        now = datetime.datetime.now().strftime("%A, %B %d %Y — %I:%M %p")
        return FRIDAY_SYSTEM_PROMPT.format(datetime=now) + "\n\nYou have access to several tools. If a user asks you to do something that matches a tool, CALL THE TOOL, do not just tell them how to do it."

    def think(self, user_input: str) -> str:
        """Process user input with memory retrieval and tool calling."""
        
        self.memory.add_message(self.session_id, "user", content=user_input)
        
       
        history = self.memory.get_recent_history(self.session_id, limit=6)
        
       
        messages = [{"role": "system", "content": self._get_system_prompt()}]
        messages.extend(history)
        
        if self.provider == "groq" and self._client:
            return self._think_groq(messages)
            
        return "I am offline or functioning without groq API keys, Boss."

    def _think_groq(self, messages: List[Dict]) -> str:
        # Initial AI Call
        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            tools=self.tools,
            tool_choice="auto",
            max_tokens=1024
        )
        
        response_msg = response.choices[0].message
        tool_calls = response_msg.tool_calls
        
        # Did the LLM decide to call a tool?
        if tool_calls:
            # Save assistant's intent to call a tool
            self.memory.add_message(
                self.session_id, 
                "assistant", 
                tool_calls=json.dumps([{"id": t.id, "function": {"name": t.function.name, "arguments": t.function.arguments}} for t in tool_calls])
            )
            messages.append(response_msg)
            
            # Execute the requested tools
            for tool_call in tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)
                
                print(f"[EXECUTING SKILL] {func_name} with args: {func_args}")
                
                # Run the actual skill
                try:
                    skill = self.skills_map[func_name]
                    result = skill.execute(**func_args)
                except Exception as e:
                    result = f"Error executing tool: {e}"
                
                # Save the tool output
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": func_name,
                    "content": str(result),
                })
                self.memory.add_message(
                    self.session_id,
                    "tool",
                    content=str(result),
                    tool_call_id=tool_call.id
                )
                
            # Send the tool output back to the LLM to formulate a final human response
            second_response = self._client.chat.completions.create(
                model=self._model,
                messages=messages
            )
            final_text = second_response.choices[0].message.content.strip()
            self.memory.add_message(self.session_id, "assistant", content=final_text)
            return final_text
            
        else:
            # Just normal text response
            text = response_msg.content.strip()
            self.memory.add_message(self.session_id, "assistant", content=text)
            return text

    def clear_memory(self):
        self.memory.clear_session(self.session_id)
        print("[FRIDAY V2] Memory purged.")

    def get_status(self) -> dict:
        return {
            "provider": self.provider,
            "model": self._model if hasattr(self, "_model") else "none",
            "conversation_turns": len(self.memory.get_recent_history(self.session_id, limit=100)),
            "status": "online"
        }

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
    brain = FRIDAYBrainV2()
    print("\nChat session (type 'exit' to quit):")
    while True:
        try:
            cmd = input("You: ")
            if cmd.lower() in ["exit", "quit"]: break
            r = brain.think(cmd)
            print("FRIDAY:", r)
        except KeyboardInterrupt:
            break

