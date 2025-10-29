apt update
apt upgrade -y
pkg install python -y
pkg install python-pip -y
pkg install git -y
git clone https://github.com/aydnn3169-sketch/AYDNQX-TOOL.git
cd AYDNQX-TOOL
pip install -r requirements.txt
python main.py
