# Security Policy

## Supported Versions

Proton-Autogen is actively maintained. Security updates are provided for the latest stable release and the current development branch.

| Version | Supported          |
| ------- | ------------------ |
| 3.2.x   | :white_check_mark: |
| 3.1.x   | :x:                |
| < 3.1   | :x:                |
| `main`  | :white_check_mark: |

Users are strongly encouraged to keep Proton-Autogen up to date and use the latest available release.

## Reporting a Vulnerability

If you discover a security vulnerability in Proton-Autogen, please report it privately and responsibly.

**Do not report security vulnerabilities through public GitHub issues, pull requests, or discussions.**

### Preferred method

Please send an email to:

**[n3oray77@gmail.com](mailto:n3oray77@gmail.com)**

Use a subject similar to:

`[SECURITY] Proton-Autogen vulnerability report`

Please include as much information as possible:

* A clear description of the vulnerability.
* The affected Proton-Autogen version(s).
* Steps to reproduce the issue.
* A proof of concept, if available.
* The expected and actual behavior.
* The potential security impact.
* Relevant logs, screenshots, or configuration details.
* Any possible mitigation or workaround you have identified.

Please avoid including sensitive personal information or real credentials in your report.

### Response timeline

We aim to:

* Acknowledge your report within **3 business days**.
* Provide an initial assessment within **7 business days** when sufficient information is available.
* Keep you informed about the progress of the investigation.
* Notify you when a fix or mitigation is available.

Response times may vary depending on the complexity and severity of the vulnerability.

### Disclosure

Please allow reasonable time for the vulnerability to be investigated and, when necessary, fixed before publicly disclosing the issue.

If the vulnerability is confirmed, we will work on an appropriate fix and release it as soon as reasonably possible.

Security fixes may be included in a new Proton-Autogen release and documented in the release notes.

### Out of scope

The following are generally not considered security vulnerabilities unless they demonstrate a realistic security impact:

* Bugs that do not have a security impact.
* Compatibility problems with Proton or Wine.
* Application crashes without a security impact.
* Issues caused exclusively by unsupported third-party software.
* Social engineering attacks against project contributors.
* Issues requiring physical access to the user's machine.

If you are unsure whether an issue is security-related, please contact us privately anyway. We would rather review a potentially valid report than have a security issue publicly disclosed.

## Security Considerations

Proton-Autogen launches Windows executables through Proton or Wine and may interact with local files, game/application prefixes, Steam installations, and system configuration.

Users should therefore:

* Only run executables from trusted sources.
* Keep Proton-Autogen, Proton/Wine, and their Linux distribution up to date.
* Review third-party executables before running them.
* Avoid running untrusted applications with elevated privileges.
* Never share credentials, API keys, or other secrets in bug reports.

Thank you for helping keep Proton-Autogen and its users secure.

