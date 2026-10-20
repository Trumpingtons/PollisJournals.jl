"""
	PollisJournals

The journals of OpenAlex (CC0) and of the Norwegian register (NLOD 2.0), two Parquet files, that Pollis copies into
its built-in database PollisJournals. The files are this package's artifact, downloaded by Pkg when the package is
added or updated; a workflow updates it each month, when OpenAlex publishes a new snapshot of its sources.

```julia
using PollisJournals, DuckDB
DBInterface.execute(DBInterface.connect(DuckDB.DB), "SELECT * FROM '$(PollisJournals.parquet())' LIMIT 5")
```
"""
module PollisJournals

using Artifacts

"""The Parquet file of the journals of OpenAlex, a row per journal, repository, conference or book series with at least one work."""
parquet() = joinpath(artifact"journals", "journals.parquet")

"""
The Parquet file of the journals and series of the Norwegian Register for Scientific Journals, Series and Publishers,
a row per journal or series, with its level for each year (0, 1, 2 or X). Contains data under the Norwegian Licence
for Open Government Data (NLOD) 2.0, distributed by HK-dir.
"""
norwegian() = joinpath(artifact"journals", "norwegian.parquet")

"""The date of the snapshot of OpenAlex that `parquet()` was built from."""
snapshot() = readchomp(joinpath(artifact"journals", "snapshot.txt"))

end
