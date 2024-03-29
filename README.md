<a name="readme-top"></a>

# phastDNA

## Getting started
phastDNA can be run as a CLI program or as a GUI program. Both versions have exactly the same computational capabilities. GUI app is a user-friendly version intended for users who are not experts in bioinformatics or familiar with terminal.

### System Requirements
There are different software requirements, depending on the usage of the app.

#### Running phastDNA from CLI only:

- Python 3.8 or newer
- UNIX-based operating system

#### Full phastDNA (CLI + GUI)

- Python 3.8 or newer
- UNIX-based operating system
- Modern web browser (Chromium-based browsers are preferred, e.g. Google Chrome)
- Internet connection

### Hardware requirements:
Depending on the use case, the hardware requirements vary.

#### Prediction

- multi-threaded processor - the more threads, the faster phastDNA should run
- at least 4 GB RAM - this is a safe number for Edwards et al. dataset. For larger datasets or for prediction using models trained with longer k-mers or with more samples, you will likely need more RAM

#### Training

- multi-threaded processor - the more threads, the faster phastDNA should run
- => 10 GB RAM - this is a safe number, since 10 GB was enough for most of the runs on Edwards et al. dataset. RAM usage also depends on settings - higher min and max k-mer size will result in higher memory allocation, as well as higher number of input sequences.
- 10 GB of disk space, under the same conditions as the memory requirement. Also, an SSD is recommended, since phastDNA performs quite a bit of IO operations. HDD will work but will be significantly slower. 

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Installation
1. Clone this repository or download the latest version from the Releases section:
```bash
git clone https://github.com/phenolophthaleinum/phastDNA.git
cd phastDNA
```

2. Create a virtual environment:

``` bash
python -m venv venv && source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. *Optional*: build [fastDNA](https://github.com/rmenegaux/fastDNA) from source

> **Note**
> If included binaries do not work, this step will be **required**.

> **Warning**
> Only included source of fastDNA is compatible with phastDNA. If you would like to introduce any changes, use the included code, not from the fastDNA repository.

[View fastDNA README](fastDNA/README.md#requirements)

5. *Optional*: download Edwards et al. dataset for training

Currently, that's the only dataset that is compatible with training. This is the highest priority to standardise the usage of different datasets. Original link to the dataset is not available anymore, but its copy is hosted at [AMU Computational Biology Department](http://combio.pl/):

<!-- is this not available? -->
```
wget http://combio.pl/files/edwards2016.zip
```
<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Usage

### CLI version
Only minimal use cases are shown here. For full description, type:
```bash
python phastdna.py -h
```
#### Prediction
```bash
python phastdna.py -O output_dir/ -C path_to_classifier/ -v path_to_virus_fastas/
```
#### Training
```bash
python phastdna.py -O output_dir/ -H path_to_host_dataset/ -V path_to_virus_dataset/
```

### GUI version
To run the webapp version, execute:
```bash
python phastDNA_gui.py
```
The webapp is hosted on computer's localhost. The address will be printed once the app is started.
Open that address in your browser to access phastDNA GUI. The address most likely will be: `http://127.0.0.1:5000/`

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Roadmap
- [ ] Standarise usage of other datasets
- [ ] Improving classifiers
  - [ ] More hyperparameter optimisation
  - [ ] Create Metaclassifier
- [ ] Migrate UI to Electron app
- [ ] Create documentation

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## License
Distributed under the GNU General Public License v3.0. See LICENSE.txt for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## References


<p align="right">(<a href="#readme-top">back to top</a>)</p>
