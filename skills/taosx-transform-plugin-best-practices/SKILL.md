---
name: taosx-transform-plugin-best-practices
description: "Best practices for building, optimizing, and reviewing TaosX transform (parser) plugins (Rust cdylib). Use when implementing taosx transform plugin FFI (parser_name/parser_version/parser_new/parser_mutate/parser_free), handling input/output memory, JSON parsing/serialization, correctness compatibility (single/batch/NDJSON), and performance optimizations (sonic-rs zero-copy typed parsing, mimalloc, allocation reuse, criterion benches)."
---

# TaosX transform plugin best practices (Rust)

## Goals
- Preserve TaosX plugin ABI compatibility (C FFI + cdylib).
- Keep hot path fast (parse + serialize) and predictable.
- Avoid UB across FFI boundaries.
- Make output semantics explicit (especially for batch input).

## Minimal ABI surface (recommended)
Export exactly these symbols:
- `parser_name() -> *mut c_char`
- `parser_version() -> *mut c_char`
- `parser_new(ctx: *const c_char, len: i32) -> ParserResponse`
- `parser_mutate(p: *mut c_void, input_p: *const u8, input_l: u32, output_p: *mut *mut u8, output_l: *mut u32) -> *const c_char`
- `parser_free(p: *mut c_void)`

Conventions:
- `ParserResponse.e == 0` => ok, `p` is context pointer.
- `parser_mutate` returns `NULL` on success; otherwise returns a `\0`-terminated error message.

## FFI safety checklist (MUST)
- Validate pointers before dereference:
  - `p` must be non-null (context)
  - `output_p` and `output_l` must be non-null
  - If `input_l > 0`, `input_p` must be non-null
- Never unwind across FFI:
  - Avoid panics (`unwrap/expect`) in exported functions.
  - Convert errors into error strings.
- Keep all `unsafe` blocks as small as possible.
- Prefer stable primitives:
  - `std::slice::from_raw_parts(input_p, len)` + `std::str::from_utf8(...)` (only if you truly need UTF-8 text)

## Output buffer ownership (choose one and document it)
You must pick a clear ownership model:

### Model A (simple, common): “runtime copies, plugin leaks per call”
- Implementation often uses `ManuallyDrop<String>` and writes pointer/len.
- Fast to implement, but leaks unless runtime frees (often it doesn’t).
- Only acceptable if you confirm TaosX runtime copies and the plugin is short-lived OR you have an explicit free path.

### Model B (recommended): “output buffer owned by parser context”
- Store `Vec<u8>` (or `String`) inside the parser context.
- Each `parser_mutate` clears/reuses it, serializes into it, and returns its pointer/len.
- Buffer is freed in `parser_free`.
- Also improves performance (allocation reuse, less allocator pressure).

## JSON performance optimizations (copy the coordinate_converter pattern)
### 1) Use sonic-rs for fast JSON
- Prefer `sonic_rs::from_slice::<T>(&[u8])` on the raw bytes.
- Prefer `sonic_rs::to_string(&out)` (or serialize into a context-owned buffer).
- Avoid `serde_json::Value` in the hot path.

### 2) Use typed structs + zero-copy borrows
For inputs where most fields are strings:
- Define `InputRecord<'a>` / `InputData<'a>` with `Cow<'a, str>`.
- Use `#[serde(borrow)]` and `#[serde(rename = "...")]`.

For fields that may arrive as either string or number:
- Use a small untagged enum, e.g.:
  - `#[serde(untagged)] enum NumOrStr<'a> { Str(Cow<'a, str>), I64(i64), U64(u64), F64(f64) }`
- Implement `safe_parse_float/safe_parse_int` that accept `Option<&NumOrStr>`.

### 3) Support both single and batch input explicitly
If upstream may send:
- single object: `{...}`
- batch array: `[{...}, {...}]`

Use:
- `#[serde(untagged)] enum InputPayload<'a> { Single(InputRecord<'a>), Batch(Vec<InputRecord<'a>>) }`

Then define policy:
- If old behavior expects “array input -> 1 placeholder output”, keep that.
- Otherwise, output N records for N inputs.

### 4) Avoid expensive generic rounding
Instead of `powi`-based rounding:
- `round6(v) = (v * 1_000_000.0).round() / 1_000_000.0`
- `round1(v) = (v * 10.0).round() / 10.0`

### 5) Minimize allocations
- Pre-allocate vectors for batch output: `Vec::with_capacity(records.len())`.
- Pre-allocate formatted strings where possible: `String::with_capacity(vin.len() + suffix.len())`.
- For regex, compile once with `LazyLock`/`OnceLock` (only if actually used).

### 6) Allocator option
- Add `mimalloc` behind a feature and enable it by default for production plugins.

## Correctness + compatibility guardrails
- Validate event gating early (cheap checks first):
  - `eventType`, then timestamps, then required fields.
- Decide what “invalid input” means:
  - Return placeholder record vs empty array vs explicit error string.
  - Keep behavior stable across versions.

## Benchmarking (MUST for performance work)
- Add Criterion benches:
  - `benches/parser_bench.rs` covering single + batch sizes (e.g. 1/10/100).
- Ensure crate can be linked in benches/examples:
  - Use `crate-type = ["cdylib", "rlib"]` during development.
- Use representative payloads:
  - Prefer `fixtures/*.json` and load with `include_bytes!()`.

## Recommended dev workflow
1) Implement correctness first; lock behavior with a few fixture-based tests.
2) Add criterion bench; measure baseline.
3) Apply sonic-rs + typed input + allocation reuse.
4) Re-run benches; confirm improvements.
5) Review FFI safety: null checks, no panics, minimal unsafe.

## Code review checklist
- No `serde_json::Value` in hot path.
- sonic-rs used on `&[u8]` input.
- Typed deserialization with `Cow` and `#[serde(borrow)]`.
- Batch semantics documented and tested.
- No panics across FFI.
- Output memory ownership model is explicit.
- Criterion bench exists and runs.
