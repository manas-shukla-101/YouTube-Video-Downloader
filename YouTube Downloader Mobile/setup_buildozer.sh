#!/bin/bash

# Update package list
sudo apt update

# Install Python and required packages
sudo apt install -y python3 python3-pip

# Install required packages for Buildozer
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev

# Install Buildozer
pip3 install --user buildozer

# Install Android build tools
sudo apt install -y automake

# Create necessary directories
mkdir -p ~/.buildozer/android/platform/
mkdir -p ~/.android

# Accept Android licenses
yes | sudo ~/.buildozer/android/platform/android-sdk/tools/bin/sdkmanager --licenses