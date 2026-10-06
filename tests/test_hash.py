from pathlib import Path
from backend.app.utils.hash_utils import sha256_file

def test_hash(tmp_path):
    p = tmp_path / "x.txt"
    p.write_text("hello")
    assert len(sha256_file(str(p))) == 64
