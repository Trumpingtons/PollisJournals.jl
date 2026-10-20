# Builds the two files that Pollis copies into its built-in database PollisJournals:
#
# - journals.parquet, the journals of OpenAlex (CC0): one row per source (journal, repository, conference, book
#   series...) with at least one work, its identifiers, publisher, field, OpenAlex's indicators, and its works and
#   citations by year. Read from the Parquet snapshot of OpenAlex's sources, free and without a key:
#   https://openalex.s3.amazonaws.com/data/parquet/sources/manifest.json
# - norwegian.parquet, the journals and series of the Norwegian Register for Scientific Journals, Series and
#   Publishers (NLOD 2.0, from HK-dir): one row per journal or series, with its level for each year. Read from the
#   register's open API: https://kanalregister.hkdir.no/api/krtabeller/bulk-csv?rptNr=851. Its field, country and
#   language are in Norwegian: they are translated with the register's own English names, from the code lists of its
#   English search page (https://kanalregister.hkdir.no/en/sok), kept in build/norwegian_english.json; a value
#   missing there stays in Norwegian.
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

# The levels of the Norwegian register: 0 not academic, 1 academic, 2 leading, X under review (it may be given
# level 0). A column per year, "Nivå 2027" back to "Nivå 2004", becomes a list of (year, level).
NORWEGIAN = 'https://kanalregister.hkdir.no/api/krtabeller/bulk-csv?rptNr=851'
english = json.loads((pathlib.Path(__file__).parent / 'norwegian_english.json').read_text(encoding = 'utf-8'))
for name, names in english.items():
    con.execute(f"SET VARIABLE {name} = MAP(?, ?)", [list(names), list(names.values())])
con.execute(f"CREATE TABLE register AS SELECT * FROM read_csv('{NORWEGIAN}', all_varchar = true, header = true)")
years = sorted(int(column[len('Nivå '):]) for (column,) in con.execute(
    "SELECT column_name FROM information_schema.columns WHERE table_name = 'register' AND column_name LIKE 'Nivå %'").fetchall())
levels = ', '.join(f"{{'year': {year}, 'level': \"Nivå {year}\"}}" for year in years)
con.execute(f"""
COPY (
    SELECT
        "Tidsskrift id" AS id,
        "Original tittel" AS title,
        "Internasjonal tittel" AS international_title,
        "Print ISSN" AS issn,
        "Online ISSN" AS eissn,
        "Aktiv" = '1' AS active,
        coalesce("Open Access" = 'DOAJ', false) AS is_in_doaj,
        coalesce(map_extract(getvariable('fields'), trim("NPI Fagfelt"))[1], nullif(trim("NPI Fagfelt"), 'Ikke tildelt')) AS field,
        CASE "NPI Fagområde"
            WHEN 'Humaniora' THEN 'Humanities'
            WHEN 'Samfunnsvitenskap' THEN 'Social sciences'
            WHEN 'Medisin og helsefag' THEN 'Medicine and health'
            WHEN 'Realfag og teknologi' THEN 'Natural sciences and technology'
        END AS area,
        "Forlag" AS publisher,
        "Utgiver" AS issuer,
        array_to_string([coalesce(map_extract(getvariable('countries'), trim(c))[1], trim(c)) FOR c IN string_split("Utgiverland", ',')], ', ') AS country,
        coalesce(map_extract(getvariable('languages'), "Språk")[1], "Språk") AS language,
        "Konferanserapport" = '1' AS is_conference,
        TRY_CAST("Etablert år" AS INTEGER) AS established,
        TRY_CAST("Nedlagt år" AS INTEGER) AS discontinued,
        "Url" AS homepage,
        [l FOR l IN [{levels}] IF l.level IS NOT NULL] AS levels,
        CAST(strptime("Sist endret", '%d-%b-%Y %H:%M:%S') AS DATE) AS updated
    FROM register
    ORDER BY title
) TO '{out / 'norwegian.parquet'}' (FORMAT parquet, COMPRESSION zstd)
""")
count = con.execute(f"SELECT count(*) FROM '{out / 'norwegian.parquet'}'").fetchone()[0]
print(f"norwegian.parquet: {count} journals and series of the Norwegian register")
