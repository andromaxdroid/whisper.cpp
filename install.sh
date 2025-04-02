#!/data/data/com.termux/files/usr/bin/bash

# Clear the screen
clear

# Colors
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Realtime loading bar function
realtime_loading_bar() {
    local total=$1
    local progress=0
    local bar=""

    while read -r line; do
        progress=$((progress + 1))
        percent=$((progress * 100 / total))
        bar=$(printf '=%.0s' $(seq 1 $((progress * 30 / total))))
        printf "\r${GREEN}[$bar$(printf ' %.0s' $(seq 1 $((30 - progress * 30 / total))))] $percent%%${NC}"
    done
    echo ""
}

# Count available packages for update
total_update=$(pkg list-upgradable 2>/dev/null | wc -l)
if [ "$total_update" -eq 0 ]; then
    total_update=1  # Avoid division by zero if no updates are available
fi

# Update process
echo -e "${GREEN}Starting update process...${NC}"
pkg update -y | realtime_loading_bar "$total_update"

# Count available packages for upgrade
total_upgrade=$(pkg list-upgradable 2>/dev/null | wc -l)
if [ "$total_upgrade" -eq 0 ]; then
    total_upgrade=1
fi

# Upgrade process
echo -e "${GREEN}Starting upgrade process...${NC}"
pkg upgrade -y -o Dpkg::Options::="--force-confnew" | realtime_loading_bar "$total_upgrade"

# Install wget and python
echo -e "${GREEN}Installing wget and python...${NC}"
pkg install wget python -y | realtime_loading_bar 2

# Finished message
echo -e "${GREEN}Process completed.${NC}"

