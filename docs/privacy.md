# Privacy

NativeRelay is local-first and has no network or cloud dependency. Collectors emit metadata only. They never read file contents, environment variable values, credentials, or secrets.

File paths, executable paths, PIDs, parent PIDs, and event times can still be sensitive. Process argv may contain tokens, passwords, or private paths. It is excluded by default; the Linux CLI requires explicit `--include-command` to read it from `/proc/<pid>/cmdline`. Consumers should keep event streams local and apply their own retention/access controls.
