# Universal Integration Protocol - Project Structure

This document explains the organization of the UIP repository to help contributors navigate and understand the codebase.

## Directory Structure

```
uip/
├── .github/                      # GitHub-specific files
│   ├── ISSUE_TEMPLATE/           # Templates for different issue types
│   └── workflows/                # CI/CD workflows
├── docs/                         # Documentation
│   ├── architecture/             # Architecture specifications
│   ├── guides/                   # User and developer guides
│   ├── specifications/           # Protocol specifications
│   └── api/                      # API documentation
├── examples/                     # Example implementations
│   ├── python/                   # Python examples
│   ├── javascript/               # JavaScript examples
│   └── java/                     # Java examples
├── implementations/              # Reference implementations
│   ├── python/                   # Python UCB implementation
│   ├── typescript/               # TypeScript UCB implementation
│   └── java/                     # Java UCB implementation (future)
├── tests/                        # Test framework and test cases
│   ├── conformance/              # Conformance tests
│   ├── performance/              # Performance benchmarks
│   └── security/                 # Security tests
├── tools/                        # Development and utility tools
│   ├── schema-validator/         # USS schema validation tool
│   └── code-generator/           # Code generation utilities
├── .gitignore                    # Git ignore file
├── CODE_OF_CONDUCT.md            # Code of conduct
├── CONTRIBUTING.md               # Contribution guidelines
├── LICENSE                       # Open source license (MIT/Apache 2.0)
├── README.md                     # Project overview and getting started
└── ROADMAP.md                    # Project roadmap
```

## Key Components

### Documentation (`docs/`)

Contains all protocol specifications, architecture documentation, user guides, and API references:

- `architecture/`: Technical architecture and design documents
- `guides/`: User and developer guides, including implementation instructions
- `specifications/`: Formal protocol specifications
- `api/`: API reference documentation

### Implementations (`implementations/`)

Reference implementations of the Universal Connector Block (UCB) in different programming languages:

- `python/`: Python implementation with standard package structure
- `typescript/`: TypeScript/JavaScript implementation
- `java/`: Java implementation (planned)

Each implementation follows the standard package structure for its respective language ecosystem.

### Examples (`examples/`)

Example applications that demonstrate UIP usage in different scenarios:

- Basic examples showing UCB initialization and usage
- Integration examples between different languages
- Complete applications that implement UIP

### Tests (`tests/`)

Contains the testing framework and test suites:

- `conformance/`: Tests to verify protocol compliance
- `performance/`: Benchmarks and performance tests
- `security/`: Security testing scripts and tools

### Tools (`tools/`)

Development tools and utilities to help with UIP implementation and usage:

- Schema validators for USS format
- Code generators for integration stubs
- Development utilities

## Development Workflow

The main branches are:

- `main`: The stable release branch
- `develop`: The active development branch
- Feature branches: Created from `develop` for new features

Contributors should:

1. Fork the repository
2. Create a feature branch from `develop`
3. Make changes following the guidelines in [CONTRIBUTING.md](../CONTRIBUTING.md)
4. Submit a pull request to merge into `develop`

## Build and Package Structure

Each implementation has its own build system appropriate for its language ecosystem:

- Python: `setup.py` with standard packaging structure
- TypeScript: npm package with `package.json`
- Java: Maven project with `pom.xml`

For more detailed information on building and testing each implementation, see the README files in their respective directories.
