# Patience Card Game

Welcome to the Patience Card Game! This is a classic card game implemented in Python using the Tkinter library for the GUI and the PIL library for image handling. The game is similar to Solitaire, where the goal is to move all cards to 4 end houses to win.

## Table of Contents

- [Patience Card Game](#patience-card-game)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
    - [Option 1: Installing from Releases](#option-1-installing-from-releases)
    - [Option 2: Installing from Source](#option-2-installing-from-source)
  - [Usage](#usage)
  - [Contributing](#contributing)
    - [Guidelines](#guidelines)
  - [Known Issues](#known-issues)
  - [License](#license)

## Installation

You can install and run the Patience Card Game in two ways: from releases or from source.

### Option 1: Installing from Releases

1. Go to the [Releases](https://github.com/depleur/patience/releases) page of the repository.
2. Download the latest release for your operating system:

   - For Windows: Download the `.exe` file
   - For macOS: Download the macOS executable
   - For Linux: Download the Linux executable

3. Running the game:
   - Windows: Simply double-click the `.exe` file to run the game.
   - macOS and Linux: Open a terminal, navigate to the directory containing the downloaded file, and run:
     ```sh
     chmod +x patience-macos && ./patience-macos
     ```
     This command makes the file executable and runs it. After the first time, you can double-click the file to run it.

### Option 2: Installing from Source

To install from source, follow these steps:

1. **Clone the repository:**

   ```sh
   git clone https://github.com/depleur/patience.git
   cd patience
   ```

2. **Set up a Python virtual environment:**

   It is highly recommended to use a virtual environment to manage dependencies. You can create and activate a virtual environment using the following commands:

   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required dependencies:**

   ```sh
   pip install -r requirements.txt
   ```

## Usage

If you installed from releases, run the game by following the instructions in the [Installing from Releases](#option-1-installing-from-releases) section.

If you installed from source, run the game by executing the following command:

```sh
python game.py
```

This will launch the Patience Card Game window.

## Contributing

We welcome contributions to improve the Patience Card Game! If you would like to contribute, please follow these steps:

1. **Fork the repository:**

   Click the "Fork" button at the top-right corner of this page to create a copy of this repository under your GitHub account.

2. **Clone your forked repository:**

   ```sh
   git clone https://github.com/your-username/patience-card-game.git
   cd patience-card-game
   ```

3. **Create a new branch for your changes:**

   ```sh
   git checkout -b my-feature-branch
   ```

4. **Make your changes and commit them:**

   ```sh
   git add .
   git commit -m "Description of your changes"
   ```

5. **Push your changes to your forked repository:**

   ```sh
   git push origin my-feature-branch
   ```

6. **Create a pull request:**

   Go to the original repository on GitHub, and you should see a prompt to create a pull request from your forked repository. Follow the instructions to submit your pull request for review.

### Guidelines

- Ensure your code follows the project's coding style and conventions.
- Write clear and concise commit messages.
- Include documentation and comments where necessary.
- Test your changes thoroughly before submitting a pull request.

## Known Issues

On macOS, Tkinter can be slower, resulting in jerkier movements.
I am aware of this [issue](https://github.com/python/cpython/issues/87677) and there is little I can do to solve it.
This may be local to macOS 14 (Sonoma), or macOS in general.

## License

This project is licensed under the GNU-GPL v3 License. See the [LICENSE](LICENSE) file for details.
