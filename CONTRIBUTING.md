# Contributing to AI Document Helper

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Getting Started

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/yourusername/simple_ai_doument_helper.git
   cd simple_ai_doument_helper
   ```

3. **Set up development environment**
   ```bash
   ./scripts/setup.sh
   ```

## Development Workflow

### Making Changes

1. **Create a new branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow the coding standards (see below)
   - Write tests for new features
   - Update documentation as needed

3. **Test your changes**
   ```bash
   ./scripts/run_tests.sh
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "Description of changes"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**

## Coding Standards

### Python (Backend)

- Follow PEP 8 style guide
- Use type hints where appropriate
- Write docstrings for functions and classes
- Maximum line length: 100 characters

**Example:**
```python
def process_document(file_path: str) -> List[Dict]:
    """
    Process a document and return chunks.
    
    Args:
        file_path: Path to the document file
        
    Returns:
        List of document chunks with metadata
    """
    # Implementation
    pass
```

### JavaScript/React (Frontend)

- Use functional components with hooks
- Follow Airbnb JavaScript Style Guide
- Use meaningful variable names
- Keep components small and focused

**Example:**
```javascript
const DocumentList = ({ documents, onDelete }) => {
  return (
    <div className="document-list">
      {documents.map(doc => (
        <DocumentItem 
          key={doc.id} 
          document={doc} 
          onDelete={onDelete} 
        />
      ))}
    </div>
  );
};
```

### Docker

- Use official base images
- Minimize layer count
- Use .dockerignore
- Don't run as root
- Use multi-stage builds where appropriate

## Testing

### Backend Tests

```bash
# Run all tests
docker-compose exec backend pytest tests/ -v

# Run specific test file
docker-compose exec backend pytest tests/test_api.py -v

# Run with coverage
docker-compose exec backend pytest tests/ --cov=. --cov-report=html
```

### Frontend Tests

```bash
cd frontend
npm test
```

### End-to-End Tests

```bash
./scripts/run_tests.sh
```

## Documentation

- Update README.md for user-facing changes
- Update ARCHITECTURE.md for architectural changes
- Add inline comments for complex logic
- Update API documentation (docstrings)

## Commit Messages

Use clear, descriptive commit messages:

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

**Examples:**
```
feat: Add support for EPUB documents
fix: Resolve chunking overlap issue
docs: Update installation instructions
test: Add tests for document processor
```

## Pull Request Guidelines

1. **Title**: Clear and descriptive
2. **Description**: Explain what and why
3. **Tests**: Include tests for new features
4. **Documentation**: Update relevant docs
5. **Breaking Changes**: Clearly mark any breaking changes

## Code Review Process

1. Automated tests must pass
2. At least one maintainer approval required
3. Address review comments
4. Keep PR scope focused

## Reporting Issues

When reporting issues, include:

1. **Description**: Clear description of the issue
2. **Steps to Reproduce**: Detailed steps
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Environment**: OS, Docker version, etc.
6. **Logs**: Relevant log output

## Feature Requests

For feature requests, include:

1. **Use Case**: Why is this needed?
2. **Proposed Solution**: How should it work?
3. **Alternatives**: Other approaches considered
4. **Additional Context**: Any other relevant info

## Development Tips

### Hot Reload

**Backend:**
```bash
# Already configured in docker-compose.yml
# Changes to Python files will auto-reload
```

**Frontend:**
```bash
# React hot reload is enabled by default
# Changes will reflect immediately
```

### Debugging

**Backend:**
```bash
# View logs
docker-compose logs -f backend

# Access container shell
docker-compose exec backend bash

# Run Python interactively
docker-compose exec backend python
```

**Frontend:**
```bash
# View logs
docker-compose logs -f frontend

# Access container shell
docker-compose exec frontend sh
```

### Database

**Qdrant:**
```bash
# Access Qdrant dashboard
open http://localhost:6333/dashboard

# View collections
curl http://localhost:6333/collections
```

## Performance Optimization

When contributing performance improvements:

1. Benchmark before and after
2. Document the improvement
3. Consider trade-offs
4. Test with realistic data

## Security

- Never commit secrets or API keys
- Use environment variables for configuration
- Validate all user input
- Follow security best practices
- Report security issues privately

## Questions?

If you have questions:

1. Check existing documentation
2. Search existing issues
3. Ask in discussions
4. Create a new issue

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Thank You!

Your contributions make this project better for everyone. Thank you for taking the time to contribute!
