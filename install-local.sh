python3 -m venv .venv
./.venv/bin/pip install -e .

echo '#!/bin/bash' > horizon
echo 'exec ./.venv/bin/python -m horizon "$@"' >> horizon
chmod +x horizon

