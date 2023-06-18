# Anki Generator
Simple tool to convert a text in form of QA to an Anki Deck

## Usage
### Create questions
Create a file in format like:
```md
# Chapter I: Basic Usage
## Question I:
Other Context
More Context
---
Answer I
Some more explanation...
More and more...
## Question II
---
Answer
# Chapter II: Some other way to use this tool
## Choose:
Choose 2
A
B
C
D
---
B
C
## Question: What is the capital city of France?
A) London
B) Paris
C) Rome
D) Madrid
---
Madrid

```
### Run
Run like `python3 gen.py your_file.extension "Deck Name"`

## Example
To run the example just run `python3 gen.py example_convert.md "Example Anki Generator"`

