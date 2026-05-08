# Agent Quick Start

1. Initialize config and log in:

   ```bash
   idmp-cli config init --server http://your-idmp:6042 --username admin@example.com
   printf '%s\n' "$IDMP_E2E_PASSWORD" | idmp-cli auth login --username "$IDMP_E2E_USERNAME" --password-stdin
   idmp-cli auth check --remote
   idmp-cli doctor
   ```

2. Decide whether the task is **element mode** or **template mode**:

   - explorer / real elements / real analyses: use `/elements/**`
   - libraries / templates / template analyses: use `/templates/elements/**`

3. Before any write, locate the target object instead of guessing IDs:

   ```bash
   idmp-cli element elements search --params '{"keyword":"district","current":1,"limitSize":20}'
   idmp-cli element elements path --params '{"elementId":123}'
   idmp-cli element elements get --params '{"elementId":123}'
   ```

4. Before a form-style workflow, preload dependencies in frontend order:

   ```bash
   idmp-cli attribute elements attributes --params '{"elementId":123}'
   idmp-cli element elements sub-templates --params '{"elementId":123}'
   idmp-cli analysis trigger-types list --params '{"elementId":123,"applyOnSelf":false,"elementTemplateId":456}'
   idmp-cli attribute attributes new-name --params '{"elementId":123}'
   idmp-cli analysis analyses list --params '{"elementId":123,"current":1,"size":20}'
   ```

5. After a write, reread the object and confirm the status:

   ```bash
   idmp-cli analysis analyses get --params '{"elementId":123,"id":456}'
   idmp-cli analysis analyses resume --ack-risk --params '{"elementId":123,"id":456}'
   ```

6. When a shortcut is not enough, prefer the generated command first and raw API last:

   ```bash
   idmp-cli schema analysis.analyses.create
   idmp-cli analysis analyses create --ack-risk --params '{"elementId":123}' --data '{...}'
   idmp-cli api POST /api/v1/elements/123/analyses --data '{...}'
   ```
