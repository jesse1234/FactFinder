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
