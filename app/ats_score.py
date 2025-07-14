from difflib import SequenceMatcher
import re

def fuzzy_match(a, b):
    a = a.lower().replace(".", "").replace("-", "").replace(" ", "")
    b = b.lower().replace(".", "").replace("-", "").replace(" ", "")
    return (
        SequenceMatcher(None, a, b).ratio() > 0.8 or
        a in b or b in a
    )

def extract_skills_from_resume(resume_json):
    all_text_sources = []

    if resume_json.get("skills"):
        all_text_sources += resume_json["skills"]

    if resume_json.get("experience"):
        for exp in resume_json["experience"]:
            if isinstance(exp, dict):
                for val in exp.values():
                    if isinstance(val, str):
                        all_text_sources.append(val)

    if resume_json.get("projects"):
        for proj in resume_json["projects"]:
            if isinstance(proj, dict):
                for val in proj.values():
                    if isinstance(val, str):
                        all_text_sources.append(val)

    if resume_json.get("summary"):
        all_text_sources.append(resume_json["summary"])

    resume_terms = set()
    for text in all_text_sources:
        text = text.lower()

        # Tokenization
        tokens = re.findall(r'\b[\w\.\+\#]+\b', text.lower())
        resume_terms.update(tokens)
        resume_terms.update(' '.join(tokens[i:i+2]) for i in range(len(tokens)-1))  # bigrams
        resume_terms.update(' '.join(tokens[i:i+3]) for i in range(len(tokens)-2))  # trigrams

    ngrams = set()
    for text in all_text_sources:
        tokens = text.lower().split()
        for i in range(len(tokens) - 1):
            bigram = tokens[i] + " " + tokens[i + 1]
            ngrams.add(bigram)
        for i in range(len(tokens) - 2):
            trigram = tokens[i] + " " + tokens[i + 1] + " " + tokens[i + 2]
            ngrams.add(trigram)

    return list(resume_terms | ngrams)

def calculate_ats_score(resume_json, ats_keywords=None, role_name=None, alignment_rating=None):
    if ats_keywords is None:
        ats_keywords = []

    score = 0
    breakdown = {}

    # Contact Info
    contact_score = 0
    if resume_json.get("email"): contact_score += 5
    if resume_json.get("phone"): contact_score += 5
    score += contact_score
    breakdown["Contact Info"] = contact_score

    # Education
    edu_score = 10 if resume_json.get("education") else 0
    score += edu_score
    breakdown["Education"] = edu_score

    # Experience
    exp_score = 20 if resume_json.get("experience") else 0
    score += exp_score
    breakdown["Experience"] = exp_score

    # Projects
    proj_score = 20 if resume_json.get("projects") else 0
    score += proj_score
    breakdown["Projects"] = proj_score

    # Summary Alignment
    alignment_score = 0
    if alignment_rating:
        alignment_rating = alignment_rating.lower()
        if "strong alignment" in alignment_rating:
            alignment_score = 20
        elif "moderate alignment" in alignment_rating:
            alignment_score = 10
        elif "poor alignment" in alignment_rating:
            alignment_score = 0
    breakdown["Summary Alignment"] = alignment_score
    score += alignment_score

    # Additional Contributions
    extras = []
    if resume_json.get("achievements"):
        extras += resume_json["achievements"]
    if resume_json.get("certifications"):
        extras += resume_json["certifications"]

    add_score = 10 if extras else 0
    breakdown["Additional Contributions"] = add_score
    score += add_score

    return min(score, 100), breakdown, []  
