# hivemind

by Joe Hahn,<br />
jmh.datasciences@gmail.com,<br />
7 March 2018<br />
git branch=master

### Summary:
Train the hivemind, which is a very simple neural net, to send its bees to the more rewarding
fields and to avoid the less productive fields.

### Setup:

Clone this repo:

    git clone https://github.com/joehahn/hivemind.git
    cd hivemind

I am executing hivemind on a Mac laptop where I've installed
Anaconda python 2.7 plus additional libraries via:

    wget https://repo.continuum.io/miniconda/Miniconda2-latest-MacOSX-x86_64.sh
    chmod +x ./Miniconda2-latest-MacOSX-x86_64.sh
    ./Miniconda2-latest-MacOSX-x86_64.sh -b -p ~/miniconda2
    ~/miniconda2/bin/conda install -y jupyter
    ~/miniconda2/bin/conda install -y keras
    ~/miniconda2/bin/conda install -y seaborn

### Execute:

Start Jupyter notebook via

    jupyter notebook

and load the hivemind.ipynb notebook > Run.