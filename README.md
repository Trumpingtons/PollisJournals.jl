# PollisJournals.jl

The journals of [OpenAlex](https://openalex.org) and of the [Norwegian Register for Scientific Journals, Series and Publishers](https://kanalregister.hkdir.no/en), as two Parquet files, for the built-in database PollisJournals of [Pollis](https://pollis.org).

The files are the package's artifact, which Pkg downloads when the package is added or updated:

```julia
using PollisJournals
PollisJournals.parquet()    # the path of journals.parquet
PollisJournals.norwegian()  # the path of norwegian.parquet
PollisJournals.snapshot()   # the date of the OpenAlex snapshot it was built from
```

Each month a workflow looks for a new snapshot of OpenAlex's sources and, when there is one, builds `journals.parquet` from it, and `norwegian.parquet` from the Norwegian register as it is that day, with `build/build.py`, publishes them as a release named after the snapshot's date, and points `Artifacts.toml` to it. Pollis installs the package, keeps it up to date with GitHub, and copies the files into the tables of PollisJournals.

## journals.parquet

One row per source with at least one work: 251,461 in the snapshot of 2026-10-14 (203,247 journals, and repositories, conferences, book series and ebook platforms).

| Column | |
|---|---|
| `id` | OpenAlex id, e.g. `S127742747` |
| `title`, `alternate_titles` | |
| `issn_l`, `issn` | the linking ISSN, unique, and every ISSN |
| `type` | journal, repository, conference, book series, ebook platform, other |
| `publisher`, `country` | |
| `field`, `subfield`, `topic` | the most frequent topic of its works, with its field and subfield |
| `works_count`, `oa_works_count`, `cited_by_count` | |
| `mean_citedness_2yr` | the mean citations, this year, of the works of the two years before: OpenAlex's analogue of the impact factor |
| `h_index`, `i10_index` | |
| `is_oa`, `is_in_doaj`, `is_core`, `apc_usd` | |
| `first_year`, `last_year`, `homepage` | |
| `counts_by_year` | works and citations by year |
| `updated` | when OpenAlex last updated the source |

## norwegian.parquet

One row per journal or series of the Norwegian register: 40,245 on 2026-10-20, read from its [open API](https://kanalregister.hkdir.no/api/krtabeller/bulk-csv?rptNr=851). The API gives field, country and language in Norwegian; the build translates them with the register's own English names, kept in `build/norwegian_english.json` from its English search page.

| Column | |
|---|---|
| `id` | the register's id, e.g. `341723` |
| `title`, `international_title` | |
| `issn`, `eissn` | print and online ISSN |
| `active` | still published |
| `is_in_doaj` | |
| `field`, `area` | the register's field (NPI field, e.g. `Economics`) and area (e.g. `Social sciences`) |
| `publisher`, `issuer` | the publisher and the society or body that issues it |
| `country`, `language` | e.g. `United Kingdom, United States`, `English` |
| `is_conference` | a conference series |
| `established`, `discontinued` | years |
| `homepage` | |
| `levels` | the level for each year, from 2004: 0 not academic, 1 academic, 2 leading, X under review (it may be given level 0) |
| `updated` | when the register last changed the row |

## Licence

The package code is MIT licensed. The data of `journals.parquet` is OpenAlex's, [CC0](https://creativecommons.org/publicdomain/zero/1.0/). `norwegian.parquet` contains data under the [Norwegian Licence for Open Government Data (NLOD) 2.0](https://data.norge.no/nlod/en/2.0), distributed by the Norwegian Directorate for Higher Education and Skills (HK-dir).

To build the file yourself:

    pip install duckdb
    python build/build.py [output folder]
