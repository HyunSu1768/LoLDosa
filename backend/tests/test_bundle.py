import duckdb

from loldosa.bundle import LOCAL_MARK, export, install


def make_stats(d):
    d.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(d / "stats.duckdb"))
    con.execute("CREATE TABLE match_totals AS SELECT * FROM (VALUES ('16.21','apex',10),('ALL','apex',10),('ALL','all',10)) t(scope,bucket,matches)")
    con.close()


def test_export_install_roundtrip(tmp_path):
    src, b, user = tmp_path / "src", tmp_path / "bundle", tmp_path / "user"
    make_stats(src)
    m = export(src, b)
    assert m["games"] == {"apex": 10} and m["patches"] == ["16.21"]
    assert install(user, bdir=b) is not None
    assert (user / "stats.duckdb").exists() and (user / LOCAL_MARK).exists()
    assert install(user, bdir=b) is None  # 이미 최신


def test_does_not_overwrite_user_built_stats(tmp_path):
    src, b, user = tmp_path / "src", tmp_path / "bundle", tmp_path / "user"
    make_stats(src)
    export(src, b)
    make_stats(user)  # 사용자가 직접 만든 통계 (표시 파일 없음)
    assert install(user, bdir=b) is None


def test_save_api_key_keeps_other_lines(tmp_path, monkeypatch):
    from loldosa.config import save_api_key

    monkeypatch.setenv("RIOT_API_KEY", "")  # 테스트가 끝나면 원래 값으로 돌아오게

    env = tmp_path / ".env"
    env.write_text("RIOT_PLATFORM=kr\nRIOT_API_KEY=old\n", encoding="utf-8")
    save_api_key("RGAPI-new", env)
    assert env.read_text(encoding="utf-8") == "RIOT_PLATFORM=kr\nRIOT_API_KEY=RGAPI-new\n"
