# Security Policy

## Reporting a Vulnerability

If you believe you have discovered a security vulnerability in HostLens, please report it privately rather than opening a public GitHub issue.

When reporting a vulnerability, include as much of the following information as possible:

* Description of the vulnerability
* Affected component
* Affected platform
* HostLens version or commit
* Steps to reproduce
* Expected behavior
* Actual behavior
* Potential impact
* Proof of concept, if available
* Any suggested mitigation

Please avoid including real credentials, private data, or sensitive system information in the report.

## What Should Be Reported

Examples include:

* Unauthorized access to collected host telemetry
* Unexpected transmission of telemetry
* Sensitive information being collected without the documented behavior
* Privilege escalation
* Unsafe handling of native operating-system APIs
* Memory-safety issues
* Command or code execution vulnerabilities
* Authentication or authorization issues in future networked components
* Vulnerabilities that could allow a malicious process to interfere with HostLens

If you are unsure whether an issue qualifies as a security vulnerability, report it privately.

## Supported Versions

HostLens is currently an early-stage project.

Security fixes are generally applied to the latest development version. Users should keep their HostLens installation up to date when possible.

As the project matures, supported versions and security-maintenance periods will be documented here.

## Security Boundaries

HostLens is intended to observe host-level system events.

Depending on the platform and collector, operation may require elevated operating-system permissions.

These permissions are platform-specific and should not be treated as evidence that HostLens itself is trusted or safe in every environment.

Collectors should request only the permissions required for their documented functionality.

HostLens should also avoid collecting sensitive information that is not necessary for the requested observation.

For example, observing file activity should not require capturing the contents of the file.

## Telemetry and Privacy

HostLens is designed to operate locally.

The project does not require a hosted telemetry service for its core functionality.

Collected events may contain sensitive host information such as:

* File paths
* Process names
* Process identifiers
* Command information
* Network information
* User or application metadata

Consumers of HostLens are responsible for handling collected events appropriately.

Users should review collector configuration and permissions before running HostLens on sensitive systems.

## Vulnerability Disclosure

Please allow maintainers reasonable time to investigate and address a privately reported vulnerability before publicly disclosing technical details.

Once a vulnerability has been addressed, the project may publish an advisory containing:

* Affected versions
* Fixed versions
* Impact
* Mitigation
* Relevant technical details

The timing and level of disclosure may depend on the severity and complexity of the issue.

## Security Contributions

Security-related improvements are welcome.

Contributors can help by:

* Auditing native collector code
* Reviewing privilege requirements
* Testing restricted environments
* Identifying unintended telemetry collection
* Reviewing event serialization
* Improving input validation
* Testing platform-specific security boundaries
* Documenting security assumptions

Security research should follow the same evidence-based approach used throughout HostLens: clearly distinguish observed behavior from assumptions and conclusions.

## Scope

This policy applies to the HostLens project and its official source code.

Third-party applications built using HostLens may introduce their own vulnerabilities or security requirements. Such issues should generally be reported to the maintainers of the affected application.
