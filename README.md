

# Automatic Product Completion


>This tool is a python script to automate Product Creation and Completion.
It can be integrated directly in Your Website with some PHP code.

>This tool get images from google searchs with chrome+selenium and get some article descriptions made by OpenAI large language models that have to be reviewed by humans due to some of his extravagances.

Tool created by Noy   


## PROMPT & REQUEST FILES
    +========================================================================+
    |To include Name, brand or EAN in the Prompt,                            |
    |you must use {name}, {ean} {brand}.                                     |
    |                                                                        |
    |To get the best results, do like the exemple,                           |
    |spliting all parts and describing all parts.                            |
    |                                                                        |
    |ExemplePrompt.txt:                                                      |
    | ______________________________________________________________________ |
    ||SEO description of: {Name} of the brand {Brand}                       ||
    ||In two parts                                                          ||
    ||                                                                      ||
    ||A first part: 20 words MAXIMUM to make you want to buy                ||
    ||And a second part: 60 words MAXIMUM the description of the product    ||
    |+======================================================================+|
    |                                                                        |
    |Write the SearchFile the same way as prompt file.                       |
    +========================================================================+

## Usage

     _____________________________________________________________________________________
    |             OPTIONS:                          Description:                          |
    +=====================================================================================+
    |   -h --help                      |  Show this help message and exit                 |
    +                                  +                                                  +
    |   -n --name <Product Name>       |  Set Product Name                                |
    +                                  +                                                  +
    |   -b --brand <Product Brand>     |  Set Product Brand                               |
    +                                  +                                                  +
    |   -e --EAN <Product EAN13>       |  Set Product EAN13                               |
    +                                  +                                                  +
    |   -i --ID <Product ID>           |  Set Product ID                                  |
    +                                  +                                                  +
    |   -m --mode <Mode>               |  Set Tool Mode                                   |
    +                                  +                                                  +
    |   -p --prompt <File Directory>   |  Use the given prompt file                       |
    +                                  +                                                  +
    |   -s --search <File Directory>   |  Use the given search File to find pictures      |
    +                                  +                                                  +
    |   -o --output <Directory>        |  Save the result IN Directory                    |
    +                                  +                                                  +
    |   -v --verbose                   |  Verbose Mode                                    |
    +                                  +                                                  +
    |   --picnum <Number>              |  Specify picture number, DEFAULT : 3             |
    +                                  +                                                  +
    |   --model <Model Name>           |  Specify Open AI LLM, DEFAULT : gpt-3.5-turbo    |
    +                                  +                                                  +
    |   --language <Language>          |  Change chat language response                   |
    +                                  +                                                  +
    ======================================================================================+



    There is multiple usages for this tool, you can change usages by changing mode.
     ___________________________________________________
    |      MODE:     |         Description:             |
    +===================================================+
    | DEFAULT:   1   |  Description, Meta and Pictures  |
    +                +                                  +
    |    2           |  Only Pictures                   | 
    +                +                                  +
    |    3           |  Only Description and Meta       |
    +                +                                  +
    ====================================================+