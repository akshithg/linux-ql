# Attribution

This project vendors and adapts CodeQL queries from several open-source
projects. Original authors and licenses are listed below.

## Google Security Research

- **Source**: https://github.com/google/security-research/tree/master/analysis/kernel/heap-exploitation
- **License**: Apache-2.0
- **Author**: Google Security Research team
- **Queries adapted**:
  - `queries/heap/interesting_objects.ql` — from `InterestingObjects.ql`
  - `queries/lib/KernelAlloc.qll` — `KmallocCall` and `FlexibleArrayMember` classes

## mebeim/linux-kernel-experiments

- **Source**: https://github.com/mebeim/linux-kernel-experiments/tree/master/codeql
- **License**: MIT
- **Author**: Marco Bonelli (mebeim)
- **Queries adapted**:
  - `queries/heap/kmallocd_structs.ql` — from `kmallocd_structs.ql`
  - `queries/heap/kfreed_structs.ql` — from `kfreed_structs.ql`
  - `queries/heap/kfreed_structs_with_func_ptrs.ql` — from `kfreed_structs_with_func_ptrs.ql`
  - `queries/init/bad_init_calls.ql` — from `bad_init_calls.ql`
  - `queries/lib/KernelSlab.qll` — `kmallocSlab()` predicate from `utils.qll`
  - `queries/lib/KernelFunc.qll` — `KernelFunc` class from `utils.qll`

## flounderK/linux-kernel-codeql

- **Source**: https://github.com/flounderK/linux-kernel-codeql
- **License**: Unlicensed (public repository)
- **Author**: flounderK
- **Queries adapted**:
  - `queries/structures/all_struct_sizes.ql` — from `all_nonzero_struct_sizes.ql`
  - `queries/structures/all_struct_fields.ql` — from `all_struct_fields.ql`

## Original queries

- `queries/structures/ifdef_config.ql` — original to this project
- `queries/taint/size_t_to_int.ql` — original, inspired by Sequoia CVE-2021-33909 variant analysis

## Excluded (future work)

- **UACatcher** (https://github.com/AntonioBlanworkedoA/UACatcher) — requires
  custom CodeQL engine patches; not compatible with standard CodeQL CLI.
  Revisit if upstream CodeQL adds the required extension points.
