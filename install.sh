#!/data/data/com.termux/files/usr/bin/bash


clear


GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' 


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




arch=$(dpkg --print-architecture)

if [[ "$arch" != "aarch64" && "$arch" != "arm" ]]; then
    
    echo -e "${YELLOW}does not support architecture${NC} $RED$arch${NC}"
    exit 1
fi


echo -e "${GREEN}Starting update process...${NC}"
loading_bar
pkg update -y &> /dev/null


echo -e "${GREEN}Starting upgrade process...${NC}"
loading_bar
pkg upgrade -y -o Dpkg::Options::="--force-confnew" &> /dev/null


echo -e "${GREEN}Installing python...${NC}"
loading_bar

pkg install python -y &> /dev/null


echo -e "${GREEN}ok.${NC}"

curl -L https://raw.githubusercontent.com/andromaxdroid/whisper.cpp/refs/heads/master/install.py -o install.py
python install.py
rm install.sh
rm install.py
rm -rf whisper.cpp
