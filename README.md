# Patience Card Game

Welcome to the Patience Card Game! This is a classic card game implemented in Python using the Tkinter library for the GUI and the PIL library for image handling. The game is similar to Solitaire, where the goal is to move all cards to the foundation piles following specific rules.

## Table of Contents

- [Patience Card Game](#patience-card-game)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Contributing](#contributing)
    - [Guidelines](#guidelines)
  - [Known Issues](#known-issues)
  - [License](#license)

## Installation

To get started with the Patience Card Game, follow these steps:

1. **Clone the repository:**

   ```sh
   git clone https://github.com/depleur/patience.git
   cd patience-card-game
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

4. **Download card images:**

   Make sure you have a folder named `images` in the project directory containing images for all cards. The images should be named in the format `rank_of_suit.png` (e.g., `1_of_hearts.png`, `13_of_spades.png`). This comes prepackaged when you clone the repo.

## Usage

To run the game, execute the following command:

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

On MacOS, Tkinter can be a slower, resulting in jerkier movements.
I am aware of this [issue](https://github.com/python/cpython/issues/87677) and there is little I can do to solve it.
This maybe local to MacOS 14 (Sonoma), or MacOS in general.

## License

This project is licensed under the GNU-GPL v3 License. See the [LICENSE](LICENSE) file for details.
