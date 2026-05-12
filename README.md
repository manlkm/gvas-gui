## Step to run the GVAS GUI Loader
```bash
# Create virtual python environment first
python -m venv .venv

# Switch to the virtual environment
#For Windows (cmd)
.venv\Scripts\activate

#For Linux / MacOS
source .venv/Scripts/activate

# Install dependency
pip install -r requirements.txt

# Run the GUI Loader
python gvas_gui.py
```