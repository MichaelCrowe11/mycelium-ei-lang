# Publishing Instructions for Mycelium-EI-Lang

## 📦 PyPI Publication

### Prerequisites
1. Create PyPI account at https://pypi.org/account/register/
2. Generate API token: Account Settings → API tokens → Add API token
3. Install twine: `pip install twine`

### Publishing Steps

#### 1. Test on TestPyPI First (Recommended)
```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ mycelium-ei-lang
```

#### 2. Publish to PyPI
```bash
# Upload to PyPI
python -m twine upload dist/*

# Or with API token (more secure)
python -m twine upload dist/* --username __token__ --password <your-token>
```

#### 3. Verify Installation
```bash
pip install mycelium-ei-lang
python -m mycelium_ei --version
```

### Automated Publishing with GitHub Actions

Create `.github/workflows/publish.yml`:
```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.x'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

## 🎨 VS Code Extension Publication

### Prerequisites
1. Create Visual Studio Marketplace publisher account
2. Install vsce: `npm install -g vsce`
3. Generate Personal Access Token (PAT) from Azure DevOps

### Publishing Steps

#### 1. Create Publisher
```bash
vsce create-publisher Mycelium-EI-Lang
```

#### 2. Login with PAT
```bash
vsce login Mycelium-EI-Lang
```

#### 3. Package Extension
```bash
cd vscode-extension
npm install
vsce package
# Creates mycelium-ei-lang-0.1.0.vsix
```

#### 4. Publish to Marketplace
```bash
vsce publish

# Or publish specific version
vsce publish 0.1.0

# Or auto-increment version
vsce publish minor  # 0.1.0 -> 0.2.0
vsce publish patch  # 0.1.0 -> 0.1.1
```

#### 5. Test Installation
- Open VS Code
- Extensions → Search "Mycelium-EI-Lang"
- Click Install

### Publishing from CI/CD

Create `.github/workflows/vscode-publish.yml`:
```yaml
name: Publish VS Code Extension

on:
  push:
    tags:
      - "v*"

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-node@v3
      with:
        node-version: 16
    - name: Install dependencies
      run: |
        cd vscode-extension
        npm install
        npm install -g vsce
    - name: Publish
      env:
        VSCE_PAT: ${{ secrets.VSCE_PAT }}
      run: |
        cd vscode-extension
        vsce publish -p $VSCE_PAT
```

## 🔑 Security Best Practices

### For PyPI
1. **Never commit tokens** to repository
2. Use GitHub Secrets for CI/CD
3. Use 2FA on PyPI account
4. Scope API tokens to specific projects

### For VS Code
1. Keep PAT tokens secure
2. Rotate tokens regularly
3. Use minimal required permissions

## 📋 Pre-Publication Checklist

### PyPI Package
- [ ] Version number updated in `setup.py` and `pyproject.toml`
- [ ] README.md is complete and formatted correctly
- [ ] LICENSE file included
- [ ] All dependencies listed in requirements.txt
- [ ] Package builds without errors: `python -m build`
- [ ] Tests pass: `pytest`
- [ ] Documentation updated

### VS Code Extension
- [ ] Version updated in package.json
- [ ] README.md includes all features
- [ ] Icon image (128x128) included
- [ ] All snippets tested
- [ ] Extension compiles: `npm run compile`
- [ ] VSIX packages correctly: `vsce package`
- [ ] Marketplace listing prepared

## 🚀 Quick Commands Reference

### PyPI
```bash
# Build
python -m build

# Check distribution
twine check dist/*

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

### VS Code Extension
```bash
# Install dependencies
cd vscode-extension && npm install

# Compile TypeScript
npm run compile

# Package extension
vsce package

# Publish
vsce publish
```

## 📊 Post-Publication

### Monitor PyPI Stats
- View at: https://pypi.org/project/mycelium-ei-lang/
- Check download stats: https://pypistats.org/packages/mycelium-ei-lang

### Monitor VS Code Extension
- Marketplace: https://marketplace.visualstudio.com/items?itemName=MichaelBenjaminCrowe.mycelium-ei-lang
- Reviews and ratings
- Download count
- Issue reports

## 🆘 Troubleshooting

### PyPI Issues
- **403 Forbidden**: Check API token permissions
- **File exists**: Version already published, increment version
- **Invalid distribution**: Run `twine check dist/*`

### VS Code Issues
- **Personal Access Token expired**: Generate new PAT
- **Version exists**: Increment version in package.json
- **Compilation errors**: Run `npm run compile` to check

## 📝 Version Management

### Semantic Versioning
- **Major** (1.0.0): Breaking changes
- **Minor** (0.1.0): New features, backward compatible
- **Patch** (0.0.1): Bug fixes

### Updating Versions
```bash
# PyPI - Edit setup.py and pyproject.toml
version="0.1.1"

# VS Code - Edit package.json or use vsce
vsce publish patch
```

## 🎉 Success Indicators

### PyPI Success
- Package appears on https://pypi.org
- `pip install mycelium-ei-lang` works
- Import successful: `import mycelium_ei`

### VS Code Success
- Extension appears in marketplace
- Installation from VS Code works
- Syntax highlighting active for .myc files
- IntelliSense functioning

---

**Congratulations on publishing Mycelium-EI-Lang!** 🧬

For support: michael.benjamin.crowe@gmail.com