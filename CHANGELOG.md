# 0.3.1
- Fix comparing order of contracts in `diff`/`breaking`

# 0.3.0
- Handle non-existent schema specification when using `diff`/`breaking`
- Resolve local and remote resources such as schema specifications when using "$ref: ..." notation
- Implement `schema` command: prints your schema
- Implement `quality` command: prints your quality definitions 
- Implement the `inline' command: resolves all references using the "$ref: ..." notation and writes them to your data contract.
- Allow remote and local location for all data contract inputs (`--file`, `--with`)

# 0.2.0

- Suggest a fix during `init` when the file already exists
- Rename `validate` command to `lint`
- Add `diff` command for dbt schema specification
- Add `breaking` command for dbt schema specification
- Remove `check-compatibility` command
- Improve usage documentation

# 0.1.1

Initial release
