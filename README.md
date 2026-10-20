# PollisJournals.jl

The journals of [OpenAlex](https://openalex.org), as one Parquet file, for the built-in database PollisJournals of [Pollis](https://pollis.org).

The file is the package's artifact, which Pkg downloads when the package is added or updated:

```julia
using PollisJournals
PollisJournals.parquet()    # the path of journals.parquet
PollisJournals.snapshot()   # the date of the OpenAlex snapshot it was built from
```

Each month a workflow looks for a new snapshot of OpenAlex's sources and, when there is one, builds `journals.parquet` from it with `build/build.py`, publishes it as a release named after the snapshot's date, and points `Artifacts.toml` to it. Pollis installs the package, keeps it up to date with GitHub, and copies the file into the tables `journals` and `journal_years` of PollisJournals.

## The file

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

## Licence

The package code is MIT licensed. The data is OpenAlex's, [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

To build the file yourself:

    pip install duckdb
    python build/build.py [output folder]
