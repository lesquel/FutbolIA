# Contributing to GoalMind

Thank you for your interest in contributing to GoalMind! 🏆

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Commit Convention](#commit-convention)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/GoalMind.git
   cd GoalMind
   ```
3. **Add upstream** remote:
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/GoalMind.git
   ```
4. **Create a branch** for your work:
   ```bash
   git checkout -b feat/your-feature-name
   ```

## Development Setup

### Prerequisites

| Tool | Version | Installation |
|------|---------|-------------|
| Python | 3.13+ | [python.org](https://python.org) |
| uv | latest | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Node.js | 22+ | [nodejs.org](https://nodejs.org) |
| Bun | latest | `curl -fsSL https://bun.sh/install \| bash` |
| MongoDB | 7+ | [mongodb.com](https://www.mongodb.com/try/download) or Docker |
| Docker | latest | [docker.com](https://docker.com) (optional) |

### Quick Setup

```bash
# Using Make (Linux/Mac)
make setup

# Using Task (Windows/Linux/Mac)
task setup

# Or manually:
cd futbolia-backend && cp .env.example .env && uv sync
cd ../futbolia-mobile && cp .env.example .env && bun install
```

### Running the Project

```bash
# Start everything
make dev

# Or individually
make dev-backend    # Backend only (port 8000)
make dev-frontend   # Frontend only (port 8081)

# With Docker
make docker-up
```

## How to Contribute

### Reporting Bugs

- Use the [Bug Report](https://github.com/ORIGINAL_OWNER/GoalMind/issues/new?template=bug_report.md) issue template
- Include steps to reproduce
- Include expected vs actual behavior
- Include screenshots if applicable

### Suggesting Features

- Use the [Feature Request](https://github.com/ORIGINAL_OWNER/GoalMind/issues/new?template=feature_request.md) issue template
- Explain the problem your feature would solve
- Describe your proposed solution

### Code Contributions

1. Check existing [issues](https://github.com/ORIGINAL_OWNER/GoalMind/issues) or create one
2. Fork & create a feature branch
3. Write your code with tests
4. Run linters and tests locally
5. Submit a Pull Request

## Coding Standards

### Python (Backend)

- **Formatter**: Ruff (`ruff format`)
- **Linter**: Ruff (`ruff check`)
- **Line length**: 100 characters
- **Type hints**: Required for function signatures
- **Docstrings**: Required for public classes and functions
- **Style**: Follow PEP 8 conventions

```bash
# Check code quality
cd futbolia-backend
uv run ruff check .
uv run ruff format --check .
```

### TypeScript (Mobile)

- **Formatter**: Prettier
- **Linter**: ESLint with Expo config
- **Style**: Single quotes, 2-space indent, trailing semicolons

```bash
# Check code quality
cd futbolia-mobile
bun run lint
bun run format:check
```

### Pre-commit Hooks

We use pre-commit to enforce standards automatically:

```bash
# Install hooks (run once after setup)
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

## Commit Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, no code change |
| `refactor` | Code restructuring |
| `perf` | Performance improvement |
| `test` | Adding or fixing tests |
| `build` | Build system or dependencies |
| `ci` | CI/CD configuration |
| `chore` | Maintenance tasks |

### Scopes

- `backend` - Backend changes
- `mobile` - Mobile app changes
- `docker` - Docker configuration
- `ci` - CI/CD changes
- `docs` - Documentation

### Examples

```
feat(backend): add player comparison endpoint
fix(mobile): resolve navigation crash on Android
docs: update setup instructions for Windows
ci: add Python lint job to CI workflow
```

## Pull Request Process

1. **Update your branch** with the latest from `main`:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Ensure all checks pass**:
   ```bash
   make lint
   make test
   ```

3. **Fill out the PR template** completely

4. **Request review** from maintainers

5. **Address feedback** by pushing additional commits

6. Once approved, a maintainer will merge your PR

### PR Guidelines

- Keep PRs focused — one feature or fix per PR
- Write descriptive PR titles using conventional commit format
- Include screenshots/recordings for UI changes
- Link related issues using `Closes #123` or `Fixes #123`
- Ensure CI passes before requesting review

## Questions?

Feel free to [open a discussion](https://github.com/ORIGINAL_OWNER/GoalMind/discussions) or reach out to the maintainers.

---

Thank you for making GoalMind better! ⚽🤖
