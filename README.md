# Jarvis - AI Assistant

An intelligent AI assistant that can help you with various tasks using a collection of tools and LLM-based decision making.

## Features

- Web search and information gathering
- Weather information
- News updates
- System information and management
- File system operations
- Process management
- LLM-based natural language understanding

## Prerequisites

- Python 3.8 or higher
- OpenAI API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/jarvis.git
cd jarvis
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key to `.env`

## Launching Jarvis

1. Activate your virtual environment (if not already activated):
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Run the launch script:
```bash
python launch.py
```

## Usage

Once Jarvis is running, you can interact with it using natural language. Here are some example commands:

- "What's the weather in New York?"
- "Show me the latest news about technology"
- "What's my CPU usage?"
- "List the files in my current directory"
- "Show me running processes"
- "Search for information about Python programming"

To exit Jarvis, type:
- "exit"
- "quit"
- "bye"

Or press Ctrl+C

## Directory Structure

```
jarvis/
├── core/
│   ├── agent/         # Agent implementations
│   ├── brain/         # LLM and decision making
│   └── tools/         # Tool implementations
├── data/
│   ├── logs/          # Log files
│   └── temp/          # Temporary files
├── config/            # Configuration files
├── tests/             # Test files
├── .env               # Environment variables
├── launch.py          # Launch script
├── main.py            # Main entry point
└── requirements.txt   # Dependencies
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for GPT models
- ElevenLabs for voice synthesis
- Whisper for speech recognition
- ChromaDB for vector storage
- All other open-source contributors

## Support

For support, please:
- Open an issue on GitHub
- Check the [documentation](docs/)
- Join our [Discord community](https://discord.gg/jarvis)

## Roadmap

- [ ] Multi-modal capabilities
- [ ] Enhanced security features
- [ ] Mobile app integration
- [ ] Plugin system
- [ ] Cloud deployment options
- [ ] More language support 