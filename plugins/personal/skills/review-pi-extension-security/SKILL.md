---
name: review-pi-extension-security
description: This skill should be used when the user asks to "review this pi extension", "check if this extension is safe", "audit a pi extension for security", "can I trust this extension", or is evaluating a third-party @earendil-works extension module for data exfiltration, malicious code execution, unauthorized network calls, or credential exposure.
---

# Review Pi Extension Security

Review a pi extension module for security concerns, particularly data exfiltration and malicious behavior.

## Procedure

1. Clone the repository
2. Examine the source code (especially index.ts and test files)
3. Look for the following concerns:
   - Unvalidated model trust: Users can define arbitrary model chains without validation
   - Hardcoded dummy credentials
   - Any network-only calls, telemetry hooks, or code that would silently forward data to a third-party endpoint
   - Specifically check for fetch, axios, raw http/https, WebSocket connections, custom logging that would ship secrets
   - Check for hidden data exfiltration: sending device secrets to a custom backend
4. Verify that the only outbound requests are normal model-API calls that pi already performs

## Pitfalls to Avoid

- Don't assume the code is safe just because it's from a known source
- Look beyond the main entry point for hidden callbacks
- Check for eval() or dynamic code execution
- Look for environment variable access that could leak secrets

## Verification

- No unauthorized network calls
- No telemetry hooks
- No data exfiltration
- No use of eval() or dynamic code execution
- No environment variable leakage