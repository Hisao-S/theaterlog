import os
import sys
import streamlit.web.cli as stcli

# プログラムがある場所をシステムに教える
sys.path.insert(0, os.path.dirname(__file__))

# PythonAnywhereがStreamlitを起動できるように仕込む
if __name__ == "__main__":
    sys.argv = ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
    stcli.main()