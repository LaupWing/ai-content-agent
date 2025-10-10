"""
Pydantic schemas for structured output
All agents return data in these formats
"""

from pydantic import BaseModel, Field
from typing import List, Optional

class BlogOutput(BaseModel):
    """Standard output format for all blog-related agents"""
    headline: str = Field(description="The blog headline/title")
    body: str = Field(description="The complete blog content in markdown format")
    ai_comment: str = Field(description="AI's explanation of what it did, suggestions, or insights about the content")

class HeadlineOption(BaseModel):
    """Single headline option with explanation"""
    headline: str = Field(description="The headline text")
    angle: str = Field(description="The angle/approach (personal, contrarian, data-driven, framework, list)")
    why_it_works: str = Field(description="Brief explanation of why this headline is effective")

class HeadlineOptions(BaseModel):
    """Multiple headline options for user to choose from"""
    options: List[HeadlineOption] = Field(description="5 diverse headline options")
    recommendation: str = Field(description="Which option is recommended and why")
