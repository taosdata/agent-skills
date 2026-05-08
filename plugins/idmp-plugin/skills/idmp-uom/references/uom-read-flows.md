# UOM read flow

Recommended order:

1. Inspect UOM classes first:

   ```bash
   idmp-cli uom uomclasses list
   idmp-cli uom uomclasses get --params '{"uomClassId":264033646}'
   ```

2. Then search for units:

   ```bash
   idmp-cli uom uom search --params '{"keyword":"kWh","limitSize":20}'
   ```

   If search returns near-matches, prefer an exact unit name or abbreviation before you continue. For example, choose ampere `A` instead of ampere-hour `Ah` when the operator asked for current units. Do not rely on class labels or family words alone to prove that search support is missing.

3. When class and unit IDs are known, read the unit within the class:

   ```bash
   idmp-cli uom uom get-get --params '{"uomClassId":264033646,"uomId":1753955006}'
   ```

4. When a global free-UOM ID is known, read the free unit:

   ```bash
   idmp-cli uom uom get --params '{"uomId":1753955006}'
   ```

5. When a unit conversion is needed:

   ```bash
   idmp-cli uom uom convert --ack-risk --data '[{"fromUomId":1,"inputValue":100,"toUomId":2}]'
   ```

Notes:

- `get` and `get-get` are not duplicate commands. One reads a free UOM, the other reads a UOM inside a class.
- If unit compatibility is unclear before modeling, run `convert` first.
