#!/bin/bash
# Скрипт установки Xray и 3X-UI на Ubuntu 20.04+

# Обновление системы
apt update

# Установка необходимых пакетов
apt install -y curl wget unzip

# Установка Xray
bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install

# Установка 3X-UI
bash <(curl -Ls https://raw.githubusercontent.com/mhsanaei/3x-ui/master/install.sh)

# Настройка фаервола
ufw allow 80
ufw allow 443
ufw allow 2096
ufw enable

# Перезапуск службы 3X-UI
systemctl restart x-ui