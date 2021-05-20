# Code Forces questions scrapper CLI

Scrapes Code forces questions, convert them to markdown files and generate respective templates as well as sample input and output files for the problem to be viewed and used locally.

The CLI can handle questions with images and text as well as if the question is in the form of a pdf.

#### Note:

1. this might not work for earlier contests where input and output files are stored in `<pre>` tags with `<br> ` instead of newlines!
2. For the case when the question is a pdf, the sample input and output files will not be generated!
3. Ensure that the local md reader can support mathematical equations contained within `$ equation $`.
4. Currently does not yet support the translation of html tables. (although presenting of tables in question is quite rare)

### Usage:

CLI:

```
usage: cf_manager.py [-h] [-t TEMPLATE] [-c] [-r | -q QUESTION] [-v] contests [contests ...]

Download code forces problems and sample case as md and input output files

positional arguments:
  contests              List of contests to download

optional arguments:
  -h, --help            show this help message and exit
  -t TEMPLATE, --template TEMPLATE
                        Add path directory for the template file.
  -c, --contest         Download problems from contests instead of problemsets
  -r, --range           2 values as min max range and download contests in between
  -q QUESTION, --question QUESTION
                        download a specific question from the contest
  -v, --verbosity       changes verbosity [-v]
```

TEMPLATE defaults to template.cpp in the directory where the CLI file is stored. TEMPLATE file will not overwrite existing solution files

Saved problems will be stored in the same directory as where the CLI files is located

### Examples

```c++
python cf_manager.py -vv -r 1400 1420 // download all contests problems with 1400 to 1420 (inclusive) with verbose on
```

```c++
python cf_manager.py -q B 1510 //download problem B from contest with id of 1510
```

```c++
python cf_manager.py 1500 1510 1247 //download all contest problems from 1500, 1510 and 1247
```

```c++
python cf_manager.py -c 1500 //download all contest problems from 1500, 1510 and 1247 from CodeForces contest instead of problemset
```

### Structure:

```
Code Forces example folder
│   cf_manager.py
│   template.cpp
│
└───1510
│   └───A
│   |   │   problem.pdf
│   |   │   solution.cpp
|   |   |
│   └───B
│   |   │   problem.md
│   |   │   solution.cpp
|   |   |	input_0
|   |   |	output_0
│   ...
└───1525
│   └───A
│   |   │   problem.md
│   |   │   solution.cpp
|   |   | 	input_0
...
```

### Sample

The files generated under sample_generated_folder is obtained using:

```c++
python cf_manager.py 1525
python cf_manager.py -c 1527
python cf_manager.py -q A 1510
```
