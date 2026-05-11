# data import and export read flow

Recommended order:

1. Read exportable root elements first:

   ```bash
   idmp-cli data first-level-elements list
   ```

2. Then inspect historical records:

   ```bash
   idmp-cli data records list
   ```

3. Download an artifact when the record file name is known:

   ```bash
   idmp-cli data download get --params '{"name":"export.zip"}'
   ```

4. Run a global export:

   ```bash
   idmp-cli data import-and-export export --ack-risk --data '{"elementIds":[123],"elementTemplateIds":[456],"uomIds":[789]}'
   ```

5. Inspect the schema before a global import:

   ```bash
   idmp-cli schema data.import-and-export.import
   ```

Notes:

- `download` uses the file name returned by `records`.
- Datasource CSV import belongs to the `datasource` domain, not the global import or export package flow here.
