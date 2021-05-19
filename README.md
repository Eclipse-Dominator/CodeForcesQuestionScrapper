# Code Forces questions scrapper CLI
Scrapes Code forces questions, convert them to markdown files and generate respective templates as well as sample input and output files for the problem



### Usage:

CLI:

```
usage: cf_manager.py [-h] [-t TEMPLATE] [-r] [-q [{A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z}]] [-v]
                     contests [contests ...]
```

TEMPLATE defaults to template.cpp in the directory where the CLI file is stored.

Saved problems will be stored in the same directory as where the CLI files is located

##### Note: this might not work for earlier contests where input and output files are stored in ```<pre>``` tags with  ```<br> ```instead of newlines!

### Examples 

```c++
python cf_manager.py -r 1400 1420 // download all contests problems with 1400 to 1420 (inclusive)
```

```c++
python cf_manager.py -q B 1510 //download problem B from contest with id of 1510
```

```c++
python cf_manager.py 1500 1510 1247 //download all contest problems from 1500, 1510 and 1247
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



