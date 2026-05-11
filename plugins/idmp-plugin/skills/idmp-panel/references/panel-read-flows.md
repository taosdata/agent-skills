# panel read flow

The frontend panel page does more than list and search. On detail pages it also runs the query, generates SQL, and validates SQL and time ranges.

Recommended order:

1. List and detail:

   ```bash
   idmp-cli panel panels list --params '{"elementId":123}'
   idmp-cli panel panels get --params '{"elementId":123,"panelId":456}'
   ```

2. Run the panel query:

   ```bash
   idmp-cli panel panels query --params '{"elementId":123}' --data '{...}'
   ```

3. Inspect the frontend-generated SQL:

   ```bash
   idmp-cli panel panels sqls --params '{"elementId":123}' --data '{...}'
   idmp-cli panel init list --params '{"elementId":123}'
   ```

4. Validate SQL or the time range:

   ```bash
   idmp-cli panel verify create --data '{"from":"now-12h","to":"now"}'
   idmp-cli panel verify create-post --params '{"elementId":123}' --data '{...}'
   ```

5. When imputation or saved interpolation results are needed:

   ```bash
   idmp-cli panel imputation create --params '{"elementId":123}' --data '{...}'
   idmp-cli panel imputation create-post --params '{"elementId":123}' --data '{...}'
   ```

Notes:

- The frontend auto-fills the default timezone for `fromText` and `toText` values formatted as `yyyy-MM-dd HH:mm:ss`.
- `panel verify create` validates only time-range text, so the body should contain only `from` and `to`.
- `panel verify create-post` is the single advanced-SQL verify DTO. Do not send the full panel DTO there.
- `query` and `sqls` use the full panel or query DTO, not a few loose query parameters.
