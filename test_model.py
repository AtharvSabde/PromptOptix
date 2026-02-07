# Quick test to verify OptimizeRequest model
import sys
sys.path.insert(0, '.')

from backend.models.request_models import OptimizeRequest

# Check fields
print("OptimizeRequest fields:")
for field_name in OptimizeRequest.__fields__.keys():
    print(f"  - {field_name}")

# Check if task_type exists
if hasattr(OptimizeRequest.__fields__, 'task_type') or 'task_type' in OptimizeRequest.__fields__:
    print("\n✓ task_type field EXISTS")
else:
    print("\n✗ task_type field MISSING")

if hasattr(OptimizeRequest.__fields__, 'domain') or 'domain' in OptimizeRequest.__fields__:
    print("✓ domain field EXISTS")
else:
    print("✗ domain field MISSING")

# Try creating an instance
try:
    req = OptimizeRequest(
        prompt="Test prompt for optimization",
        analysis={"defects": [], "overall_score": 5.0}
    )
    print(f"\nCreated instance:")
    print(f"  task_type = {req.task_type}")
    print(f"  domain = {req.domain}")
except Exception as e:
    print(f"\nError creating instance: {e}")
