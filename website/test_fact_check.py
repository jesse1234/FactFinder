from .rag_module import fact_check_crew

def parse_raw_content(raw_content):
    sections = {}
    current_section = None
    lines = raw_content.splitlines()

    for line in lines:
        line = line.strip()
        if line.startswith("**") and line.endswith("**"):
            current_section = line.strip("*:")
            sections[current_section] = []
        elif current_section:
            sections[current_section].append(line)

    # Join lines in each section and return as a dictionary
    return {key: "\n".join(value) for key, value in sections.items()}

def test_fact_check_crew():
    claim = "Did President Ruto pay 500 million to host the Grammys?"
    result = fact_check_crew.kickoff({'claim': claim})

    raw_content = result.raw
    parsed_content = parse_raw_content(raw_content)

    assert "Summary of Findings" in parsed_content, "Summary of Findings is missing"
    assert "Verdict" in parsed_content, "Verdict is missing"
    assert len(parsed_content.get('References', '').splitlines()) > 0, "References are missing"




analysis_task = Task(
    description = (
        "As a Fact Analyst, your task is to thoroughly analyze the retrieved information and provide a comprehensive, fact-checked response to the claim: {claim}.\n"
        "\n"
        "Your analysis should include the following:\n"
        "1. **Summary of Findings:** Present a set of bullet points that describe the key details and claims from each relevant article. Reference each article by its title and URL, but do not enumerate them as 'Article 1', 'Article 2', etc. Instead, integrate the article's source or a key identifying detail directly into your explanation. Focus on clearly describing the information and how it relates to the claim.\n"
        "2. **Cross Verification:** Cross-verify the information across different sources, highlighting any agreements of discrepancies among them.\n"
        "3. **Contextual Background:** Include any necessary background information that helps in understanding the claim and its significance.\n"
        "4. **Conclusion:** Based on your analysis, draw a well-reasoned conclusion about the validity of the claim.\n"
        "5. **Verdict:** Clearly state your verdict as one of the following options: True, False, Partly True, Partly False or Not Enough Information.\n"
        "6. **References:** List all the articles you used in your analysis, including their titles and URLs.\n"
        "\n"
        "The response should be structured in the following format:\n"
        "\n"
        "**Summary of Findings:**\n"
        "- [Describe details from a relevant article, referencing the article's title or source within the explanation, and include the URL at the end.]\n"
        "- [Describe details from another relevant article in a similar fashion, ensuring the narrative flows naturally.]\n"
        "- [Continue for all relevant articles.]\n"
        "\n"
        "**Cross-Verification:**\n"
        "- Compare and contrast the information from the articles...\n"
        "\n"
        "**Contextual Background:**\n"
        "- Provide any additional background information...\n"
        "\n"
        "**Verdict:**\n"
        "- Your verdict here...\n"
        "\n"
        "**References**\n"
        "- [Title of article 1] - [URL of article 1]\n"
        "- [Title of article 2] - [URL of article 2]\n"
        "[...]\n"
        "\n"
        "Ensure that your analysis and verdict are strictly supported by the retrieved context. Do not include any information not found in the context. DO NOT begin your answer with 'The first article ...' or 'The article ..., The article titled...'. DO NOT put the title or url of the articles in the **Summary of Findings** section, just give the information found in those articles"
        "\n"
    ),
    agent=Analyst_Agent,
    context=[retrieval_task],
    expected_output=(
        "A detailed, structured analysis of the claim, including summaries, cross-verification, contextual background, a conclusion, a verdict, and references."
    )
)