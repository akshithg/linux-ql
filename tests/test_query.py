"""Tests for query module: suite resolution, analysis, and CSV export."""

from unittest.mock import patch

import click
import pytest

from linux_ql.query import export_csv, queries_dir, run_analysis


class TestQueriesDir:
    def test_finds_real_queries_directory(self):
        qdir = queries_dir()
        assert qdir.is_dir()
        assert qdir.name == "queries"
        assert (qdir / "codeql-pack.yml").exists()


class TestRunAnalysis:
    @patch("linux_ql.query.subprocess.run")
    def test_raises_for_nonexistent_suite(self, mock_run, tmp_path, monkeypatch):
        # Point queries_dir to a tmp directory with no suite files
        fake_qdir = tmp_path / "queries"
        fake_qdir.mkdir()
        (fake_qdir / "suites").mkdir()
        monkeypatch.setattr("linux_ql.query.queries_dir", lambda: fake_qdir)

        with pytest.raises(click.ClickException, match="Unknown suite: bogus"):
            run_analysis(tmp_path / "db", "bogus", tmp_path / "out", 4)

        # subprocess.run should never be called for a bad suite
        mock_run.assert_not_called()

    @patch("linux_ql.query.subprocess.run")
    def test_runs_pack_install_then_analyze(self, mock_run, tmp_path, monkeypatch):
        fake_qdir = tmp_path / "queries"
        fake_qdir.mkdir()
        suites = fake_qdir / "suites"
        suites.mkdir()
        (suites / "all.qls").touch()
        monkeypatch.setattr("linux_ql.query.queries_dir", lambda: fake_qdir)

        sarif = run_analysis(tmp_path / "mydb.db", "all", tmp_path / "out", 8)

        calls = mock_run.call_args_list
        # First: pack install
        assert calls[0].args[0] == ["codeql", "pack", "install", str(fake_qdir)]
        # Second: database analyze
        analyze_args = calls[1].args[0]
        assert analyze_args[0:3] == ["codeql", "database", "analyze"]
        assert "--threads=8" in analyze_args
        assert str(suites / "all.qls") in analyze_args
        assert sarif == tmp_path / "out" / "mydb-all.sarif"


class TestExportCsv:
    def test_returns_empty_when_bqrs_dir_missing(self, tmp_path):
        db = tmp_path / "test.db"
        db.mkdir()
        result = export_csv(db, tmp_path / "csvout")
        assert result == []

    @patch("linux_ql.query.subprocess.run")
    def test_decodes_each_bqrs_file(self, mock_run, tmp_path):
        db = tmp_path / "test.db"
        bqrs_dir = db / "results" / "linux-ql" / "kernel-queries"
        bqrs_dir.mkdir(parents=True)
        (bqrs_dir / "query_a.bqrs").touch()
        (bqrs_dir / "query_b.bqrs").touch()

        csv_dir = tmp_path / "csvout"
        result = export_csv(db, csv_dir)

        assert len(result) == 2
        assert mock_run.call_count == 2
        # Verify decode commands
        for c in mock_run.call_args_list:
            args = c.args[0]
            assert args[0:3] == ["codeql", "bqrs", "decode"]
            assert "--format=csv" in args
