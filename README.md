# Instructions

## How to install

* Clone this repo (or download the single files in this folder, MkitMod folder and Kubesec binary included)
* If you are running under a different OS than Linux, you need to download the Kubesec binaries for your OS from [here](https://github.com/controlplaneio/kubesec/releases) (or compile it from source) and substitute the ones found in this folder.
* install dependencies: `pip install -r requirements.txt` (we suggest to use a virtual environment)

## How to run

In order to run the Mkit tool (included in the complete scan) you need docker installed and running.
Additionally you need a kubectl configuration file under the default folder `$HOME/.kube/config` and permissions to create/delete Pods and Jobs in the default namespace.
The most simple way to run the program is: 
`python prototype.py complete` 
this will run the tool in the standard way with writing to standard output the json report.

### Tool selection and output

The tools offer many options: you can do scans with a single tool changing from complete to one of `cis`, `kube-hunter`, `kubesec` or `mkit`.

There are two filtering options: `-f` for reporting only failing tests and `-s` followed by the severity of the vulnerability that you want to select (all, high, medium, low).

Additionally there is an output option: with -o you can select the output format, `json` for a json object to standard output and `html` for an html page named `report.html` that output the report in a simple but easy to read html page.

Finally there is a verbosity flag with `-v`, augmenting the number of `v`s augment the verbosity of the output.

## Active scan

If the results of your complete scan met certain criteria you will be asked with a prompt if you want to perform an active scan.
This type of scan tries to exploit the vulnerabilities found in order to collect additional data.
Be careful! It's potentially harmfull to your cluster!
