## SOS 

```docker stop $(docker ps -aq)```

```bash -i <(curl -fsSL https://fiveonefour.com/install.sh) moose, aurora```

Ensure you have followed the instructions adding moose to your path or start a new terminal

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

moose dev

In another terminal run:

moose workflow run generate_data


Configure Aurora:

aurora setup --mcp cursor-project
aurora setup --mcp claude-desktop


Running Streamlit:

In another terminal:

streamlit run app/streamlit_app.py