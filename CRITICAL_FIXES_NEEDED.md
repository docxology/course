# Critical Fixes Required

## High Priority Fixes

### 1. Missing `timezone` Import in Core Files

**Files to Fix:**
- `src/curriculum/core/base.py`
- `src/curriculum/core/assessment.py`
- `src/curriculum/core/user.py`
- `src/curriculum/content_generation/quality.py`
- `src/curriculum/content_generation/workflow.py`

**Fix Pattern:**
```python
# Change from:
from datetime import datetime

# To:
from datetime import datetime, timezone
```

**Or use:**
```python
from datetime import datetime
from datetime import timezone
```

### 2. Duplicate Import in user.py

**File:** `src/curriculum/core/user.py`

**Issue:** Lines 5 and 9 both import `Optional` from typing

**Fix:** Remove one of the duplicate imports:
```python
# Remove line 9:
from typing import Optional  # DELETE THIS LINE
```

### 3. Type Hint Issues

**Files:**
- `src/curriculum/tools/file_handling.py:100` - Add return type annotation
- `src/curriculum/tools/formatters.py:71` - Fix type assignment (float to int)
- `src/curriculum/content_generation/workflow.py:45-46` - Fix dictionary key types

## Verification Steps

After fixes, run:
```bash
# Check for syntax errors
python3 -m py_compile src/curriculum/**/*.py

# Check type hints
mypy src/curriculum/

# Check formatting
black --check src/

# Check imports
isort --check src/
```

## Files Requiring timezone Import

Based on mypy output, these files need `timezone` import:
1. src/curriculum/core/base.py
2. src/curriculum/core/assessment.py
3. src/curriculum/core/user.py
4. src/curriculum/content_generation/quality.py
5. src/curriculum/content_generation/workflow.py

Total: ~15 occurrences across multiple files

