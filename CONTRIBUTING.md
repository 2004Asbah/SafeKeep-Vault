# Contributing to Safekeep NGO Vault

First off, thank you for considering contributing to Safekeep NGO Vault! It's people like you that make this project better for NGOs worldwide.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title**
* **Describe the exact steps to reproduce the problem**
* **Provide specific examples**
* **Describe the behavior you observed and what you expected**
* **Include screenshots if relevant**
* **Include your environment details** (OS, Python version, Docker version)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* **Use a clear and descriptive title**
* **Provide a detailed description of the suggested enhancement**
* **Explain why this enhancement would be useful**
* **List any similar features in other applications**

### Pull Requests

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. Ensure the test suite passes
4. Make sure your code follows the existing style
5. Write a clear commit message

## Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/safekeep-vault.git
cd safekeep-vault

# Create a branch
git checkout -b feature/your-feature-name

# Set up development environment
docker-compose up

# Make your changes and test
pytest

# Commit and push
git add .
git commit -m "Add: your feature description"
git push origin feature/your-feature-name
```

## Coding Standards

### Python Code Style
- Follow PEP 8
- Use type hints where possible
- Write docstrings for functions and classes
- Keep functions focused and small

### Commit Messages
- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters
- Reference issues and pull requests

### Testing
- Write unit tests for new features
- Ensure all tests pass before submitting PR
- Aim for >80% code coverage

## Project Structure

- `backend/` - FastAPI backend code
- `frontendd/` - Streamlit frontend code
- `terraform/` - Infrastructure as Code
- `tests/` - Test suite
- `docs/` - Documentation

## Questions?

Feel free to open an issue with your question or reach out to the maintainers.

Thank you for contributing! 🎉
