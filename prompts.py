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
                    "description": (
                        "General summary and feedback on the writing. This must start with a section summarizing "
                        "the writing quality and tone, followed by a separate, clearly demarcated section titled "
                        "'Stylistic Rewriting Recommendations' proposing optional suggestions for sentences that "
                        "could flow better, including stated assumptions about the writer's intent."
                    )
                }
            },
            "required": ["original_text", "corrected_text", "corrections", "overall_feedback"],
            "additionalProperties": False
        }
    }
}

# The main prompt template for the proofreader
PROOFREAD_PROMPT_TEMPLATE = (
    "You are a meticulous, professional proofreader. Your primary objective is to review "
    "the text thoroughly and identify grammatical errors, spelling mistakes, and typos.\n\n"
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
    "- 'overall_feedback': Provide your feedback here. Start with a brief, objective summary of the grammatical issues, "
    "followed by a dedicated, clearly labelled 'Stylistic Rewriting Recommendations' section that lists your suggestions, "
    "re-written sentences, and stated assumptions.\n\n"
    "Text to proofread:\n{text}"
)

def get_proofread_prompt(text: str) -> str:
    """
    Generates the proofread prompt for a given text input.
    """
    return PROOFREAD_PROMPT_TEMPLATE.format(text=text)

