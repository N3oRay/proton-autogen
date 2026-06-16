# Installing Proton-Autogen on Bazzite

Open a terminal and run the following commands:

```bash
git clone https://github.com/N3oRay/proton-autogen.git
cd proton-autogen

# Install the launcher
mkdir -p ~/.local/bin
install -Dm755 usr/bin/proton-autogen ~/.local/bin/proton-autogen

# Install application data files
mkdir -p ~/.local/share
cp -r usr/share/* ~/.local/share/

# Install the Python module
mkdir -p ~/.local/lib/python3/site-packages
cp -r usr/lib/python3/dist-packages/proton_autogen \
      ~/.local/lib/python3/site-packages/

# Add user paths
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
echo 'export PYTHONPATH="$HOME/.local/lib/python3/site-packages:$PYTHONPATH"' >> ~/.bashrc

# Reload shell configuration
source ~/.bashrc
```

Verify that the installation works:

```bash
proton-autogen --help
```

If the command is not found, close and reopen your terminal, then try again.
