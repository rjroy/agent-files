# File Validation Pattern

**Version**: 1.0.0
**Purpose**: Reusable validation pattern for file path security, existence checks, and markdown format validation

---

## Security Validation

### Directory Traversal Prevention

**Rule**: ALWAYS reject paths containing `..` before any file operations

**Pattern**:
```
IF file_path contains ".." THEN
  RETURN Error("Invalid path: directory traversal not allowed")
END IF
```

**Applies to**: All user-provided paths (plan files, output directories, resume paths)

---

## File Existence Validation

### Before Reading Files

**Pattern**:
```
1. Attempt Read tool on file_path
2. IF Read returns "file not found" or error THEN
     RETURN Error("File not found: [file_path]")
   END IF
3. Proceed with file content processing
```

**Error Message Format**: `"File not found: [absolute_path]"`

### Before Writing Files

**Pattern**:
```
1. Extract parent directory from file_path
2. IF parent directory doesn't exist THEN
     RETURN Error("Directory does not exist: [parent_path]")
   END IF
3. Proceed with Write tool
```

**Error Message Format**: `"Directory does not exist: [absolute_path]"`

---

## Markdown Frontmatter Validation

### Required Fields Check

**Pattern**:
```
1. Extract frontmatter from markdown (between --- markers)
2. Parse as YAML
3. FOR EACH required_field IN [list of required fields]:
     IF required_field NOT IN frontmatter THEN
       RETURN Error("Missing required frontmatter field: [field_name]")
     END IF
   END FOR
4. Proceed with content processing
```

**Error Message Format**: `"Missing required frontmatter field: [field_name] in [file_path]"`

### Field Type Validation

**Pattern**:
```
1. FOR EACH field IN frontmatter:
     expected_type = schema[field.name].type
     IF typeof(field.value) != expected_type THEN
       RETURN Error("Invalid type for [field_name]: expected [expected_type], got [actual_type]")
     END IF
   END FOR
```

**Error Message Format**: `"Invalid type for [field_name]: expected [expected_type], got [actual_type] in [file_path]"`

---

## Reference Example

### Commands/Agents Should Reference This Pattern

**Instead of duplicating ~20 lines of validation logic, reference this pattern:**

```markdown
**File Validation**: Follow file-validation-pattern.md for:
- Security: Reject `..` in all user-provided paths
- Existence: Verify file exists before Read operations
- Frontmatter: Validate required fields per story-bible-schema.md
```

**Then implement the specific validation inline:**

```
// Security check
IF plan_path contains ".." THEN
  Report error and exit  // Per file-validation-pattern.md
END IF

// Existence check
Attempt Read on plan_path
IF Read fails THEN
  Report "File not found: [plan_path]" and exit
END IF
```

---

## Schema Integration

For frontmatter field requirements, consult [story-bible-schema.md](../docs/story-bible-schema.md):

- **PLAN.md**: Required fields: title, world, format, created, total_chapters, version
- **Character files**: Required fields: name, role, created
- **Chapter files**: Required fields: chapter_number, title, word_count, status

---

## Implementation Notes

- **Keep validation inline minimal**: Just the check + error return
- **Reference this pattern** for the structure, don't copy entire logic
- **Use exact error message formats** for consistency across all agents/commands
