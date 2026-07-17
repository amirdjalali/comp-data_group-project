# Sigh-Tations

![](img/sigh-tations-small.png)

This is an implementation of the [project](https://github.com/comp-data/2025-2026/tree/main/docs/project) for the 2025-2026 [Computational Management of Data](https://github.com/comp-data/2025-2026) course at the [University of Bologna](https://unibo.it).

## Team

The project was realized by:

[DanieleBottaro](https://github.com/DanieleBottaro): `FullQueryEngine`, `CitationUploadHandler`, `CitationQueryHandler`.

[simulateher](https://github.com/simulateher): `BibliographicEntityQueryHandler`. 

[rdemauro](https://github.com/rdemauro): `BibliographicEntityUploadHandler`, `BasicQueryEngine`, classes for data model.

[amirdjalali](https://github.com/amirdjalali): `CitationUploadHandler`, `CitationQueryHandler`, `BasicQueryEngine`.

## How to use

This project uses [uv](https://github.com/astral-sh/uv) to manage dependencies.

1. Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. Install dependencies: `uv sync`
3. Launch main file: `uv run python3 -m main`
4. To launch the `unittest` test file: `uv run python3 -m unittest -v test`