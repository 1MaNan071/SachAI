"""Disambiguation node - resolves ambiguous references.

Clarifies pronouns and other references so claims make sense on their own.
"""

import logging
from typing import Dict, List, Optional, Tuple

from langchain_core.language_models.chat_models import BaseChatModel
from pydantic import BaseModel, Field

from claim_extractor.config import DISAMBIGUATION_CONFIG
from claim_extractor.prompts import DISAMBIGUATION_SYSTEM_PROMPT, HUMAN_PROMPT
from claim_extractor.schemas import DisambiguatedContent, SelectedContent, State
from utils import (
    call_llm_with_structured_output,
    get_llm,
    process_with_voting,
    remove_following_sentences,
)

logger = logging.getLogger(__name__)

# Disambiguation settings - we use multiple completions
# to ensure consistency in how references are resolved
COMPLETIONS = DISAMBIGUATION_CONFIG["completions"]
MIN_SUCCESSES = DISAMBIGUATION_CONFIG["min_successes"]

# --- START OF ADDED CODE ---
# A list of common pronouns to check for ambiguity.
AMBIGUOUS_PRONOUNS = {"it", "he", "she", "they", "them", "his", "her", "its", "their"}
# --- END OF ADDED CODE ---


class DisambiguationOutput(BaseModel):
    """Response schema for disambiguation LLM calls."""

    disambiguated_sentence: Optional[str] = Field(
        default=None, description="The sentence with ambiguities resolved"
    )
    cannot_be_disambiguated: bool = Field(
        description="Flag indicating if the sentence cannot be disambiguated",
    )


async def _single_disambiguation_attempt(
    selected_item: SelectedContent, llm: BaseChatModel
) -> Tuple[bool, Optional[str]]:
    """Try to disambiguate a single sentence.

    Args:
        selected_item: Selected content to disambiguate
        llm: LLM instance

    Returns:
        (success, disambiguated_sentence)
    """
    sentence = selected_item.processed_sentence

    # Get context but remove following sentences
    # We don't want to rely on future info that might not be available
    modified_context = remove_following_sentences(
        selected_item.original_context_item.context_for_llm
    )

    # Prep the prompt
    messages = [
        ("system", DISAMBIGUATION_SYSTEM_PROMPT),
        (
            "human",
            HUMAN_PROMPT.format(
                excerpt=modified_context,
                sentence=sentence,
            ),
        ),
    ]

    # Call the LLM
    response = await call_llm_with_structured_output(
        llm=llm,
        output_class=DisambiguationOutput,
        messages=messages,
        context_desc=f"disambiguation attempt for '{sentence}'",
    )

    # Skip sentences we can't disambiguate - better to drop them
    # than have unclear claims
    if (
        not response
        or not response.disambiguated_sentence
        or response.cannot_be_disambiguated
    ):
        return False, None

    return True, response.disambiguated_sentence.strip()


def _create_disambiguated_content(
    disambiguated_sentence: str, selected_item: SelectedContent
) -> DisambiguatedContent:
    """Package the disambiguated content.

    Args:
        disambiguated_sentence: Sentence with resolved references
        selected_item: Original selected content

    Returns:
        DisambiguatedContent object
    """
    sentence = selected_item.processed_sentence
    logger.info(f"Disambiguated: '{sentence}' → '{disambiguated_sentence}'")
    return DisambiguatedContent(
        disambiguated_sentence=disambiguated_sentence,
        original_selected_item=selected_item,
    )


async def disambiguation_node(state: State) -> Dict[str, List[DisambiguatedContent]]:
    """Resolve ambiguous references in sentences.

    Args:
        state: Current workflow state

    Returns:
        Dictionary with disambiguated_contents key
    """
    selected_contents = state.selected_contents or []

    if not selected_contents:
        logger.warning("Nothing to disambiguate")
        return {}

    # --- START OF CHANGED BLOCK ---
    # Create a "fast lane" for sentences without obvious pronouns.
    unambiguous_contents = []
    ambiguous_contents = []
    
    # Sort claims into two lists: simple ones to pass through, complex ones for the LLM.
    for item in selected_contents:
        words = set(item.processed_sentence.lower().split())
        if not AMBIGUOUS_PRONOUNS.intersection(words):
            # If no pronouns are found, add it to the "fast lane"
            unambiguous_contents.append(
                _create_disambiguated_content(item.processed_sentence, item)
            )
            logger.info(f"Bypassing disambiguation for simple claim: '{item.processed_sentence}'")
        else:
            # If it has a pronoun, it needs the LLM's analysis
            ambiguous_contents.append(item)
    
    disambiguated_from_llm = []
    if ambiguous_contents:
        logger.info(f"Sending {len(ambiguous_contents)} claims to LLM for disambiguation.")
        # Get LLM with temperature 0.2 for multiple completions
        llm = get_llm(completions=COMPLETIONS)

        # Process only the ambiguous contents with voting
        disambiguated_from_llm = await process_with_voting(
            items=ambiguous_contents,
            processor=_single_disambiguation_attempt,
            llm=llm,
            completions=COMPLETIONS,
            min_successes=MIN_SUCCESSES,
            result_factory=_create_disambiguated_content,
            description="sentence for disambiguation",
        )

    # Combine the results from the "fast lane" and the LLM processing.
    final_disambiguated_contents = unambiguous_contents + disambiguated_from_llm
    # --- END OF CHANGED BLOCK ---

    if not final_disambiguated_contents:
        logger.info("Nothing could be disambiguated")
        return {}

    logger.info(
        f"Successfully disambiguated a total of {len(final_disambiguated_contents)} items"
    )
    return {"disambiguated_contents": final_disambiguated_contents}
