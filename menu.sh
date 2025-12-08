#!/bin/bash
# Copyright cc 2025 thian


# setup color
red='\033[0;31m'
green='\e[0;32m'
white='\033[0m'
yellow='\033[0;33m'
cyan='\033[0;36m'
blue='\033[0;34m'
reset='\e[0m'

OUTPUT_DIR="output"


function download_model () {
    echo -e "${green}PLEASE SELECT A MODEL TO DOWNLOAD:${reset}"
    #MODEEL "tiny,tiny.en,tiny-q5_1,tiny.en-q5_1,tiny-q8_0,base,base.en,base-q5_1,base.en-q5_1,base-q8_0,small,small.en,small.en-tdrz,small-q5_1,small.en-q5_1,small-q8_0,medium,medium.en,medium-q5_0,medium.en-q5_0,medium-q8_0,large-v1,large-v2,large-v2-q5_0,large-v2-q8_0,large-v3,large-v3-q5_0,large-v3-turbo,large-v3-turbo-q5_0,large-v3-turbo-q8_0"
    echo -e "${cyan}1.tyni${reset}"
    echo -e "${cyan}2.tiny.en${reset}"
    echo -e "${cyan}3.tiny-q5_1${reset}"
    echo -e "${cyan}4.tiny.en-q5_1${reset}"
    echo -e "${cyan}5.tiny-q8_0${reset}"
    echo -e "${cyan}6.base${reset}"
    echo -e "${cyan}7.base.en${reset}"
    echo -e "${cyan}8.base-q5_1${reset}"
    echo -e "${cyan}9.base.en-q5_1${reset}"
    echo -e "${cyan}10.base-q8_0${reset}"
    echo -e "${cyan}11.small${reset}"
    echo -e "${cyan}12.small.en${reset}"
    echo -e "${cyan}13.small.en-tdrz${reset}"
    echo -e "${cyan}14.small-q5_1${reset}"
    echo -e "${cyan}15.small.en-q5_1${reset}"
    echo -e "${cyan}16.small-q8_0${reset}"
    echo -e "${cyan}17.medium${reset}"
    echo -e "${cyan}18.medium.en${reset}"
    echo -e "${cyan}19.medium-q5_0${reset}"
    echo -e "${cyan}20.medium.en-q5_0${reset}"
    echo -e "${cyan}21.medium-q8_0${reset}"
    echo -e "${cyan}22.large-v1${reset}"
    echo -e "${cyan}23.large-v2${reset}"
    echo -e "${cyan}24.large-v2-q5_0${reset}"
    echo -e "${cyan}25.large-v2-q8_0${reset}"
    echo -e "${cyan}26.large-v3${reset}"
    echo -e "${cyan}27.large-v3-q5_0${reset}"
    echo -e "${cyan}28.large-v3-turbo${reset}"
    echo -e "${cyan}29.large-v3-turbo-q5_0${reset}"
    echo -e "${cyan}30.large-v3-turbo-q8_0${reset}"
    echo -e "${yellow}Enter the number model name to download:${reset}"
    read model_number
    #example download base.en sh ./models/download-ggml-model.sh base.en
    case $model_number in
        1) model_name="tiny" ;;
        2) model_name="tiny.en" ;;
        3) model_name="tiny-q5_1" ;;
        4) model_name="tiny.en-q5_1" ;;
        5) model_name="tiny-q8_0" ;;
        6) model_name="base" ;;
        7) model_name="base.en" ;;
        8) model_name="base-q5_1" ;;
        9) model_name="base.en-q5_1" ;;
        10) model_name="base-q8_0" ;;
        11) model_name="small" ;;
        12) model_name="small.en" ;;
        13) model_name="small.en-tdrz" ;;
        14) model_name="small-q5_1" ;;
        15) model_name="small.en-q5_1" ;;
        16) model_name="small-q8_0" ;;
        17) model_name="medium" ;;
        18) model_name="medium.en" ;;
        19) model_name="medium-q5_0" ;;
        20) model_name="medium.en-q5_0" ;;
        21) model_name="medium-q8_0" ;;
        22) model_name="large-v1" ;;
        23) model_name="large-v2" ;;
        24) model_name="large-v2-q5_0" ;;
        25) model_name="large-v2-q8_0" ;;
        26) model_name="large-v3" ;;
        27) model_name="large-v3-q5_0" ;;
        28) model_name="large-v3-turbo" ;;
        29) model_name="large-v3-turbo-q5_0" ;;
        30) model_name="large-v3-turbo-q8_0" ;;
        *) echo -e "${red}Invalid selection. Exiting.${reset}" ; exit 1 ;;
    esac
    echo -e "${green}You have selected model: ${model_name}${reset}"
    # Call the download script with the selected model name
    ./models/download-ggml-model.sh "$model_name"

}

function transcript_menu () {
    echo -e "${green} please select an model to transcribe with:${reset}"
    #read list model from models/*.bin
    echo -e "${yellow}Available models:${reset}"
    ls models/*.bin | nl -w2 -s'. '
    echo -e "${yellow}Enter the number of the model to use:${reset}"
    read model_number
    #./build/bin/whisper-cli -m models/selected_model.bin -f file.mp3/wav -l (languange en/id) -osrt
    selected_model=$(ls models/*.bin | sed -n "${model_number}p")
    if [ -z "$selected_model" ]; then
        echo -e "${red}Invalid selection. Exiting.${reset}"
        exit 1
    fi
    echo -e "${green}You have selected model: ${selected_model}${reset}"
    echo -e "${yellow}Enter the path to the audio file to transcribe:${reset}"
    read audio_file
    echo -e "${yellow}Enter the language code (e.g., en for English, id for Indonesian) or leave blank for auto-detect:${reset}"
    read language_code
    if [ -z "$language_code" ]; then
        ./build/bin/whisper-cli -m "$selected_model" -f "$audio_file" -osrt 
    else
        ./build/bin/whisper-cli -m "$selected_model" -f "$audio_file" -l "$language_code" -osrt
    fi


}

function read_user(){
    echo -e "${green}PLEASE SELECT AN OPTION:${reset}"
    echo -e "${cyan}1.Download Model${reset}"
    echo -e "${cyan}2.Transcribe Audio File${reset}"
    echo -e "${yellow}Enter your choice (1 or 2):${reset}"
    read user_choice
    case $user_choice in
        1) download_model ;;
        2) transcript_menu ;;
        *) echo -e "${red}Invalid selection. Exiting.${reset}" ; exit 1 ;;
    esac
}   
read_user
