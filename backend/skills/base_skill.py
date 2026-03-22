import json
from typing import Dict, Any, Optional

class BaseSkill:
    """
    Abstract Base Class for all F.R.I.D.A.Y skills.
    A skill translates to an LLM Tool (Function Call).
    """
    
    name: str = "base_skill"
    description: str = "A generic skill"
    
    # JSON Schema for the tool arguments, compatible with OpenAI/Groq/Gemini tool calling
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": []
    }
    
    requires_confirmation: bool = False

    def execute(self, **kwargs) -> str:
        """Execute the skill and return a string observation for the LLM."""
        raise NotImplementedError("Skills must implement the execute method.")

    @classmethod
    def to_tool_schema(cls) -> Dict[str, Any]:
        """Convert the skill definition into an LLM tool schema."""
        return {
            "type": "function",
            "function": {
                "name": cls.name,
                "description": cls.description,
                "parameters": cls.parameters
            }
        }
