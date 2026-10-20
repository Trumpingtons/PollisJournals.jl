# Builds journals.parquet, the journals of OpenAlex (CC0) that Pollis copies into its built-in database
# PollisJournals: one row per source (journal, repository, conference, book series...) with at least one work,
# its identifiers, publisher, field, OpenAlex's indicators, and its works and citations by year.
#
# Reads the Parquet snapshot of OpenAlex's sources, free and without a key:
# https://openalex.s3.amazonaws.com/data/parquet/sources/manifest.json
#
#     pip install duckdb
#     python build/build.py [output folder]

import json
import pathlib
import sys

import duckdb

MANIFEST = 'https://openalex.s3.amazonaws.com/data/parquet/sources/manifest.json'

out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.')
out.mkdir(parents=True, exist_ok=True)

con = duckdb.connect()
con.execute('INSTALL httpfs; LOAD httpfs')
manifest = json.loads(con.execute('SELECT content FROM read_text(?)', [MANIFEST]).fetchone()[0])
urls = [file['url'].replace('s3://openalex/', 'https://openalex.s3.amazonaws.com/') for file in manifest['files']]
files = ', '.join("'" + url + "'" for url in urls)
con.execute(f"""
COPY (
    SELECT
        replace(id, 'https://openalex.org/', '') AS id,
        display_name AS title,
        issn_l,
        issn,
        alternate_titles,
        type,
        host_organization_name AS publisher,
        country_code AS country,
        topics[1].field.display_name AS field,
        topics[1].subfield.display_name AS subfield,
        topics[1].display_name AS topic,
        works_count,
        oa_works_count,
        cited_by_count,
        summary_stats."2yr_mean_citedness" AS mean_citedness_2yr,
        summary_stats.h_index AS h_index,
        summary_stats.i10_index AS i10_index,
        is_oa,
        is_in_doaj,
        is_core,
        apc_usd,
        first_publication_year AS first_year,
        last_publication_year AS last_year,
        homepage_url AS homepage,
        [{{'year': c.year, 'works': c.works_count, 'cited_by': c.cited_by_count}} FOR c IN counts_by_year] AS counts_by_year,
        CAST(updated_date AS DATE) AS updated
    FROM read_parquet([{files}], union_by_name = true)
    WHERE works_count > 0
    -- A source updated twice is in two files: the latest is kept
    QUALIFY row_number() OVER (PARTITION BY id ORDER BY updated_date DESC) = 1
    ORDER BY title
) TO '{out / 'journals.parquet'}' (FORMAT parquet, COMPRESSION zstd)
""")
count = con.execute(f"SELECT count(*) FROM '{out / 'journals.parquet'}'").fetchone()[0]
(out / 'snapshot.txt').write_text(manifest['date'] + '\n')
print(f"journals.parquet: {count} sources, OpenAlex snapshot of {manifest['date']}")
