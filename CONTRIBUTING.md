# Contributing to EvidenceGap AI 2026

Thank you for your interest in contributing to EvidenceGap AI (Ontology-Guided Hypothesis Generation Using LLMs and Topic Modeling in mHealth Research).

## Code of Conduct

We are committed to providing a welcoming, inclusive, and harassment-free environment for all contributors.

## Development Workflow

1. Fork the repository on GitHub.
2. Clone your fork locally:
   ```bash
   git clone https://github.com/Bhuvanasri-gundu/EvidenceGap-AI.git
   cd EvidenceGap-AI
   ```
3. Create a feature branch:
   ```bash
   git checkout -b feat/your-feature-name
   ```
4. Set up the Python virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
5. Set up the React frontend:
   ```bash
   cd frontend
   npm install
   ```

## Commit Conventions

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` Introduces a new feature to the codebase
- `fix:` Patches a bug in the application
- `refactor:` Code restructuring without changing external behavior
- `docs:` Documentation additions or updates
- `test:` Adding or updating automated tests
- `chore:` Maintenance tasks, dependency updates, or configuration

## Pull Request Guidelines

1. Ensure all backend tests pass before opening a pull request:
   ```bash
   python -m pytest tests/ -v
   ```
2. Verify the frontend builds cleanly without TypeScript or Vite errors:
   ```bash
   cd frontend && npm run build
   ```
3. Keep pull requests focused on a single logical change.
4. Do not commit sensitive credentials, API keys, or large data files.
