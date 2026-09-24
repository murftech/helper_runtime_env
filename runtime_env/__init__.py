import os
import sys
from pathlib import Path

# This is the `######## ENVIRONMENT STUB PENDING DRY GIT ########` block from the
# top of every pipe_hdb script, moved into an installable package. Three changes a
# library needs (its own __file__ is the library, not the caller):
#   - IS_SH can't test `'__file__' in globals()` here -> it's the negation
#   - the src-dir bootstrap is a function that takes the caller's repo-relative src path
#   - the IS_SH branch uses sys.argv[0] (the process entry point) instead of __file__


# ── WHICH ENVIRONMENT? (at most one is True; the real 3 are mutually exclusive) ──
IS_DATABRICKS    = os.path.isdir('/databricks') or 'DATABRICKS_RUNTIME_VERSION' in os.environ # use two becasue number 2 may be required on classic clusters
IS_IPYTHON       = ('IPython' in sys.modules) and not IS_DATABRICKS # not databricks is unfortunately needed because it pulls and ipython in
IS_SH            = not (IS_DATABRICKS or IS_IPYTHON)  # `python x.py` - can't test `'__file__' in globals()` from inside a library
IS_LOCAL = IS_IPYTHON or IS_SH

# tester
# IS_DATABRICKS=True
print(f'[ENVIRONMENT check] IS_SH: {IS_SH},  IS_IPYTHON: {IS_IPYTHON}, IS_DATABRICKS: {IS_DATABRICKS}')
n_env = sum([IS_SH, IS_IPYTHON, IS_DATABRICKS])
if n_env > 1:
    raise Exception('More than 1 runtime turned up true. Edge case is happening. Script cannot continue. Debug in dev')
elif n_env == 0:
    raise Exception('No runtime could be identified with our conditionals. Script might not continue correctly. Debug in dev')
else:
    print('okay to proceed')


'''
IS_DATABRICKS
# In databricks, sys.argv[0] := '/Workspace/Users/murftech7@gmail.com/deployments/pipe_hdb/src/xxx.py'
IS_SH:
# if we use python xxx.py, __file__ is always the path ending with xxx.py, resolve to absolute, then up one space onto it's src
# for now, xxx.py and everything it imports (providers/, helper_datagov.py, helper_transit.py, …) must be flat siblings in the same directory.
IS_IPYTHON:
Ruled that ipython should always be turned on from repo root.
'''


def add_src_to_path(repo_rel_src):
    # repo_rel_src: the src dir RELATIVE TO THE REPO ROOT, e.g. 'modules/pipe_hdb/src'
    #               (used directly for IS_IPYTHON, where cwd is the repo root; for
    #               IS_SH/IS_DATABRICKS only its LAST segment is used - see below)
    # helper
    if IS_DATABRICKS or IS_SH:
        # 2026-09-24: was `Path(sys.argv[0]).resolve().parent` - the running script's
        # OWN directory. That silently broke the moment a caller's entry script moved
        # into a subfolder of its src dir (e.g. src/pipeline/x.py): the immediate
        # parent became src/pipeline, not src, so anything in a SIBLING of pipeline/
        # (providers/, io_helpers/, ...) stopped being importable.
        # Fix: walk UP from the running script looking for an ancestor directory named
        # the same as repo_rel_src's last segment (e.g. 'src'), instead of assuming
        # it's the immediate parent. Backward compatible for every existing caller -
        # checked live 2026-09-24 across pipe_hdb, pipe_hdb_pandas_mirror and
        # pyspark_practice: in each, the entry script already sits DIRECTLY inside
        # that folder, so the very first ancestor checked is the same directory this
        # used to return unconditionally. Only a caller nesting scripts DEEPER (like
        # pipe_hdb/src/pipeline/) sees new (intended) behavior.
        target_name = Path(repo_rel_src).name
        script_path = Path(sys.argv[0]).resolve()   # library can't use the caller's __file__; python x.py sets argv[0] to the script
        for ancestor in script_path.parents:
            if ancestor.name == target_name:
                _src = ancestor
                break
        else:
            raise RuntimeError(
                f"add_src_to_path({repo_rel_src!r}): no ancestor directory named "
                f"{target_name!r} found above {script_path} - is the running script "
                f"actually somewhere under a {target_name!r} folder?")
    elif IS_IPYTHON:
        _src = Path.cwd() / repo_rel_src
    print(_src)
    sys.path.insert(0, str(_src))
