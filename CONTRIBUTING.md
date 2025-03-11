# Contributing to Universal Integration Protocol

Thank you for considering contributing to UIP! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Licensing and Contributor Agreement

### Licensing

The Universal Integration Protocol is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0) for non-commercial use. For commercial use, a separate license is required.

### Contributor License Agreement (CLA)

We require all contributors to sign a Contributor License Agreement (CLA) before we can accept their contributions. The CLA is designed to protect both the project and its contributors by:

1. Ensuring that all contributions are properly licensed
2. Allowing the project to use contributions in both open-source and commercial contexts
3. Protecting the project's ability to offer dual licensing options

The CLA will be provided when you submit your first pull request. By signing the CLA, you're not giving up your copyright, but you are granting us the rights to use your contributions.

## How Can I Contribute?

### Reporting Bugs

Bugs are tracked as GitHub issues. Before creating a bug report, please check the existing issues to see if the problem has already been reported.

When creating a bug report, include as many details as possible:

- Use a clear and descriptive title
- Describe the steps to reproduce the issue
- Provide specific examples
- Describe the behavior you observed and why it's a problem
- Include screenshots or screen recordings if applicable
- Include details about your environment (OS, language version, etc.)

### Suggesting Enhancements

Enhancement suggestions are also tracked as GitHub issues. When creating an enhancement suggestion:

- Use a clear and descriptive title
- Provide a detailed description of the suggested enhancement
- Explain why this enhancement would be useful
- Include examples of how it would be used
- Consider including mock-ups or diagrams

### Contributing Code

#### Development Setup

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/uip.git`
3. Create a branch for your feature or fix: `git checkout -b feature/your-feature-name`
4. Install development dependencies for the relevant implementation:

   **Python:**
   ```bash
   cd implementations/python
   pip install -e ".[dev]"
   ```

   **TypeScript:**
   ```bash
   cd implementations/typescript
   npm install
   ```

#### Making Changes

1. Follow the coding style of the project
2. Write or update tests for your changes
3. Ensure all tests pass
4. Update documentation as needed
5. Verify your changes with the conformance test suite

#### Pull Request Process

1. Update the CHANGELOG.md with details of your changes
2. Ensure any install or build dependencies are removed before the PR
3. Update the README.md if needed
4. The PR should target the `develop` branch
5. Include a clear description of the changes
6. Link any related issues with "Fixes #issue_number" or "Relates to #issue_number"
7. Be prepared to sign the CLA if this is your first contribution

## Style Guides

### Git Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests after the first line
- Consider starting the commit message with an applicable emoji:
  - ✨ `:sparkles:` for new features
  - 🐛 `:bug:` for bug fixes
  - 📚 `:books:` for documentation changes
  - ♻️ `:recycle:` for refactoring code
  - 🧪 `:test_tube:` for adding tests
  - ⚡️ `:zap:` for performance improvements

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints for all function definitions
- Use docstrings that follow [Google's Python Style Guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- Run `flake8` and `mypy` before submitting

### TypeScript Style Guide

- Follow the [TypeScript Style Guide](https://github.com/basarat/typescript-book/blob/master/docs/styleguide/styleguide.md)
- Use ES6 features when appropriate
- Use async/await instead of Promise chains
- Run ESLint before submitting

### Documentation Style Guide

- Use Markdown for all documentation
- Use clear, concise language
- Include code examples when relevant
- Follow a logical structure with appropriate headings

## Code Review Process

The project maintainers will review all pull requests. During the review, maintainers may ask for changes to be made before a PR can be merged, either using suggested changes or pull request comments.

## Core Development Principles

1. **Cross-Language Compatibility**: All changes must maintain compatibility across supported languages
2. **Performance Sensitivity**: Be mindful of performance overhead in implementation
3. **Backward Compatibility**: Avoid breaking changes to existing APIs
4. **Security First**: Consider security implications of all changes
5. **Comprehensive Testing**: All features must have thorough tests

## Getting Help

If you need help with your contribution, feel free to:

- Join our [Discord community](https://discord.gg/uip-community)
- Open a "Question" issue on GitHub
- Contact the project maintainers directly at contributors@universalintegrationprotocol.org

Thank you for contributing to Universal Integration Protocol!
