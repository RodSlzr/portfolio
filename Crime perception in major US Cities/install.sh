PLATFORM=$(python3 -c 'import crime; print(crime.system())')

echo -e "1. Creating new virtual environment..."

python3 -m venv env 

echo -e "2. Installing requirements..."

source env/bin/activate
pip install requirements.txt

fi 
deactivate 
echo -e "Install is complete."