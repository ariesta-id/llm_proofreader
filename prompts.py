"""
Prompts and JSON Schemas for the GPT-5 Structured Proofreader.
"""

# JSON schema for the proofread structured output
PROOFREAD_SCHEMA = {
    "format": {
        "type": "json_schema",
        "name": "proofread_result",
        "schema": {
            "type": "object",
            "properties": {
                "original_text": {
                    "type": "string",
                    "description": "The exact original text that was provided for proofreading."
                },
                "corrected_text": {
                    "type": "string",
                    "description": (
                        "The corrected version of the text, focusing strictly on resolving grammatical errors, "
                        "spelling mistakes, and punctuation issues. Do NOT rewrite the text's style or voice here; "
                        "preserve the original writer's style and ownership completely."
                    )
                },
                "corrections": {
                    "type": "array",
                    "description": (
                        "A list of necessary grammatical, spelling, and punctuation corrections. "
                        "Only include actual errors (no stylistic preferences or over-corrections)."
                    ),
                    "items": {
                        "type": "object",
                        "properties": {
                            "original_phrase": {
                                "type": "string",
                                "description": "The exact phrase or word from the original text that was changed."
                            },
                            "corrected_phrase": {
                                "type": "string",
                                "description": "The replacement phrase or word used in the corrected text."
                            },
                            "category": {
                                "type": "string",
                                "enum": ["spelling", "grammar", "style", "punctuation", "other"],
                                "description": "The classification of the error or improvement."
                            },
                            "explanation": {
                                "type": "string",
                                "description": "The reason why the change was made and how it improves the text."
                            }
                        },
                        "required": ["original_phrase", "corrected_phrase", "category", "explanation"],
                        "additionalProperties": False
                    }
                },
                "overall_feedback": {
                    "type": "string",
                    "description": "General summary and feedback on the writing quality, tone, and readability (no stylistic suggestions here)."
                },
                "stylistic_suggestions": {
                    "type": "array",
                    "description": (
                        "Optional stylistic rewriting recommendations for sentences that could flow better or sound "
                        "more natural, while following the writer's existing style and not changing the meaning."
                    ),
                    "items": {
                        "type": "object",
                        "properties": {
                            "original_sentence": {
                                "type": "string",
                                "description": "The original sentence that can be improved."
                            },
                            "suggested_rewrite": {
                                "type": "string",
                                "description": "The proposed rewritten sentence matching the author's voice but flowing better."
                            },
                            "assumption": {
                                "type": "string",
                                "description": "The assumption made about the writer's original meaning or intent."
                            },
                            "explanation": {
                                "type": "string",
                                "description": "Why this suggestion improves flow or readability."
                            }
                        },
                        "required": ["original_sentence", "suggested_rewrite", "assumption", "explanation"],
                        "additionalProperties": False
                    }
                }
            },
            "required": ["original_text", "corrected_text", "corrections", "overall_feedback", "stylistic_suggestions"],
            "additionalProperties": False
        }
    }
}

# The main prompt template for the proofreader
PROOFREAD_PROMPT_TEMPLATE = (
    "You are a meticulous, professional proofreader. Your primary objective is to review "
    "the text thoroughly and identify grammatical errors, spelling mistakes, and typos.\n\n"
    "{language_instruction}\n\n"
    "Follow these strict instructions to perform the proofreading in two distinct steps:\n\n"
    "1. FIRST PASS: GRAMMAR & TYPOS (No Style Rewriting)\n"
    "   - Scan the text repeatedly and thoroughly for spelling, grammar, and punctuation errors.\n"
    "   - List only necessary corrections. Do NOT over-correct or perform editorial rewriting here.\n"
    "   - Do not comment on the content of the writing.\n"
    "   - Respect the original writer's voice and ownership completely. Do not introduce stylistic changes "
    "in this stage.\n"
    "   - If there are many grammatical/typo errors, stylistic changes must be kept to an absolute minimum.\n\n"
    "2. SECOND PASS: STYLISTIC REWRITING RECOMMENDATIONS\n"
    "   - Because the writer may not be a native English speaker, separate any stylistic improvements into a second pass.\n"
    "   - Identify sentences that would benefit significantly from a rewrite to flow better or sound more natural.\n"
    "   - For each recommended rewrite, you must follow the writer's existing style, must NOT change the meaning of the words, "
    "and must clearly state any assumptions you are making about the writer's original intent.\n\n"
    "Structure your output strictly according to the requested JSON schema:\n"
    "- 'corrected_text': The final text incorporating ONLY the spelling, grammar, and punctuation corrections from the First Pass. "
    "No stylistic rewrites should be applied here.\n"
    "- 'corrections': The detailed array of corrections made in the First Pass.\n"
    "- 'overall_feedback': Provide your high-level feedback summary here regarding writing quality, tone, and grammar.\n"
    "- 'stylistic_suggestions': The structured array of your recommended sentence rewrites, assumptions, and explanations from the Second Pass.\n\n"
    "Text to proofread:\n{text}"
)

def get_proofread_prompt(text: str, language: str = "en-US") -> str:
    """
    Generates the proofread prompt for a given text input.
    """
    if language == "en-GB":
        lang_instruction = (
            "CRITICAL: The target dialect for this proofreading is British English (UK). "
            "Ensure that all spelling (e.g., 'colour' instead of 'color', 'organise' instead of 'organize', "
            "'centre' instead of 'center'), vocabulary, and punctuation choices strictly adhere to British English standards."
        )
    else:
        lang_instruction = (
            "CRITICAL: The target dialect for this proofreading is American English (US). "
            "Ensure that all spelling (e.g., 'color' instead of 'colour', 'organize' instead of 'organise', "
            "'center' instead of 'centre'), vocabulary, and punctuation choices strictly adhere to American English standards."
        )
    return PROOFREAD_PROMPT_TEMPLATE.format(language_instruction=lang_instruction, text=text)


