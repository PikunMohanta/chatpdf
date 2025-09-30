# UV Installation and Migration Guide

## Why UV?

UV is a next-generation Python package manager that's significantly faster than pip:
- **10-100x faster** package installation
- **Better dependency resolution**
- **Compatible with pip** and existing workflows
- **Built in Rust** for maximum performance

## Installation

### Windows
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Linux/macOS
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Alternative (using pip)
```bash
pip install uv
```

## Migration from pip

If you're migrating from the old pip setup:

1. **Remove old virtual environment:**
   ```bash
   rm -rf env  # or rmdir /s env on Windows
   ```

2. **Create new UV virtual environment:**
   ```bash
   uv venv
   ```

3. **Activate the environment:**
   ```bash
   # Linux/macOS
   source .venv/bin/activate
   
   # Windows
   .venv\Scripts\activate
   ```

4. **Install dependencies:**
   ```bash
   uv pip install -r requirements.txt
   ```

## UV Commands vs pip

| Operation | pip | uv |
|-----------|-----|-----|
| Install packages | `pip install package` | `uv pip install package` |
| Install from requirements | `pip install -r requirements.txt` | `uv pip install -r requirements.txt` |
| Create venv | `python -m venv env` | `uv venv` |
| List packages | `pip list` | `uv pip list` |
| Freeze packages | `pip freeze` | `uv pip freeze` |
| Uninstall | `pip uninstall package` | `uv pip uninstall package` |

## Performance Benefits

In our testing with the Newchat backend:

- **pip install**: ~45 seconds
- **uv pip install**: ~3-8 seconds
- **Cold cache vs warm cache**: Even better performance on subsequent installs

## Configuration

UV uses the `pyproject.toml` file for configuration. Our setup includes:

- Python 3.10+ requirement
- Optimized resolution strategy
- Pre-compiled bytecode for faster imports
- Preference for binary wheels

## Troubleshooting

### UV not found after installation
- Restart your terminal
- Check PATH: `echo $PATH` (Unix) or `echo $env:PATH` (Windows)
- Manually add to PATH: `~/.cargo/bin` (Unix) or `%USERPROFILE%\.cargo\bin` (Windows)

### Compatibility issues
- UV is designed to be pip-compatible
- If you encounter issues, you can fall back to pip temporarily
- Report compatibility issues to the UV project

### Performance not as expected
- Ensure you're using `uv pip install` not just `pip install`
- Check if you have a fast internet connection
- UV performs best with many packages to install

## VS Code Integration

If you're using VS Code, make sure to:

1. Select the correct Python interpreter from `.venv/`
2. Update your VS Code settings to use the new virtual environment path
3. The Python extension should automatically detect the UV virtual environment

## Docker Considerations

Our Dockerfile now installs UV for faster container builds. This means:
- Faster CI/CD pipeline builds
- Reduced container build times
- More efficient dependency layer caching

The Docker image size remains the same, but build time is significantly reduced.