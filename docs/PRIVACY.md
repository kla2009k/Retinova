# Privacy and Safety

## Public Preview

The GitHub Pages preview performs file type, file size, and image decoding checks in the browser. It does not upload the selected image, create an account, or store medical history.

## Local optional proxy

`dashboard/serve_with_log.py` can call the legacy Roboflow model only when `ROBOFLOW_API_KEY` is supplied as a server environment variable. The key must never be embedded in client JavaScript or committed. Rotate any key that was previously exposed.

## Data rules for future inference

- Collect the minimum data needed.
- Obtain consent and document purpose/retention.
- Reject identifiers in filenames and metadata where possible.
- Do not log raw images, base64 payloads, credentials, or patient identifiers.
- Encrypt transport and stored data with managed secrets and access controls.
- Define deletion, incident-response, and audit procedures before accepting patient data.
- Complete legal, ethics, and clinical review for the intended deployment jurisdiction.

## Safety rules

- Always label output as screening support, not diagnosis.
- Provide an uncertainty/quality path instead of forcing a disease prediction.
- Urgent symptoms must direct users to professional care without waiting for AI.
- Require human review before any clinical decision.
