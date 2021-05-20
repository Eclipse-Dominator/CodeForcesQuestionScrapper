# MIT License

# Copyright (c) 2021 ZQ

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from typing import List, Optional, Tuple
import requests
from html.parser import HTMLParser
import os
import argparse


class CfParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.mkdown_data = ""
        self.searching = False
        self.drawTable = False
        self.tag = []
        self.input_bool = False
        self.input_text = ""
        self.output_text = ""
        self.input = []
        self.output = []
        self.ul_ol_container = []
        self.last_removed_tag = ""
        self.tempData = ""
        self.inlineContainers = set(["span", "br", "ol", "ul"])

    def addTemplate(self, path: str):
        try:
            with open(path, 'r') as f:
                self.template = f.read()
        except Exception as e:
            print("Unable to find template file!")

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        if not self.searching:
            if self.checkClass((tag, attrs), "div", "class", "problem-statement"):
                self.searching = True
            self.tag.append((tag, attrs))
        else:
            self.tag.append((tag, attrs))
            if (tag == "img"):
                for attr in attrs:
                    if attr[0] == "src":
                        self.tempData += f"\n![]({attr[1]})"
                        break
            elif self.checkClass(self.tag[-1], "div", "class", "input"):
                self.input_bool = True
                self.drawTable = True
            elif self.checkClass(self.tag[-1], "div", "class", "output"):
                self.input_bool = False
                self.drawTable = True
            elif self.checkClass(self.tag[-1], "ul"):
                self.tempData += "\n"
                self.ul_ol_container.append(["ul", "-"])
            elif self.checkClass(self.tag[-1], "ol"):
                self.tempData += "\n"
                self.ul_ol_container.append(["ol", 0])

            elif self.checkClass(self.tag[-1], "div", "class", "input-specification"):
                self.tempData += "\n\n------\n"
            elif self.checkClass(self.tag[-1], "div"):
                self.tempData += "\n"
            elif self.checkClass(self.tag[-1], "p"):
                self.tempData += "\n\n"

    def handle_endtag(self, tag: str) -> None:
        if not self.searching:
            return
        self.last_removed_tag = self.tag.pop()

        if self.checkClass(self.last_removed_tag, "div", "class", "problem-statement"):
            self.searching = False
        elif self.checkClass(self.last_removed_tag, "div", "class", "property-title"):
            self.tempData += ": "
        elif self.checkClass(self.last_removed_tag, "div", "class", "header"):
            self.tempData += "\n\n------\n"
        elif self.checkClass(self.last_removed_tag, "pre"):
            self.drawTable = False
        elif self.checkClass(self.last_removed_tag, "ul"):
            self.ul_ol_container.pop()
        elif self.checkClass(self.last_removed_tag, "ol"):
            self.ul_ol_container.pop()

        if self.last_removed_tag[0] not in self.inlineContainers:
            if self.tempData:
                self.mkdown_data += self.tempData
                self.tempData = ""

    def handle_data(self, data: str) -> None:
        if not self.searching:
            return
        if self.checkClass(self.tag[-1], "div", "class", "title"):
            if self.drawTable:
                self.tempData += f"\n| {data} |\n| ---- |\n"
            else:
                self.tempData += f"\n### {data}\n"
        elif self.checkClass(self.tag[-1], "div", "class", "section-title"):
            self.tempData += f"\n#### {data}\n"
        else:
            data = data.replace("$", "\\$")
            data = data.replace("*", "\\*")

            if self.checkClass(self.tag[-1], "pre"):
                if self.drawTable:
                    if self.input_bool:
                        self.input.append(data.strip())
                    else:
                        self.output.append(data.strip())
                    self.mkdown_data += "| " + \
                        '<br />'.join(data.strip().split('\n'))+" |"
                else:
                    self.mkdown_data += data.strip()
            else:
                if not data.strip():
                    self.tempData += "\n"
                    return
                data = data.replace("\\$\\$\\$", "$")

                if self.checkClass(self.tag[-1], "li"):
                    if self.last_removed_tag[0] not in self.inlineContainers:
                        if self.ul_ol_container[-1][0] == "ul":
                            delimeter = "- "
                        else:
                            self.ul_ol_container[-1][1] += 1
                            delimeter = f"{self.ul_ol_container[-1][1]}. "
                        self.tempData += "\n"+"  " * \
                            (len(self.ul_ol_container)-1) + delimeter
                    elif self.last_removed_tag[0] in ["ul", "ol"]:
                        self.tempData += "\n\n"+"  " * \
                            (len(self.ul_ol_container))

                if self.checkClass(self.tag[-1], "a"):
                    for prop in self.tag[-1][1]:
                        if prop[0] == "href" and prop[1]:
                            data = f"[{data}]({prop[1]})"

                if self.checkClass(self.tag[-1], "span", "class", "tex-font-style-bf"):
                    data = f"**{data}**"

                self.tempData += data

    def clearData(self):
        self.__init__()

    def saveData(self, url: str):
        if (url[-1] != "/"):
            url += "/"
        with open(f"{url}problem.md", "w+") as f:
            f.write(self.mkdown_data)
        for i in range(len(self.input)):
            with open(f"{url}input_{i}", "w+") as f:
                f.write(self.input[i])
            with open(f"{url}output_{i}", "w+") as f:
                f.write(self.output[i])
        self.saveTemplate(url)

    def saveTemplate(self, url: str):
        if (url[-1] != "/"):
            url += "/"
        if not os.path.exists(f"{url}solution.cpp"):
            with open(f"{url}solution.cpp", "w+") as f:
                f.write(self.template)

    @staticmethod
    def checkClass(data: Tuple[str, List[Tuple[str, Optional[str]]]],
                   checkTag: str,
                   checkAttr: Optional[str] = None,
                   checkData: Optional[str] = None
                   ) -> bool:
        tag, attrs = data

        if tag != checkTag:
            return False
        if checkAttr == None:
            return True
        for attr in attrs:
            if attr[0] == checkAttr and attr[1] == checkData:
                return True
        return False


