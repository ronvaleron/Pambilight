#!/bin/bash

# Create pambilight.sh script
echo '#!/bin/bash' > ./pambilight.sh;
echo "cd $(pwd)" >> ./pambilight.sh;
echo '# Проверка на запущенное приложение' >> ./pambilight.sh;
echo 'ps -ef | grep "python pambilight.py" | grep -v "grep" > /dev/null 2>&1' >> ./pambilight.sh;
echo 'if [ $? -eq 0 ]; then' >> ./pambilight.sh;
echo '  # Приложение запущено, останавливаем' >> ./pambilight.sh;
echo '  echo "Остановка приложения..."' >> ./pambilight.sh;
echo '  pkill -f "pambilight.py"' >> ./pambilight.sh;
echo 'else' >> ./pambilight.sh;
echo '  # Приложение не запущено, запускаем' >> ./pambilight.sh;
echo '  echo "Запуск приложения..."' >> ./pambilight.sh;
echo '  source ./venv/bin/activate' >> ./pambilight.sh;
echo '  python pambilight.py &' >> ./pambilight.sh;
echo 'fi' >> ./pambilight.sh;

# Make executible
chmod +x $(pwd)/pambilight.sh;

# Create desktop link
binpath="/usr/bin";
appspath="/usr/share/applications";
echo "[Desktop Entry]" > $appspath/pambilight.desktop;
echo "Name=Pambilight" >> $appspath/pambilight.desktop;
echo "Exec=$binpath/pambilight %U" >> $appspath/pambilight.desktop;
echo "Terminal=false" >> $appspath/pambilight.desktop;
echo "Type=Application" >> $appspath/pambilight.desktop;
echo "Icon=$(pwd)/pambilight.png" >> $appspath/pambilight.desktop;
echo "StartupWMClass=pambilight" >> $appspath/pambilight.desktop;
echo "Comment=Analog Ambibox by Python" >> $appspath/pambilight.desktop;
echo "Categories=Graphics;" >> $appspath/pambilight.desktop;



#  Create softlink
ln -sf $(pwd)/pambilight.sh $binpath/pambilight;

# Install VENV
python3 -m venv venv;

# Activate venv
source ./venv/bin/activate;

# Install requirements
pip install -r requirements.txt;