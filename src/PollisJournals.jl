"""
	PollisJournals

The journals of OpenAlex (CC0), one Parquet file, that Pollis copies into its built-in database PollisJournals. The
file is this package's artifact, downloaded by Pkg when the package is added or updated; a workflow updates it each
month, when OpenAlex publishes a new snapshot of its sources.

```julia
using PollisJournals, DuckDB
DBInterface.execute(DBInterface.connect(DuckDB.DB), "SELECT * FROM '$(PollisJournals.parquet())' LIMIT 5")
```
"""
module PollisJournals

using Artifacts

"""The Parquet file of the journals of OpenAlex, a row per journal, repository, conference or book series with at least one work."""
parquet() = joinpath(artifact"journals", "journals.parquet")

"""The date of the snapshot of OpenAlex that `parquet()` was built from."""
snapshot() = readchomp(joinpath(artifact"journals", "snapshot.txt"))

end
