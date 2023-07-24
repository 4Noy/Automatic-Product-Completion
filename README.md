# Automatic Product Completion

## Overview

The Automatic Product Completion tool is a Python script designed to automate the process of creating and completing product information. It can be easily integrated into your website using some PHP code.

This tool leverages Selenium with Chrome to retrieve images from Google searches and utilizes OpenAI's large language models to generate article descriptions. However, please note that due to certain extravagances in the generated text, human review is recommended for the descriptions.

The tool was created by Noy.

## Prompt & Request Files

To include the product name, brand, or EAN (European Article Number) in the prompt, you should use `{name}`, `{brand}`, and `{ean}` respectively. For optimal results, follow the example provided, where all parts of the product are split and described.

**Example Prompt File (ExemplePrompt.txt):**
```
SEO description of: {Name} of the brand {Brand}
In two parts

A first part: 20 words MAXIMUM to make you want to buy
And a second part: 60 words MAXIMUM the description of the product
```

The Search File should be structured similarly to the Prompt File.

## Usage

The tool offers several options for customization:

```
Options:
  -h, --help                      Show this help message and exit
  -n, --name <Product Name>       Set Product Name
  -b, --brand <Product Brand>     Set Product Brand
  -e, --EAN <Product EAN13>       Set Product EAN13
  -i, --ID <Product ID>           Set Product ID
  -m, --mode <Mode>               Set Tool Mode
  -p, --prompt <File Directory>   Use the given prompt file
  -s, --search <File Directory>   Use the given search File to find pictures
  -o, --output <Directory>        Save the result IN Directory
  -v, --verbose                   Verbose Mode
  --picnum <Number>               Specify picture number, DEFAULT: 3
  --model <Model Name>            Specify OpenAI LLM cht, DEFAULT: gpt-3.5-turbo
  --language <Language>           Change chat language response
```

The tool supports multiple modes, which can be selected using the `-m` or `--mode` option:
- Mode 1 (DEFAULT): Generates Description, Meta, and Pictures.
- Mode 2: Retrieves Only Pictures.
- Mode 3: Generates Only Description and Meta.

## License

This project is licensed under the [MIT License](LICENSE).

## Contributing

Contributions to this project are welcome. If you encounter any issues or have ideas for improvement, feel free to create an issue or submit a pull request.

## Author

This tool was developed by [Noy](https://github.com/4Noy/).

## Model and Language

The tool utilizes OpenAI's large language models, with the default model being `gpt-3.5-turbo`. You can specify a different model using the `--model` option. The language used for chat responses can also be changed with the `--language` option.

Please refer to the source code and comments within the Python script for a more detailed understanding of the tool's functionalities.