PAPER_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "PaperMeta",
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "minLength": 3,
            "maxLength": 300
        },
        "authors": {
            "type": "array",
            "items": {
                "type": "string",
                "minLength": 2
            },
            "minItems": 1
        },
        "venue": {
            "type": "string",
            "enum": [
                "NeurIPS", "ICLR", "ICML",
                "ACL", "EMNLP", "NAACL",
                "CVPR", "ICCV", "ECCV",
                "AAAI", "KDD", "TheWebConf",
                "SIGIR", "SIGCOMM",
                "INFOCOM", "GLOBECOM",
                "TPDS", "TOS"
            ]
        },
        "year": {
            "type": "integer",
            "minimum": 1900,
            "maximum": 2100
        },
        "doi": {
            "anyOf": [
                {"type": "string", "pattern": "^10\\..+/.+"},
                {"type": "null"}
            ],
            "description": "Use null if DOI is missing or invalid."
        },
        "keywords": {
            "type": "array",
            "items": {
                "type": "string",
                "minLength": 2,
                "maxLength": 50,
                "pattern": "^[a-z0-9\\- ]+$"
            },
            "minItems": 3,
            "maxItems": 10
        },
        "abstract": {
            "anyOf": [
                {"type": "string", "minLength": 20},
                {"type": "null"}
            ]
        },
        "arxiv_id": {
            "anyOf": [
                {"type": "string", "pattern": "^\\d{4}\\.\\d{4,5}(v\\d+)?$"},
                {"type": "null"}
            ]
        },
        "url": {
            "anyOf": [
                {"type": "string", "minLength": 1},
                {"type": "null"}
            ]
        }
    },
    "required": ["title", "authors", "venue", "year", "doi", "keywords", "abstract", "arxiv_id", "url"],
    "additionalProperties": False
}

# System instruction for all three LLM providers
SYSTEM_INSTRUCTION = (
    "Extract paper metadata strictly according to the JSON Schema.\n"
    "Normalization rules:\n"
    "1) Venue must be one of the enum values in the schema. If the text says 'NIPS', map it to 'NeurIPS'.\n"
    "2) Authors should be a full list of strings in reading order.\n"
    "3) If DOI is missing or not starting with '10.', output null.\n"
    "4) Keywords: return 3–10 concise lowercase tokens (no punctuation).\n"
    "5) If abstract, arxiv_id, or url is missing, output null for those fields.\n"
    "Return only the JSON object that matches the schema; no extra keys."
)
