CAZy_utils
==========

Utilities for parsing CAZy GI numbers, and creating blastDB compatible fasta files and MetaCyc functional hierarchies. Assumes the use of an sqlite database to create hierarchy.

#### Contents:

`download_cazy_pages.py`: A simple script to download CAZy HTML pages from <http://www.cazy.org/>. Uses the structure of their URL to download all the HTML tables from each family.
`load_cazy_db.py`: Script parses HTML tables files downloaded with `download_cazy_pages.py` to export



## Example Use

This procedure worked at time of writing, but I antisipate that it may have to be re-factored slightly if the CAZy HTML format or NCBI API changes.

#### Downloaded CAZy HTML files with `download_cazy_pages.py`

```
python download_cazy_pages.py
```
*Note: You may want to check the `families` dictionary to make sure there are no new CAZy families added.*

#### Load SQLITE database of CAZy information

* parse HTML files and load into the SQLite database

```
python load_cazy_db.py -i *html --db CAZY_SQLITE_DB
```
where,
* `-i`: is a glob of the CAZy HTML tables downloaded in the previous step
* `--db`: path to the CAZY_SQLITE_DB

*Note: The script currently assume the SQLite database contains a table of the form:*

```
CREATE TABLE `CAZY_2014_09_04` (
	`fam`	TEXT,
	`num`	TEXT,
	`super`	TEXT,
	`org`	TEXT,
	`protein`	TEXT,
	`ec`	TEXT,
	`genbank`	TEXT,
	`uniprot`	TEXT,
	`pdb`	TEXT,
	`subf`	TEXT
);
```

#### Download RefSeq Sequences using the NCBI Web API

* `refseq_seqs_from_db` pulls all the unique NCBI GI numbers from the SQLite and pulls from from the Web API in batches of 500
* Produces a FASTA file compatible with the CAZy hierarchy for MetaPathways
* Note: A **stable internet connection** is critical here

```
python refseq_seqs_from_db.py --db <SQLITE_DB> -t <DB_ TABLE_NAME> -o <OUTPUT_FILE>
```

#### Extract CAZy Hierarchy for MetaPathways

* extract CAZy functional hierarchy for MetaPathways from the SQLite database

```
python extract_cazy_hierarchy_from_db.py --db <SQLITE_DB> -t <DB_ TABLE_NAME> -o <OUTPUT_FILE>
```

