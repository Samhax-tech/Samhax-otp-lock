# OTP Lock Script

This repository contains a Node.js script for an OTP lock mechanism. This document provides instructions for setting up and running the script on Kali Linux and Termux.

## Prerequisites

Before running the script, ensure you have Node.js and npm installed on your system.

### Kali Linux

To install Node.js and npm on Kali Linux, open your terminal and run the following commands:

```bash
sudo apt update
sudo apt install nodejs npm
```

### Termux

To install Node.js and npm on Termux, open your Termux application and run the following commands:

```bash
pkg update
pkg install nodejs npm
```

## Setup

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/Samhax-tech/Samhax-otp-lock.git
    cd Samhax-otp-lock
    ```

2.  **Install Node.js dependencies:**

    Navigate to the `Samhax-otp-lock` directory (if you are not already there) and install the required npm packages:

    ```bash
npm install
    ```

## Running the Script

To run the script, navigate to the `Samhax-otp-lock` directory and execute the `index.js` file using Node.js.

### Running Persistently

To keep the script running even if you close your terminal session, you can use `nohup` or `screen`/`tmux`.

#### Using `nohup` (Recommended for simple persistence)

`nohup` allows a command to continue running after you log out from a shell. The output will be redirected to `nohup.out`.

```bash
nohup node index.js &
```

To stop the script, you will need to find its process ID (PID) and kill it:

```bash
ps aux | grep index.js
kill <PID>
```

#### Using `screen` or `tmux` (Recommended for managing multiple persistent sessions)

`screen` and `tmux` are terminal multiplexers that allow you to create and manage multiple terminal sessions, detach from them, and reattach later.

**Install `screen` (if not already installed):**

*   **Kali Linux:** `sudo apt install screen`
*   **Termux:** `pkg install screen`

**Install `tmux` (if not already installed):**

*   **Kali Linux:** `sudo apt install tmux`
*   **Termux:** `pkg install tmux`

**To start a new session and run the script:**

```bash
screen -S otplock # or tmux new -s otplock
node index.js
```

**To detach from the session (leave it running in the background):**

*   **`screen`:** Press `Ctrl+A` then `D`
*   **`tmux`:** Press `Ctrl+B` then `D`

**To reattach to the session:**

```bash
screen -r otplock # or tmux attach -t otplock
```

## Code Structure

*   `index.js`: The main script logic.
*   `package.json`: Lists Node.js dependencies.
*   `files/numbers.json`: Stores phone numbers.

## Disclaimer

This tool is provided for educational and ethical purposes only. Misuse of this tool for illegal activities is strictly prohibited. The developer is not responsible for any misuse or damage caused by this tool.




