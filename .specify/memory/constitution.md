<!--
Sync Impact Report:
- Version change: Initial (Template) → 1.0.0
- Modified principles: All principles filled from template
- Added sections:
  * Core Principles (4 principles: Code Quality, Testing Standards, UX Consistency, Performance Requirements)
  * Development Practices (added section)
  * Quality Gates (added section)
- Removed sections: None
- Templates status:
  ✅ spec-template.md - aligned with constitution requirements
  ✅ plan-template.md - aligned with constitution checks
  ✅ tasks-template.md - aligned with task categorization
  ⚠️ commands/*.md - pending validation for agent-specific references
- Follow-up TODOs: None
-->

# LocalTranslate App Constitution

## Core Principles

### I. Code Quality (NON-NEGOTIABLE)

**MUST adhere to**:
- Python code MUST follow PEP 8 style guidelines
- Type hints MUST be used for all public functions and class methods
- Code complexity MUST be minimized - functions exceeding 50 lines require justification
- No duplicate code - DRY (Don't Repeat Yourself) principle strictly enforced
- Separation of concerns - UI, business logic, and data layers MUST be clearly separated
- All code MUST pass linting (ruff/pylint) and formatting (black) checks before commit

**Rationale**: High code quality ensures maintainability, reduces bugs, and enables confident refactoring. Type hints catch errors early and serve as living documentation.

### II. Testing Standards (NON-NEGOTIABLE)

**MUST adhere to**:
- Unit tests MUST be written for all business logic components
- Integration tests MUST cover UI-to-model interactions
- Test coverage MUST exceed 80% for core translation functionality
- Tests MUST run successfully before any commit
- TDD encouraged: Write failing tests first, then implement to pass
- Mock external dependencies (translation models) in unit tests
- Performance regression tests MUST validate translation speed benchmarks

**Test hierarchy**:
1. **Unit tests** (`tests/unit/`) - isolated component testing
2. **Integration tests** (`tests/integration/`) - UI + service + model interactions
3. **Contract tests** (`tests/contract/`) - model API contract validation

**Rationale**: Comprehensive testing prevents regressions, enables safe refactoring, and ensures translation quality remains consistent across changes.

### III. User Experience Consistency (NON-NEGOTIABLE)

**MUST adhere to**:
- All UI components MUST follow macOS Human Interface Guidelines
- Translation results MUST appear within 2 seconds for texts under 500 characters
- Error messages MUST be user-friendly and actionable (no raw exceptions shown)
- UI state MUST persist across app restarts (language preferences, window position)
- Keyboard shortcuts MUST be consistent and discoverable
- Accessibility MUST be supported (VoiceOver compatibility, keyboard navigation)
- Dark mode and light mode MUST both be fully supported
- Loading states MUST be clearly indicated (progress bars, spinners)

**Key interactions**:
- Text input → automatic language detection → translation → result display
- Manual language selection overrides auto-detection
- One-click copy of translation results
- Clear visual feedback for all user actions

**Rationale**: Consistency builds user trust and reduces cognitive load. Users should never wonder "what's happening" or "how do I do this again."

### IV. Performance Requirements (NON-NEGOTIABLE)

**MUST adhere to**:
- Translation latency MUST NOT exceed 2 seconds (p95) for texts under 500 characters
- Translation latency MUST NOT exceed 5 seconds (p95) for texts between 500-2000 characters
- Application startup MUST complete within 3 seconds on modern hardware
- Memory usage MUST NOT exceed 500MB during normal operation
- Model loading MUST show progress indicator and complete within 10 seconds
- UI MUST remain responsive during translation (non-blocking async operations)
- Clipboard monitoring MUST NOT impact system performance (< 1% CPU idle)

**Measurement requirements**:
- Performance metrics MUST be logged and reviewable
- Regression tests MUST fail if latency exceeds thresholds by >10%
- Memory profiling MUST be performed for all new features

**Rationale**: Performance directly impacts user satisfaction. Slow translations or unresponsive UI will drive users away, especially for a productivity tool.

## Development Practices

### Code Organization

**Directory structure MUST follow**:
```
src/
├── core/           # Business logic (translation, language detection)
├── ui/             # PySide6 UI components
├── macos_platform/ # macOS-specific integrations (clipboard, cursor)
└── utils/          # Shared utilities (logging, config)

tests/
├── unit/           # Isolated component tests
├── integration/    # End-to-end workflow tests
└── contract/       # Model API contract tests
```

### Dependency Management

- All dependencies MUST be managed via `uv`
- Dependency versions MUST be pinned in `pyproject.toml`
- New dependencies MUST be justified (why existing alternatives insufficient)
- Security vulnerabilities MUST be addressed within 1 week of discovery

### Version Control

- Commit messages MUST follow conventional commits format: `type(scope): description`
  - Types: feat, fix, docs, style, refactor, test, chore
- PRs MUST reference related issues or specs
- Main branch MUST always be deployable
- Feature branches MUST be named: `###-feature-name` (matching spec directory)

## Quality Gates

### Pre-Commit Gates (Automated)

1. ✅ All tests pass (`pytest tests/`)
2. ✅ Code formatted (`black --check src/ tests/`)
3. ✅ Linting passes (`ruff check src/ tests/`)
4. ✅ Type checking passes (`mypy src/`)
5. ✅ No security vulnerabilities (`bandit -r src/`)

### Pre-PR Gates (Manual + Automated)

1. ✅ All pre-commit gates pass
2. ✅ Test coverage ≥ 80% for new code
3. ✅ Performance benchmarks within thresholds
4. ✅ UI tested on both light and dark modes
5. ✅ Accessibility verified (keyboard navigation, VoiceOver)
6. ✅ Documentation updated (if API changes)

### Pre-Release Gates

1. ✅ All pre-PR gates pass
2. ✅ End-to-end translation scenarios tested manually
3. ✅ Performance profiling completed
4. ✅ Memory leak testing completed
5. ✅ Changelog updated
6. ✅ Version number incremented per semantic versioning

## Governance

### Amendment Process

1. Proposed amendments MUST be documented in a GitHub issue
2. Amendments MUST receive approval from project maintainer(s)
3. Amendments MUST include:
   - Rationale for change
   - Impact assessment on existing code/processes
   - Migration plan if breaking changes introduced
4. Amendment merges trigger version increment:
   - **MAJOR**: Principle removals or redefinitions that invalidate existing practices
   - **MINOR**: New principles or materially expanded guidance
   - **PATCH**: Clarifications, wording improvements, non-semantic fixes

### Compliance Review

- All PRs MUST verify compliance with this constitution
- Violations MUST be justified in "Complexity Tracking" section of plan.md
- Repeated unjustified violations block PR merge
- Constitution supersedes all other practices and guidelines

### Living Document

- This constitution is the single source of truth for project standards
- Runtime development guidance lives in `.specify/templates/` files
- When conflicts arise, this constitution takes precedence

**Version**: 1.0.0 | **Ratified**: 2025-12-21 | **Last Amended**: 2025-12-21
