# Contributing to LLM API Demonstrations

Thank you for your interest in contributing to this project! We welcome contributions from the community.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Pull Request Process](#pull-request-process)
- [Reporting Issues](#reporting-issues)

---

## 🤝 Code of Conduct

This project adheres to a code of conduct that fosters an open and welcoming environment. Please be respectful and professional in all interactions.

---

## 💡 How to Contribute

### Types of Contributions

1. **Bug Reports**: Found a bug? Please report it!
2. **Feature Requests**: Have an idea? We'd love to hear it!
3. **Code Contributions**: Fix bugs or add features
4. **Documentation**: Improve README, add examples, fix typos
5. **Testing**: Add test cases, improve coverage

---

## 🛠️ Development Setup

### Prerequisites

- Python 3.11+
- Git
- API keys for testing (OpenAI, Anthropic, or Gemini)

### Setup Steps

```bash
# 1. Fork the repository on GitHub

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/API_Demo.git
cd API_Demo

# 3. Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Set up API keys
cp .env.example .env
# Edit .env with your API keys

# 6. Create a feature branch
git checkout -b feature/your-feature-name
```

---

## 📝 Coding Standards

### Python Style Guide

Follow [PEP 8](https://pep8.org/) with these specifics:

- **Indentation**: 4 spaces (no tabs)
- **Line length**: 100 characters max
- **Imports**: Grouped (stdlib, third-party, local)
- **Docstrings**: Google style for functions/classes
- **Type hints**: Use where applicable

### Example

```python
def extract_metadata(text: str, schema: dict) -> dict:
    """
    Extract structured metadata from text using JSON schema.
    
    Args:
        text: Input text to process
        schema: JSON schema for validation
        
    Returns:
        Validated dictionary matching schema
        
    Raises:
        ValidationError: If output doesn't match schema
    """
    # Implementation...
    pass
```

### Documentation

- **Comments**: Explain *why*, not *what*
- **README**: Update if adding features
- **Examples**: Include usage examples
- **Docstrings**: All public functions/classes

### Testing

- Test your changes before submitting
- Add test cases for new features
- Ensure existing tests pass

```bash
# Run demo tests
cd 01_structured_extract && python run_all.py
cd ../02_tool_calling && python run_examples.py
cd ../03_MARL_ViZ_Demo && python src/marl_viz.py --steps 50
```

---

## 🔄 Pull Request Process

### Before Submitting

1. ✅ Test all changes thoroughly
2. ✅ Update documentation
3. ✅ Follow coding standards
4. ✅ Add examples if applicable
5. ✅ Commit with clear messages

### PR Guidelines

1. **Title**: Clear, concise description
   - Good: `Add LLM-based assignment for MARL demo`
   - Bad: `Update files`

2. **Description**: Include:
   - What changes were made
   - Why they were needed
   - How to test
   - Related issues (if any)

3. **Scope**: Keep PRs focused
   - One feature/fix per PR
   - Avoid mixing unrelated changes

### Review Process

1. Maintainers will review your PR
2. Address feedback and update as needed
3. Once approved, PR will be merged
4. Your contribution will be credited

### Commit Messages

Follow conventional commits:

```
feat: Add support for GPT-4o in structured extraction
fix: Handle rate limiting in Gemini API calls
docs: Update installation instructions for macOS
refactor: Simplify reward calculation in MARL viz
test: Add test cases for tool calling demo
```

---

## 🐛 Reporting Issues

### Bug Reports

Include:
- **Description**: Clear explanation of the bug
- **Steps to Reproduce**: Minimal example
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Environment**:
  - Python version
  - OS (Windows/macOS/Linux)
  - Relevant library versions
- **Error Messages**: Full traceback if applicable

### Feature Requests

Include:
- **Use Case**: Why is this feature needed?
- **Proposed Solution**: How should it work?
- **Alternatives**: Other approaches considered
- **Examples**: Similar features elsewhere

---

## 📚 Additional Resources

- [Python Style Guide (PEP 8)](https://pep8.org/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [How to Write a Git Commit Message](https://chris.beams.io/posts/git-commit/)

---

## 🎯 Priority Areas

We especially welcome contributions in:

1. **New Demos**: Additional LLM API use cases
2. **Provider Support**: More LLM providers (e.g., Cohere, Mistral)
3. **Documentation**: Tutorials, guides, examples
4. **Testing**: Unit tests, integration tests
5. **Performance**: Optimization, caching, batching

---

## ❓ Questions?

- Open an issue for questions
- Tag with `question` label
- We'll respond as soon as possible

---

Thank you for contributing! 🎉

