# GPU server environment. Usage: source ~/chlorosis/env.sh
# All tools, caches, and the venv for this project live under ~/chlorosis.
# Remove everything: rm -rf ~/chlorosis
export CHLOROSIS_HOME="$HOME/chlorosis"
export PATH="$CHLOROSIS_HOME/.tools/bin:$PATH"
export UV_CACHE_DIR="$CHLOROSIS_HOME/.tools/uv-cache"
export UV_PYTHON_INSTALL_DIR="$CHLOROSIS_HOME/.tools/python"
export PIP_CACHE_DIR="$CHLOROSIS_HOME/.tools/pip-cache"
export HF_HOME="$CHLOROSIS_HOME/.tools/hf-cache"
export TORCH_HOME="$CHLOROSIS_HOME/.tools/torch-cache"
if [ -f "$CHLOROSIS_HOME/.venv/bin/activate" ]; then . "$CHLOROSIS_HOME/.venv/bin/activate"; fi
