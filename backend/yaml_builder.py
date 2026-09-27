"""Convert the web form's JSON payload into RenderCV's YAML input structure."""


def build_yaml(form: dict) -> dict:
    cv: dict = {
        "name": form["name"].strip(),
        "location": (form.get("location") or "").strip() or None,
        "email": (form.get("email") or "").strip() or None,
    }

    social_networks = []
    if form.get("linkedin_username"):
        social_networks.append({"network": "LinkedIn", "username": form["linkedin_username"].strip()})
    if form.get("github_username"):
        social_networks.append({"network": "GitHub", "username": form["github_username"].strip()})
    if social_networks:
        cv["social_networks"] = social_networks

    sections: dict = {}

    objective = (form.get("objective") or "").strip()
    if objective:
        sections["Objective"] = [objective]

    education_entries = [_build_education_entry(e) for e in form.get("education") or [] if e.get("institution")]
    if education_entries:
        sections["education"] = education_entries

    experience_entries = [_build_experience_entry(e) for e in form.get("experience") or [] if e.get("company")]
    if experience_entries:
        sections["experience"] = experience_entries

    project_entries = [_build_project_entry(p) for p in form.get("projects") or [] if p.get("name")]
    if project_entries:
        sections["projects"] = project_entries

    extracurricular_lines = [
        line.strip() for line in (form.get("extracurricular") or "").splitlines() if line.strip()
    ]
    if extracurricular_lines:
        sections["Extracurricular"] = extracurricular_lines

    skill_entries = [
        {"label": s["label"].strip(), "details": s["details"].strip()}
        for s in form.get("skills") or []
        if s.get("label") and s.get("details")
    ]
    if skill_entries:
        sections["skills"] = skill_entries

    publication_entries = [
        _build_publication_entry(p)
        for p in form.get("publications") or []
        if p.get("title") and p.get("authors")
    ]
    if publication_entries:
        sections["publications"] = publication_entries

    if sections:
        cv["sections"] = sections

    cv = {k: v for k, v in cv.items() if v not in (None, "", [])}

    return {
        "cv": cv,
        "locale": {
            "language": "english",
            "present": "Present",
        },
        "design": {
            "theme": "classic",
            "colors": {
                "body": "rgb(0, 0, 0)",
                "name": "rgb(0, 0, 0)",
                "headline": "rgb(0, 0, 0)",
                "connections": "rgb(0, 0, 0)",
                "section_titles": "rgb(0, 0, 0)",
                "links": "rgb(0, 0, 0)",
                "footer": "rgb(0, 0, 0)",
                "top_note": "rgb(0, 0, 0)",
            },
            "typography": {
                "font_size": {
                    "name": "22pt",
                },
            },
            "page": {
                "show_footer": False,
                "show_top_note": False,
            },
            "sections": {
                "show_time_spans_in": [],
            },
        },
    }


def _build_education_entry(e: dict) -> dict:
    entry = {
        "institution": e["institution"].strip(),
        "area": _clean(e.get("area")),
        "degree": _clean(e.get("degree")),
        "location": _clean(e.get("location")),
    }
    _add_dates(entry, e)
    entry["highlights"] = _clean_highlights(e.get("highlights"))
    return _drop_empty(entry)


def _build_experience_entry(e: dict) -> dict:
    entry = {
        "company": e["company"].strip(),
        "position": _clean(e.get("position")),
        "location": _clean(e.get("location")),
    }
    _add_dates(entry, e)
    entry["highlights"] = _clean_highlights(e.get("highlights"))
    return _drop_empty(entry)


def _build_publication_entry(p: dict) -> dict:
    authors = [a.strip() for a in (p.get("authors") or "").split(",") if a.strip()]
    entry = {
        "title": p["title"].strip(),
        "authors": authors,
        "journal": _clean(p.get("journal")),
        "date": _clean(p.get("date")),
        "url": _clean(p.get("url")),
    }
    return _drop_empty(entry)


def _build_project_entry(e: dict) -> dict:
    entry = {
        "name": e["name"].strip(),
        "summary": _clean(e.get("summary")),
    }
    _add_dates(entry, e)
    entry["highlights"] = _clean_highlights(e.get("highlights"))
    return _drop_empty(entry)


def _add_dates(entry: dict, e: dict) -> None:
    start = _clean(e.get("start_date"))
    end = "present" if e.get("current") else _clean(e.get("end_date"))
    if start:
        entry["start_date"] = start
    if end:
        entry["end_date"] = end


def _clean_highlights(highlights) -> list:
    return [h.strip() for h in (highlights or []) if h and h.strip()]


def _clean(value):
    if value is None:
        return None
    value = value.strip()
    return value or None


def _drop_empty(entry: dict) -> dict:
    return {k: v for k, v in entry.items() if v not in (None, "", [])}
