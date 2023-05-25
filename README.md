# GPT Diagrams Plugin

This plugin uses `kroki.io` or networkx and matplotlib to generate diagrams from GPT instructions.  It returns a link which is then rendered by the GPT chat window.

## Installation

If you have access to the plugin store, you can install the plugin from there using the "Install an unverified plugin" 
link until the plugin is approved by OpenAI and then it should be available via
the OpenAI plugin store.

To install an unverified plugin, use the following URL:

```
https://gpt-diagrams.herokuapp.com
```

## Development

```bash
pip install -r requirements.txt
python main.py
```

This will run the service at `localhost:5003`.  To install the plugin within ChatGPT, 
you must first have been granted access to plugin development by OpenAI, then 
you can use `localhost:5003` as the URL after clicking on the 
"Develop your own plugin" link on the Plugin store.

As of today, it takes some time to get approval from OpenAI so have patience!
