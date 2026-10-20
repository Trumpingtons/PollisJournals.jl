# Makes the artifact of PollisJournals from a folder holding journals.parquet and snapshot.txt: a tarball to publish
# as a release asset at `url`, and the entry of Artifacts.toml that points to it.
#
#     julia build/artifact.jl <folder> <tarball> <url>

using Pkg.Artifacts

folder, tarball, url = ARGS
hash = create_artifact() do dir
    for file in readdir(folder)
        cp(joinpath(folder, file), joinpath(dir, file))
    end
end
sha = archive_artifact(hash, tarball)
bind_artifact!(joinpath(@__DIR__, "..", "Artifacts.toml"), "journals", hash; download_info = [(url, sha)], force = true)
println("Artifacts.toml: journals ", hash, ", ", url)
