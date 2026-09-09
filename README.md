# runtime_env

Which runtime is this (`sh` / `ipython` / `databricks`), and put the calling
script's `src/` directory on `sys.path` so its siblings import by bare name.

Pip-installed everywhere the consuming scripts run (local venv, Databricks
serverless via `requirements`, docker), so it imports with no bootstrap.

## Use

```python
from runtime_env import IS_DATABRICKS, IS_IPYTHON, IS_SH, IS_LOCAL, add_src_to_path
add_src_to_path('modules/pipe_hdb/src')      # repo-relative src dir (used only for IS_IPYTHON)

if IS_DATABRICKS:
    from providers.databricks import ...
else:
    from providers.local import ...
```

## What it does

- `IS_DATABRICKS` — `/databricks` dir exists, or `DATABRICKS_RUNTIME_VERSION` is set
- `IS_IPYTHON` — `IPython` imported **and not** Databricks (Databricks serverless runs jobs in an ipykernel)
- `IS_SH` — neither of the above (`python x.py`)
- `IS_LOCAL` — `IS_SH or IS_IPYTHON`
- on import: raises if not exactly one is true
- `add_src_to_path(repo_rel_src)` — inserts the caller's `src/` at `sys.path[0]`
  (`sys.argv[0]`'s parent for sh/databricks; `cwd / repo_rel_src` for ipython)

## Install as a dependency

```toml
# pyproject.toml
dependencies = ["runtime_env @ git+https://github.com/murftech/helper_runtime_env.git"]
```
