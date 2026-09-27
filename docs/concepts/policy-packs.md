# Policy packs

Every legal number dpdpkit uses (the 48-hour pre-erasure warning, the one-year log floor, the 90-day
grievance ceiling) lives in a versioned YAML pack in
[`dpdpkit-policies`](https://github.com/dpdpkit-dev/dpdpkit-policies). No such number is in code.

```bash
dpdpkit policy show
dpdpkit policy diff dpdp-rules-2025.v1 my-pack.yaml
```

A missing or invalid pack stops dpdpkit from starting. There are no built-in defaults. See
[Rule to code](../reference/rule-to-code.md) for every key and its legal source.