def mkfolder_exist(path: str) -> str:
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def questionLetterGenerator():
    for i in range(65, 91):
        Letter = chr(i)
        result = yield Letter
        if result:
            continue
        additional_addon = ["1", "2", "3", "4", "5", "6", "7"]
        for j in additional_addon:
            result = yield Letter+j
            if not result:
                if j == additional_addon[0]:
                    yield ""
                    return
                break


project_dir = os.path.dirname(os.path.normpath(__file__))
project_dir = project_dir if project_dir else "."


parser = argparse.ArgumentParser(
    description="Download code forces problems and sample case as md and input output files")
parser.add_argument('contests', type=int, nargs="+",
                    help="List of contests to download")
parser.add_argument('-t', '--template', type=str,
                    help="Add path directory for the template file.", default=f"{project_dir}/template.cpp")
parser.add_argument('-c', '--contest', action="store_true",
                    help="Download problems from contests instead of problemsets")
grp = parser.add_mutually_exclusive_group()
grp.add_argument('-r', '--range', action="store_true",
                 help="2 values as min max range and download contests in between")
grp.add_argument('-q', '--question', type=str, default="",
                 help="download a specific question from the contest")
parser.add_argument('-v', '--verbosity', action="count",
                    default=0, help="changes verbosity [-v]")

args = parser.parse_args()

p = CfParser()

p.addTemplate(args.template)

if args.verbosity > 0:
    print("Verbosity mode is on")

contestsGenerator = args.contests
if args.contest:
    ROOT_DIR = "https://codeforces.com/contest/{}/problem/{}"
else:
    ROOT_DIR = "https://codeforces.com/problemset/problem/{}/{}"


if args.range:
    if len(args.contests) != 2:
        print("you need 2 argument for min and max range!")
        exit(0)
    contestsGenerator = range(args.contests[0], args.contests[1]+1)

elif args.question:
    if len(args.contests) != 1:
        print("You can only enter 1 contests when downloading individual question")
    if args.verbosity:
        print(
            f"Collecting {args.contests[0]}/{args.question} information from CodeForces.com...")
    res = requests.get(ROOT_DIR.format(args.contests[0], args.question),
                       allow_redirects=False)
    if (res.status_code != 200):
        print("Question does not exist")
        exit(0)
    if 'application/pdf' in res.headers.get("Content-Type"):
        if args.verbosity > 1:
            print(f"{args.question} is a pdf, downloading pdf...")
        with open(f"{mkfolder_exist(f'{project_dir}/{args.contests[0]}/{args.question}')}/problem.pdf", 'wb+') as f:
            f.write(res.content)
        p.saveTemplate(f"{project_dir}/{args.contests[0]}/{args.question}")
        exit(0)

    p.feed(res.content.decode('UTF-8'))

    p.saveData(mkfolder_exist(
        f"{project_dir}/{args.contests[0]}/{args.question}"))
    exit(0)
for contest in contestsGenerator:
    lettergen = questionLetterGenerator()
    Question = next(lettergen)
    while Question:
        if args.verbosity:
            print(f"Collecting {contest}/{Question} from CodeForces.com...")
        res = requests.get(ROOT_DIR.format(contest, Question),
                           allow_redirects=False)
        if (res.status_code != 200):
            if args.verbosity > 1:
                print(
                    f"{contest}/{Question} does not exist on this question. Moving on...")
            Question = lettergen.send(False)
            continue
        if 'application/pdf' in res.headers.get("Content-Type"):
            if args.verbosity > 1:
                print(f"{Question} is a pdf, downloading pdf...")
            with open(f"{mkfolder_exist(f'{project_dir}/{contest}/{Question}')}/problem.pdf", 'wb+') as f:
                f.write(res.content)
            p.saveTemplate(f"{project_dir}/{contest}/{Question}")
            continue
        p.feed(res.content.decode('UTF-8'))
        p.saveData(mkfolder_exist(f"{project_dir}/{contest}/{Question}"))
        p.clearData()
        Question = lettergen.send(True)
    if args.verbosity:
        print(f"finish collecting questions on contest {contest}")
