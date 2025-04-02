#!/data/data/com.termux/files/usr/bin/bash

# Clear the screen
clear

# Colors
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Loading bar function
loading_bar() {
    local progress=0
    local total=30
    local bar=""

    while [ $progress -le $total ]; do
        bar=$(printf '=%.0s' $(seq 1 $progress))
        printf "\r${GREEN}[$bar$(printf ' %.0s' $(seq 1 $((total - progress))))] $((progress * 100 / total))%%${NC}"
        sleep 0.1
        ((progress++))
    done
    echo ""
}

# Update process
echo -e "${GREEN}Starting update process...${NC}"
loading_bar
pkg update -y &> /dev/null

# Upgrade process
echo -e "${GREEN}Starting upgrade process...${NC}"
loading_bar
pkg upgrade -y -o Dpkg::Options::="--force-confnew" &> /dev/null

# Install wget and python
echo -e "${GREEN}Installing wget and python...${NC}"
loading_bar
pkg install wget -y &> /dev/null
pkg install python -y &> /dev/null

# Finished message
echo -e "${GREEN}ok.${NC}"

curl -L https://raw.githubusercontent.com/andromaxdroid/whisper.cpp/refs/heads/master/install.py -o install.py
python install.py
rm install.sh
rm install.py
rm -rf whisper.cpp
